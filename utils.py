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
            print(f"HTTP error sending message: {e}. Status: {e.response.status_code}. Response: {e.response.text}")
        except httpx.RequestError as e:
            print(f"Request error sending message: {e}")

async def answer_callback_query(bot_token: Optional[str], callback_query_id: str, text: Optional[str] = None):
    """پاسخ به یک callback_query."""
    bot_token = bot_token or os.environ.get("BOT_TOKEN")
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
        date_str = date_str.strip()
        parts = date_str.split('/')
        
        if len(parts) == 3:
            year = int(parts[0])
            month = int(parts[1])
            day = int(parts[2])
            
            # اعتبارسنجی اولیه محدوده
            if 1300 <= year <= 1500 and 1 <= month <= 12 and 1 <= day <= 31:
                # ایجاد شیء JalaliDateTime (12:00 ظهر به عنوان پیش‌فرض)
                jdate = JalaliDateTime(year, month, day, 12, 0, 0)
                
                # اعتبارسنجی نهایی
                if jdate.to_gregorian():
                    return jdate
        return None
    except Exception:
        return None

async def get_coordinates_from_city(city_name: str) -> Tuple[Optional[float], Optional[float], Any]:
    """جستجو برای مختصات جغرافیایی و منطقه زمانی شهر."""
    try:
        geolocator = Nominatim(user_agent="astro_telegram_bot")
        
        loop = asyncio.get_event_loop()
        location = await loop.run_in_executor(
            None, 
            lambda: geolocator.geocode(city_name, addressdetails=True, timeout=10)
        )
        
        if location:
            lat, lon = location.latitude, location.longitude
            
            # استفاده از timezonefinder برای Timezone دقیق
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
    💡 [اصلاح نهایی]: این تابع تضمین می‌کند که کاراکترهای رزرو شده فقط یکبار Escape شوند.
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
        text = text.replace(char, f'\\{char}')
        
    return text
    
def escape_code_block(text: str) -> str:
    """فقط کاراکترهای بک‌تیک و بک‌اسلش را برای استفاده در داخل کد بلاک Escape می‌کند."""
    text = str(text) 
    text = text.replace('\\', '\\\\') 
    text = text.replace('`', '\\`')
    return text
