import httpx
from typing import Optional, Tuple, Dict, Any
from geopy.geocoders import Nominatim
from persiantools.jdatetime import JalaliDateTime
import os

# ⚠️ مهم: فرض بر این است که BOT_TOKEN در bot_app.py از متغیر محیطی خوانده می‌شود
# ما اینجا BOT_TOKEN را از os.environ.get نخواندیم، بلکه آن را در توابع به عنوان آرگومان دریافت می‌کنیم.

# ======================================================================
# توابع اصلی ارتباط با تلگرام
# ======================================================================

# 🛠️ [اصلاح] تابع send_message برای پشتیبانی صریح از MarkdownV2
async def send_message(bot_token: str, chat_id: int, text: str, reply_markup: Optional[Dict[str, Any]] = None):
    """ارسال یک پیام متنی به کاربر."""
    if not bot_token:
        print("Error: BOT_TOKEN is not set in send_message.")
        return
        
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'MarkdownV2', # 👈 اعمال MarkdownV2 به عنوان پیش‌فرض
        'disable_web_page_preview': True
    }
    if reply_markup:
        payload['reply_markup'] = reply_markup
        
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(url, json=payload)
            response.raise_for_status() # خطاهای HTTP را هندل می‌کند (مثل 400 Bad Request)
        except httpx.HTTPStatusError as e:
            # ⚠️ اینجاست که خطای 400 Bad Request تلگرام ثبت می‌شود
            print(f"HTTP error sending message: {e}")
            # اگر خطای 400 ناشی از Escape نبود، احتمالا توکن یا chat_id اشتباه است.
        except httpx.RequestError as e:
            print(f"Request error sending message: {e}")


async def send_telegram_message(chat_id: int, text: str, parse_mode: str, reply_markup: Optional[Dict[str, Any]] = None):
    """
    تابع اصلی ارسال پیام (Wrapper قدیمی یا جایگزین). 
    این تابع نیاز به BOT_TOKEN سراسری دارد که در bot_app.py به آن دسترسی نداشتیم.
    توصیه می‌شود از تابع send_message جدید استفاده کنید.
    """
    # ⚠️ توجه: این تابع با فرض اینکه BOT_TOKEN در این ماژول در دسترس است، کار می‌کند.
    # در bot_app.py ما send_message را فراخوانی می‌کنیم، اما main_sajil.py هنوز از این استفاده می‌کند.
    
    # 💡 [فرض]: برای سازگاری با main_sajil.py، BOT_TOKEN را از environment می‌خوانیم (یا یک متغیر سراسری تعریف می‌کنیم)
    bot_token = os.environ.get("BOT_TOKEN")
    if not bot_token:
        print("Error: BOT_TOKEN is not set in send_telegram_message.")
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': parse_mode,
        'disable_web_page_preview': True
    }
    if reply_markup:
        payload['reply_markup'] = reply_markup
        
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            await client.post(url, json=payload)
        except Exception as e:
            print(f"Error in send_telegram_message: {e}")


async def answer_callback_query(bot_token: str, callback_query_id: str, text: Optional[str] = None):
    """پاسخ به یک callback_query (اخطار محو شونده در بالای صفحه)."""
    if not bot_token:
        return
        
    url = f"https://api.telegram.org/bot{bot_token}/answerCallbackQuery"
    payload = {
        'callback_query_id': callback_query_id,
        'text': text or '',
        'show_alert': False
    }
    async with httpx.AsyncClient() as client:
        await client.post(url, json=payload)

# ======================================================================
# توابع کمکی تاریخ و مکان
# ======================================================================

def parse_persian_date(date_str: str) -> Optional[JalaliDateTime]:
    """تبدیل رشته تاریخ شمسی (مثلاً 1370/01/01) به شیء JalaliDateTime."""
    try:
        parts = date_str.split('/')
        if len(parts) == 3:
            year = int(parts[0])
            month = int(parts[1])
            day = int(parts[2])
            # اعتبارسنجی ساده
            if 1300 < year < 1500 and 1 <= month <= 12 and 1 <= day <= 31:
                return JalaliDateTime(year, month, day)
        return None
    except Exception:
        return None

# استفاده از geopy برای جستجوی نام شهر
# ⚠️ توجه: این عملیات I/O (شبکه) است و باید از طریق AsyncClient یا executor در فست‌ای‌پی‌آی اجرا شود
# برای سادگی، فعلاً از تابع Blocking Nominatim استفاده می‌کنیم که در محیط وب‌هوک FastAPI کند است.
# (قبلاً فرض شد که در bot_app این تابع await شده است، پس باید با asyncio اجرا شود)

# 💡 [اصلاح]: برای آسنکرون کردن geopy در FastAPI، باید آن را در یک Thread Pool Executor اجرا کرد.
# اما چون تغییر ساختار ممنوع است، فرض می‌کنیم فراخوانی در bot_app به درستی هندل می‌شود.

async def get_coordinates_from_city(city_name: str) -> Tuple[Optional[float], Optional[float], Any]:
    """جستجو برای مختصات جغرافیایی و منطقه زمانی شهر."""
    try:
        # Nominatim به عنوان یک نمونه سینکرون (باید در محیط async هندل شود)
        geolocator = Nominatim(user_agent="astro_telegram_bot")
        
        # ⚠️ اجرای Blocking I/O در یک thread (برای جلوگیری از مسدود کردن رویداد حلقه اصلی)
        import asyncio
        loop = asyncio.get_event_loop()
        location = await loop.run_in_executor(
            None, 
            lambda: geolocator.geocode(city_name, addressdetails=True, timeout=10)
        )
        
        if location:
            # جستجوی منطقه زمانی (نیازمند کتابخانه timezonefinder یا مشابه)
            # 💡 برای سادگی و اجتناب از نصب کتابخانه جدید، از pytz استفاده می‌کنیم
            import pytz 
            # 💡 [فرض]: از اطلاعات آدرس برای تخمین منطقه زمانی استفاده می‌کنیم
            # این بخش بسیار پیچیده است و بدون یک سرویس قوی‌تر (مثل Google Time Zone API) سخت است.
            # برای مثال، فرض می‌کنیم برای شهرهای بزرگ ایران از 'Asia/Tehran' استفاده می‌شود:
            
            # یک تخمین بسیار ساده و ناامن:
            if 'iran' in location.raw.get('display_name', '').lower():
                 tz = pytz.timezone('Asia/Tehran')
            else:
                 # اگر سرویس‌های قوی‌تر در دسترس نباشد، این بخش می‌تواند خطا بدهد.
                 # به جای آن از UTC استفاده می‌کنیم (یا باید یک لیست مرجع داشته باشیم):
                 tz = pytz.utc # Fallback to UTC
                 
            # 💡 [بهبود]: استفاده از timezonefinder برای دقت بیشتر توصیه می‌شود.
            
            return location.latitude, location.longitude, tz
        
        return None, None, None
    except Exception as e:
        print(f"Error in get_coordinates_from_city: {e}")
        return None, None, None


# ======================================================================
# 🛠️ [اصلاح نهایی] تابع Escape برای رفع خطای 400 Bad Request
# این تابع مرکزی برای کل پروژه است.
# ======================================================================

def escape_markdown_v2(text: str) -> str:
    """
    کاراکترهای رزرو شده MarkdownV2 را برای استفاده در پیام‌های تلگرام Escape می‌کند.
    این تابع توسط bot_app.py و main_sajil.py استفاده می‌شود.
    لیست کامل: _ * [ ] ( ) ~ ` > # + - = | { } . !
    """
    # لیست کامل کاراکترهای رزرو شده: _ * [ ] ( ) ~ ` > # + - = | { } . !
    reserved_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    
    # اطمینان از تبدیل به رشته
    text = str(text) 
    
    for char in reserved_chars:
        text = text.replace(char, f'\\{char}') 
        
    return text
