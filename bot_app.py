import httpx
from typing import Optional, Tuple, Dict, Any
from geopy.geocoders import Nominatim
from persiantools.jdatetime import JalaliDateTime
import os
import asyncio
import pytz 

# ======================================================================
# توابع اصلی ارتباط با تلگرام (بدون تغییر)
# ======================================================================

async def send_message(bot_token: str, chat_id: int, text: str, reply_markup: Optional[Dict[str, Any]] = None):
    """ارسال یک پیام متنی به کاربر."""
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
            print(f"HTTP error sending message: {e}")
        except httpx.RequestError as e:
            print(f"Request error sending message: {e}")


async def send_telegram_message(chat_id: int, text: str, parse_mode: str, reply_markup: Optional[Dict[str, Any]] = None):
    """تابع اصلی ارسال پیام (Wrapper قدیمی یا جایگزین) که در main_sajil.py استفاده می‌شود."""
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
    """پاسخ به یک callback_query."""
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
# توابع کمکی تاریخ و مکان (بدون تغییر)
# ======================================================================

def parse_persian_date(date_str: str) -> Optional[JalaliDateTime]:
    """تبدیل رشته تاریخ شمسی (مثلاً 1370/01/01) به شیء JalaliDateTime."""
    try:
        parts = date_str.split('/')
        if len(parts) == 3:
            year = int(parts[0])
            month = int(parts[1])
            day = int(parts[2])
            if 1300 < year < 1500 and 1 <= month <= 12 and 1 <= day <= 31:
                return JalaliDateTime(year, month, day)
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
            if 'iran' in location.raw.get('display_name', '').lower():
                 tz = pytz.timezone('Asia/Tehran')
            else:
                 tz = pytz.utc
                 
            return location.latitude, location.longitude, tz
        
        return None, None, None
    except Exception as e:
        print(f"Error in get_coordinates_from_city: {e}")
        return None, None, None


# ======================================================================
# 🛠️ توابع Escape (رفع خطای 400 Bad Request)
# ======================================================================

def escape_markdown_v2(text: str) -> str:
    """
    کاراکترهای رزرو شده MarkdownV2 را برای استفاده در متن عادی Escape می‌کند.
    لیست کامل: _ * [ ] ( ) ~ ` > # + - = | { } . !
    """
    text = str(text) 
    # لیست کامل کاراکترهای رزرو شده
    reserved_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    
    for char in reserved_chars:
        text = text.replace(char, f'\\{char}') 
        
    return text

def escape_code_block(text: str) -> str:
    """
    فقط کاراکترهای بک‌تیک و بک‌اسلش را برای استفاده در داخل کد بلاک Escape می‌کند.
    """
    text = str(text) 
    # ترتیب جایگزینی مهم است: ابتدا بک‌اسلش، سپس بک‌تیک.
    text = text.replace('\\', '\\\\') 
    text = text.replace('`', '\\`')
    return text
