# ----------------------------------------------------------------------
# utils.py - ماژول نهایی توابع کمکی (نسخه قطعی، امن و پاک‌سازی‌شده)
# ----------------------------------------------------------------------

import httpx
from typing import Optional, Dict, Any, Union
from persiantools.jdatetime import JalaliDateTime
import os
import datetime
import logging 
import pytz 
# ❌ ایمپورت‌های مربوط به geopy و timezonefinder کاملاً حذف شدند

# --- تنظیمات ضروری ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ======================================================================
# 💥💥💥 پایگاه داده محلی شهرهای پرتکرار ایران (Cache) 💥💥💥
# ======================================================================

LOCAL_CITY_DB: Dict[str, Dict[str, Union[float, str]]] = {
    "تهران": {"latitude": 35.6892, "longitude": 51.3890, "timezone": "Asia/Tehran"},
    "مشهد": {"latitude": 36.2605, "longitude": 59.6168, "timezone": "Asia/Tehran"},
    "اصفهان": {"latitude": 32.6546, "longitude": 51.6679, "timezone": "Asia/Tehran"},
    "تبریز": {"latitude": 38.0806, "longitude": 46.2919, "timezone": "Asia/Tehran"},
    "شیراز": {"latitude": 29.6037, "longitude": 52.5332, "timezone": "Asia/Tehran"},
    "اهواز": {"latitude": 31.3168, "longitude": 48.6749, "timezone": "Asia/Tehran"},
    "کرج": {"latitude": 35.8423, "longitude": 50.9770, "timezone": "Asia/Tehran"},
    "قم": {"latitude": 34.6418, "longitude": 50.8752, "timezone": "Asia/Tehran"},
    "اراک": {"latitude": 34.0863, "longitude": 49.6894, "timezone": "Asia/Tehran"},
    "کرمان": {"latitude": 30.2832, "longitude": 57.0620, "timezone": "Asia/Tehran"},
    "رشت": {"latitude": 37.2801, "longitude": 49.5888, "timezone": "Asia/Tehran"},
    "زنجان": {"latitude": 36.6746, "longitude": 48.4900, "timezone": "Asia/Tehran"},
    "همدان": {"latitude": 34.8066, "longitude": 48.5160, "timezone": "Asia/Tehran"},
    "یزد": {"latitude": 31.8973, "longitude": 54.3686, "timezone": "Asia/Tehran"},
    "ساری": {"latitude": 36.5658, "longitude": 53.0560, "timezone": "Asia/Tehran"},
    # ... شهرهای دیگر را اینجا اضافه کنید
}

def get_city_lookup_data(city_name: str) -> Optional[Dict[str, Union[float, str]]]:
    """
    مختصات جغرافیایی و منطقه زمانی شهر را با اولویت جستجوی محلی برمی‌گرداند.
    """
    normalized_city_name = city_name.strip()
    
    # 1. جستجوی محلی 
    if normalized_city_name in LOCAL_CITY_DB:
        logging.info(f"✅ شهر {city_name} از دیتابیس محلی یافت شد.")
        result = LOCAL_CITY_DB[normalized_city_name].copy()
        result['city_name'] = normalized_city_name
        return result

    # 2. جستجوی خارجی: حذف شده
    logging.warning(f"❌ شهر {city_name} در دیتابیس محلی یافت نشد. جستجوی خارجی فعال نیست.")
    return None 
    

# ======================================================================
# توابع اصلی ارتباط با تلگرام و اعتبارسنجی (بدون تغییر)
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

def escape_markdown_v2(text: str) -> str:
    """فراردهی کاراکترهای رزرو شده برای MarkdownV2 تلگرام."""
    reserved_chars = [
        '\\', 
        '_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', 
        '-', '=', '|', '{', '}', '.', '!', ':' 
    ]
    
    for char in reserved_chars:
        text = text.replace(char, f'\\{char}') 
        
    return text
