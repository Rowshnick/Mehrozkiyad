import httpx
from typing import Optional, Tuple, Dict, Any
from geopy.geocoders import Nominatim
from persiantools.jdatetime import JalaliDateTime
import os
import asyncio
import pytz 
from timezonefinder import TimezoneFinder 
import datetime

# --- تنظیمات ضروری ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
tf = TimezoneFinder() # آبجکت سراسری TimezoneFinder
geolocator = Nominatim(user_agent="TelegramAstroBot") # 💡 [جدید]: آبجکت سراسری Nominatim

# ======================================================================
# توابع اصلی ارتباط با تلگرام
# ======================================================================

async def send_message(bot_token: Optional[str], chat_id: int, text: str, reply_markup: Optional[Dict[str, Any]] = None):
    """ارسال یک پیام متنی به کاربر."""
    bot_token = bot_token or os.environ.get("BOT_TOKEN")
    if not bot_token:
        print("Error: BOT_TOKEN is not set in send_message.")
        return
        
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'MarkdownV2', 
        'disable_web_page_preview': True
    }
    if reply_markup:
        payload['reply_markup'] = reply_markup
        
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(url, json=payload)
            response.raise_for_status() 
        except httpx.HTTPStatusError as e:
            # نمایش خطای API تلگرام (مثلاً پیام خیلی بلند است)
            print(f"Telegram API error: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            # نمایش خطای شبکه/ارتباط
            print(f"Network error during Telegram API call: {e}")

async def answer_callback_query(bot_token: Optional[str], callback_query_id: str, text: str = "✅"):
    """پاسخ به یک Callback Query."""
    bot_token = bot_token or os.environ.get("BOT_TOKEN")
    if not bot_token:
        print("Error: BOT_TOKEN is not set in answer_callback_query.")
        return
        
    url = f"https://api.telegram.org/bot{bot_token}/answerCallbackQuery"
    payload = {
        'callback_query_id': callback_query_id,
        'text': text,
        'show_alert': False
    }
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.post(url, json=payload)
            response.raise_for_status()
        except Exception as e:
            print(f"Error answering callback query: {e}")


# ======================================================================
# توابع Utility
# ======================================================================

def parse_persian_date(date_str: str) -> Optional[JalaliDateTime]:
    """تلاش برای تبدیل رشته تاریخ شمسی به شیء JalaliDateTime."""
    try:
        # فرض استاندارد: 1370/01/01
        return JalaliDateTime.strptime(date_str.strip(), '%Y/%m/%d')
    except ValueError:
        return None

async def get_coordinates_from_city(city_name: str) -> Tuple[Optional[float], Optional[float], Optional[pytz.BaseTzInfo]]:
    """دریافت مختصات و منطقه زمانی از نام شهر با استفاده از geopy و timezonefinder."""
    try:
        # استفاده از geopy برای یافتن مختصات
        location = await asyncio.to_thread(geolocator.geocode, city_name, language='fa')
        
        if location:
            lat = location.latitude
            lon = location.longitude
            
            # استفاده از timezonefinder برای یافتن منطقه زمانی
            tz_name = tf.timezone_at(lat=lat, lng=lon)
            
            if tz_name:
                tz = pytz.timezone(tz_name)
            else:
                tz = pytz.utc 
                print(f"Warning: Could not find specific timezone for {city_name}. Using UTC.")
                
            return lat, lon, tz
        
        return None, None, None
    except Exception as e:
        print(f"Error in get_coordinates_from_city: {e}")
        return None, None, None


# ======================================================================
# توابع Escape (رفع مشکل \ در پیام‌ها)
# ======================================================================

def escape_markdown_v2(text: str) -> str:
    """
    کاراکترهای رزرو شده MarkdownV2 را Escape می‌کند.
    💡 [اصلاح نهایی]: این تابع تضمین می‌کند که کاراکرهای رزرو شده فقط یکبار Escape شوند.
    """
    text = str(text)
    
    # لیست کامل کاراکترهای رزرو شده در MarkdownV2
    reserved_chars = [
        '\\', # باید اول Escape شود
        '_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', 
        '-', '=', '|', '{', '}', '.', '!'
    ]
    
    # اعمال Escape
    for char in reserved_chars:
        # برای بک‌اسلش، باید اطمینان حاصل کنیم که بک‌اسلش‌های موجود (که قبلاً برای Escape اضافه شده‌اند) مجدداً Escape نشوند.
        # اما برای سادگی و اجتناب از تکرار Escape، همان روش ساده جایگزینی را حفظ می‌کنیم.
        # در Python، یک '\\' در رشته، یک کاراکتر بک‌اسلش واقعی است.
        if char == '\\':
             # اگر بک‌اسلش بود، باید آن را با دو بک‌اسلش جایگزین کنیم تا Escape شود: \\ -> \\\\
             text = text.replace(char, r'\\')
        else:
            text = text.replace(char, f'\\{char}')
        
    return text
    
def escape_code_block(text: str) -> str:
    """فقط کاراکترهای بک‌تیک و بک‌اسلش را برای استفاده در بلوک کد (``) Escape می‌کند."""
    text = str(text)
    # Escape بک‌اسلش
    text = text.replace('\\', r'\\')
    # Escape بک‌تیک
    text = text.replace('`', r'\`')
    return text
