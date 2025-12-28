# utils.py
# =============================================================================
# توابع کمکی ربات (ارسال پیام، ارسال عکس، فراردهی MarkdownV2، تبدیل تاریخ و ...)
# -----------------------------------------------------------------------------
# این نسخه:
#   - کاملاً فارسی است
#   - با MarkdownV2 سازگار است
#   - از خطای 400 تلگرام جلوگیری می‌کند
#   - escape_code_block اضافه شده
#   - برای Railway و httpx بهینه شده
# =============================================================================

import os
import re
import logging
from typing import Dict, Any, Optional
import httpx
import io
import datetime
from persiantools.jdatetime import JalaliDate, JalaliDateTime

logging.basicConfig(level=logging.INFO)

# -----------------------------------------------------------------------------
# توکن ربات
# -----------------------------------------------------------------------------
BOT_TOKEN = os.environ.get("BOT_TOKEN")


# =============================================================================
# ۱) توابع فراردهی MarkdownV2
# =============================================================================

def escape_markdown_v2(text: str) -> str:
    """
    فراردهی کامل کاراکترهای خاص MarkdownV2.
    این تابع از خطای 400 تلگرام جلوگیری می‌کند.
    """
    if text is None:
        return ""

    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return "".join("\\" + c if c in escape_chars else c for c in str(text))


def escape_code_block(text: str) -> str:
    """
    فراردهی مخصوص کد یا ورودی کاربر.
    این تابع فقط بک‌تیک‌ها و بک‌اسلش‌ها را امن می‌کند.
    """
    if text is None:
        return ""

    text = text.replace("\\", "\\\\")
    text = text.replace("`", "\\`")
    return text


# =============================================================================
# ۲) ارسال پیام متنی
# =============================================================================

async def send_message(
    bot_token: str,
    chat_id: int,
    text: str,
    reply_markup: Optional[Dict[str, Any]] = None
):
    """
    ارسال پیام متنی به کاربر.
    - اگر reply_markup خالی باشد، ارسال نمی‌شود (برای جلوگیری از خطای 400)
    - متن به‌صورت MarkdownV2 ارسال می‌شود.
    """

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "MarkdownV2"
    }

    if reply_markup is not None:
        payload["reply_markup"] = reply_markup

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            logging.info(f"📨 پیام ارسال شد → {response.status_code}")
    except httpx.HTTPStatusError as e:
        logging.error(f"❌ خطای HTTP در sendMessage: {e.response.status_code} → {e.response.text}")
    except Exception as e:
        logging.error(f"❌ خطای ناشناخته در sendMessage: {e}")


# =============================================================================
# ۳) پاسخ به CallbackQuery
# =============================================================================

async def answer_callback_query(
    bot_token: str,
    callback_id: str,
    text: Optional[str] = None,
    show_alert: bool = False
):
    """
    پاسخ به کلیک دکمه‌های اینلاین.
    """
    url = f"https://api.telegram.org/bot{bot_token}/answerCallbackQuery"

    payload = {
        "callback_query_id": callback_id,
        "text": text,
        "show_alert": show_alert
    }

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(url, json=payload)
    except Exception as e:
        logging.error(f"❌ خطا در answerCallbackQuery: {e}")


# =============================================================================
# ۴) ارسال عکس + کپشن (بدون خطای 400)
# =============================================================================

async def send_photo_with_caption(
    bot_token: str,
    chat_id: int,
    photo: io.BytesIO,
    caption: str,
    reply_markup: Optional[Dict[str, Any]] = None
):
    """
    ارسال عکس به همراه کپشن MarkdownV2.
    - فایل به‌صورت باینری ارسال می‌شود
    - reply_markup در صورت وجود JSON می‌شود
    """

    url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"

    files = {
        "photo": ("chart.png", photo, "image/png")
    }

    data = {
        "chat_id": chat_id,
        "caption": caption,
        "parse_mode": "MarkdownV2"
    }

    if reply_markup is not None:
        import json
        data["reply_markup"] = json.dumps(reply_markup)

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, data=data, files=files)
            response.raise_for_status()
            logging.info(f"🖼 عکس ارسال شد → {response.status_code}")
            return response.json()

    except httpx.HTTPStatusError as e:
        logging.error(f"❌ خطای HTTP در sendPhoto: {e.response.status_code} → {e.response.text}")
        await send_message(
            bot_token, chat_id,
            escape_markdown_v2(f"❌ خطا در ارسال عکس:\n{e.response.status_code}")
        )
        return {"ok": False}

    except Exception as e:
        logging.error(f"❌ خطای ناشناخته در sendPhoto: {e}")
        return {"ok": False}


# =============================================================================
# ۵) توابع تبدیل تاریخ و زمان
# =============================================================================

def parse_persian_date(date_str: str) -> Optional[JalaliDate]:
    """
    تبدیل رشته تاریخ شمسی به JalaliDate.
    ورودی: YYYY/MM/DD
    """
    try:
        return JalaliDate.strptime(date_str, "%Y/%m/%d")
    except ValueError:
        return None


def parse_persian_time(time_str: str) -> Optional[str]:
    """
    اعتبارسنجی رشته ساعت (HH:MM)
    """
    try:
        datetime.datetime.strptime(time_str, "%H:%M")
        return time_str
    except ValueError:
        return None


# =============================================================================
# ۶) جستجوی شهر (نسخه ساده – قابل جایگزینی با دیتابیس واقعی)
# =============================================================================

def get_city_lookup_data(city_name: str) -> Optional[Dict[str, Any]]:
    """
    جستجوی اطلاعات شهر بر اساس نام فارسی.
    این نسخه ساده است و می‌توان آن را با دیتابیس واقعی جایگزین کرد.
    """

    city_name = city_name.strip()

    test_cities = {
        "تهران": {"latitude": 35.68, "longitude": 51.41, "timezone": "Asia/Tehran"},
        "مشهد": {"latitude": 36.31, "longitude": 59.58, "timezone": "Asia/Tehran"},
        "شیراز": {"latitude": 29.60, "longitude": 52.54, "timezone": "Asia/Tehran"},
        "اصفهان": {"latitude": 32.65, "longitude": 51.67, "timezone": "Asia/Tehran"},
        "تبریز": {"latitude": 38.08, "longitude": 46.29, "timezone": "Asia/Tehran"},
        "اراک": {"latitude": 34.09, "longitude": 49.69, "timezone": "Asia/Tehran"},
    }

    if city_name in test_cities:
        logging.info(f"🏙 شهر '{city_name}' یافت شد.")
        return test_cities[city_name]

    logging.warning(f"❌ شهر '{city_name}' یافت نشد.")
    return None
