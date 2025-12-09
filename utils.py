# ----------------------------------------------------------------------
# utils.py - ماژول نهایی توابع کمکی (با اصلاحیه قطعی مکان‌یابی)
# ----------------------------------------------------------------------

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
tf = TimezoneFinder() 
# آبجکت سراسری Nominatim: مطمئن شوید که این آبجکت فقط یک بار ساخته شده است
geolocator = Nominatim(user_agent="astro_bot_v1") 

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
            print(f"Telegram API Error (send_message): {e.response.status_code} - {e.response.text}")
        except Exception as e:
            print(f"An unexpected error occurred in send_message: {e}")

async def answer_callback_query(bot_token: Optional[str], callback_id: str, text: Optional[str] = None):
    """ارسال پاسخ به یک Callback Query (برای بستن دایره بارگذاری روی دکمه)."""
    bot_token = bot_token or os.environ.get("BOT_TOKEN")
    if not bot_token:
        print("Error: BOT_TOKEN is not set in answer_callback_query.")
        return

    url = f"https://api.telegram.org/bot{bot_token}/answerCallbackQuery"
    payload = {
        'callback_query_id': callback_id,
    }
    if text:
        payload['text'] = text
        payload['show_alert'] = False
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            await client.post(url, json=payload)
        except Exception as e:
            print(f"An unexpected error occurred in answer_callback_query: {e}")


# ======================================================================
# توابع اعتبارسنجی و تبدیل تاریخ/زمان
# ======================================================================

def parse_persian_date(date_str: str) -> Optional[JalaliDateTime]:
    """تلاش برای تبدیل رشته تاریخ شمسی (YYYY/MM/DD) به JalaliDateTime."""
    try:
        parts = date_str.split('/')
        if len(parts) == 3:
            year, month, day = map(int, parts)
            if 1 <= month <= 12 and 1 <= day <= 31:
                return JalaliDateTime(year, month, day)
        return None
    except Exception:
        return None

def parse_persian_time(time_str: str) -> Optional[str]:
    """تلاش برای تبدیل رشته زمان (ساعت:دقیقه) به فرمت HH:MM."""
    try:
        dt_time = datetime.datetime.strptime(time_str.strip(), '%H:%M').time()
        return dt_time.strftime('%H:%M')
    except ValueError:
        return None


# ======================================================================
# توابع مکان‌یابی (با جستجوی پشتیبان و استفاده از Lambda)
# ======================================================================

async def get_coordinates_from_city(city_name: str) -> Tuple[Optional[float], Optional[float], Optional[pytz.BaseTzInfo]]:
    """دریافت مختصات و منطقه زمانی از نام شهر با مکانیزم جستجوی پشتیبان."""
    try:
        loop = asyncio.get_event_loop()
        location = None
        
        # 1. تلاش اول: جستجو با زبان فارسی (استفاده از Lambda برای انتقال پارامتر keyword)
        # 💡 این روش، خطای run_in_executor() got an unexpected keyword argument 'language' را رفع می‌کند.
        location = await loop.run_in_executor(
            None, 
            lambda: geolocator.geocode(city_name, language='fa') 
        )
        
        # 2. تلاش دوم (Fallback): اگر با زبان فارسی پیدا نشد، بدون پارامتر زبان جستجو کن.
        if not location:
            location = await loop.run_in_executor(
                None, 
                lambda: geolocator.geocode(city_name)
            )

        if location:
            lat = location.latitude
            lon = location.longitude
            
            # پیدا کردن منطقه زمانی
            tz_name = tf.timezone_at(lat=lat, lng=lon)
            
            if tz_name:
                tz = pytz.timezone(tz_name)
            else:
                tz = pytz.utc 
                print(f"Warning: Could not find specific timezone for {city_name}. Using UTC.")
                
            return lat, lon, tz
        
        # اگر هیچ‌کدام از دو تلاش موفقیت‌آمیز نبود
        return None, None, None
    except Exception as e:
        print(f"Error in get_coordinates_from_city: {e}")
        return None, None, None


# ======================================================================
# توابع Escape (رفع مشکل \ در پیام‌ها)
# ======================================================================

def escape_markdown_v2(text: str) -> str:
    """کاراکترهای رزرو شده MarkdownV2 را Escape می‌کند."""
    text = str(text)
    
    reserved_chars = [
        '\\', 
        '_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', 
        '-', '=', '|', '{', '}', '.', '!'
    ]
    
    for char in reserved_chars:
        text = text.replace(char, f'\\{char}')
        
    return text
    
def escape_code_block(text: str) -> str:
    """فقط کاراکترهای بک‌تیک و بک‌اسلش را برای بلاک‌های کد Escape می‌کند."""
    text = str(text)
    text = text.replace('\\', '\\\\')
    text = text.replace('`', '\\`')
    return text

