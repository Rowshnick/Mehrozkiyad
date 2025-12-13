# utils.py - ماژول توابع کمکی (اصلاح شده برای رفع خطای 400 تلگرام)

import os
import re
import logging
from typing import Dict, Any, Optional
import httpx 
import io 
from persiantools.jdatetime import JalaliDate, JalaliDateTime 
import datetime

logging.basicConfig(level=logging.INFO)

# فرض می‌کنیم توکن ربات از متغیر محیطی گرفته می‌شود
BOT_TOKEN = os.environ.get("BOT_TOKEN") 

# --- توابع Telegram API Call ---

def escape_markdown_v2(text: str) -> str:
    """فراردهی کاراکترهای خاص برای MarkdownV2 تلگرام."""
    chars_to_escape = r'([_*\[\]()~`>#+\-=|{}.!])'
    return re.sub(chars_to_escape, r'\\\1', text)

async def send_message(bot_token: str, chat_id: int, text: str, reply_markup: Optional[Dict[str, Any]] = None):
    """
    ارسال پیام متنی به کاربر.
    اصلاح: کلید 'reply_markup' در صورت None بودن حذف می‌شود تا خطای 400 تلگرام رفع شود.
    """
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'MarkdownV2'
    }
    
    # 💥💥💥 اصلاح حیاتی برای رفع خطای Bad Request 💥💥💥
    if reply_markup is not None:
        payload['reply_markup'] = reply_markup
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            logging.info(f"HTTP Request: POST .../sendMessage \"HTTP/1.1 {response.status_code}\"")
    except httpx.HTTPStatusError as e:
        logging.error(f"HTTP Error: Status {e.response.status_code}, Response: {e.response.text}")
    except Exception as e:
        logging.error(f"Error sending message: {e}")

async def answer_callback_query(bot_token: str, callback_id: str, text: Optional[str] = None, show_alert: bool = False):
    """پاسخ به کلیک‌های اینلاین (برای جلوگیری از ماندن علامت لودینگ)."""
    url = f"https://api.telegram.org/bot{bot_token}/answerCallbackQuery"
    payload = {
        'callback_query_id': callback_id,
        'text': text,
        'show_alert': show_alert
    }
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(url, json=payload)
    except Exception as e:
        logging.error(f"Error answering callback query: {e}")


# 💥 تابع ارسال عکس با کپشن 💥
async def send_photo_with_caption(bot_token: str, chat_id: int, photo: io.BytesIO, caption: str, reply_markup: Optional[Dict[str, Any]] = None):
    """ارسال یک فایل باینری (عکس) به همراه کپشن به تلگرام."""
    url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
    
    files = {
        'photo': ('chart.png', photo, 'image/png') 
    }
    
    data = {
        'chat_id': chat_id,
        'caption': caption,
        'parse_mode': 'MarkdownV2', 
        # نکته: reply_markup باید برای متد sendPhoto هم به صورت شرطی استفاده شود، اما در این ساختار
        # چون از data و files استفاده می‌شود، معمولاً خطا کمتر رخ می‌دهد.
        # برای اطمینان بیشتر، آن را در دیکشنری data قرار می‌دهیم.
    }
    
    # اضافه کردن شرطی reply_markup
    if reply_markup is not None:
        # برای sendPhoto، reply_markup باید در بخش data (و نه files) به صورت JSON string ارسال شود
        import json
        data['reply_markup'] = json.dumps(reply_markup)


    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, data=data, files=files)
            response.raise_for_status()
            logging.info(f"HTTP Request: POST .../sendPhoto \"HTTP/1.1 {response.status_code}\"")
            return response.json()
    except httpx.HTTPStatusError as e:
        logging.error(f"HTTP ERROR in send_photo: Status {e.response.status_code}, Response: {e.response.text}")
        await send_message(bot_token, chat_id, escape_markdown_v2(f"❌ *خطای ارسال عکس*:\n `{e.response.status_code}`"), None)
        return {"ok": False, "error": f"HTTP Error: {e.response.status_code}"}
    except Exception as e:
        logging.error(f"Unknown ERROR in send_photo: {e}")
        return {"ok": False, "error": f"Unknown Error: {str(e)}"}


# --- توابع کمکی تبدیل و جستجو ---

def parse_persian_date(date_str: str) -> Optional[JalaliDate]:
    """تبدیل رشته تاریخ شمسی به شیء JalaliDate."""
    try:
        return JalaliDate.strptime(date_str, '%Y/%m/%d')
    except ValueError:
        return None

def parse_persian_time(time_str: str) -> Optional[str]:
    """اعتبار سنجی رشته ساعت (HH:MM)."""
    try:
        datetime.datetime.strptime(time_str, '%H:%M')
        return time_str
    except ValueError:
        return None

def get_city_lookup_data(city_name: str) -> Optional[Dict[str, Any]]:
    """
    تابع شبیه‌سازی جستجوی اطلاعات شهر بر اساس نام.
    (شما باید این تابع را با دیتابیس شهرهای خود جایگزین کنید.)
    """
    city_name = city_name.strip()
    
    test_cities = {
        "اراک": {"latitude": 34.09, "longitude": 49.69, "timezone": "Asia/Tehran"},
        "تهران": {"latitude": 35.68, "longitude": 51.41, "timezone": "Asia/Tehran"},
        "مشهد": {"latitude": 36.31, "longitude": 59.58, "timezone": "Asia/Tehran"},
        "شیراز": {"latitude": 29.60, "longitude": 52.54, "timezone": "Asia/Tehran"},
    }

    if city_name in test_cities:
        logging.info(f"✅ شهر {city_name} از دیتابیس محلی یافت شد.")
        return test_cities[city_name]
    
    logging.warning(f"❌ شهر {city_name} در دیتابیس محلی یافت نشد.")
    return None
