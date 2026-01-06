# utils.py
# =============================================================================
# توابع کمکی ربات (ارسال پیام، ارسال عکس، فراردهی MarkdownV2، تبدیل تاریخ و ...)
# نسخه اصلاح‌شده و پایدار برای Railway + لاگ‌های دقیق‌تر
# =============================================================================

import logging
from typing import Dict, Any, Optional
import httpx
import io
import datetime
from persiantools.jdatetime import JalaliDate
import json

logging.basicConfig(level=logging.INFO)

# =============================================================================
# ۱) توابع فراردهی MarkdownV2
# =============================================================================

def escape_markdown_v2(text: str) -> str:
    if text is None:
        return ""
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return "".join("\\" + c if c in escape_chars else c for c in str(text))


def escape_code_block(text: str) -> str:
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
    توجه: فرض می‌کنیم متن قبلاً با escape_markdown_v2 فرار داده شده.
    """

    if not bot_token:
        logging.error("❌ BOT_TOKEN خالی است! پیام ارسال نشد.")
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    payload: Dict[str, Any] = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "MarkdownV2",
    }

    if reply_markup is not None:
        # اینجا json خود httpx را می‌گذاریم آن را serialize کند
        payload["reply_markup"] = reply_markup

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=payload)
            if response.status_code != 200:
                logging.error(
                    f"❌ خطای HTTP در sendMessage: {response.status_code} → {response.text}"
                )
            else:
                logging.info(f"📨 پیام ارسال شد → {response.status_code}")

    except httpx.HTTPError as e:
        logging.error(f"❌ خطای شبکه/HTTP در sendMessage: {repr(e)}")

    except Exception as e:
        logging.error(f"❌ خطای ناشناخته در sendMessage: {repr(e)}")


# =============================================================================
# ۳) پاسخ به CallbackQuery
# =============================================================================

async def answer_callback_query(
    bot_token: str,
    callback_id: str,
    text: Optional[str] = None,
    show_alert: bool = False
):
    if not bot_token:
        logging.error("❌ BOT_TOKEN خالی است! Callback ارسال نشد.")
        return

    url = f"https://api.telegram.org/bot{bot_token}/answerCallbackQuery"

    payload: Dict[str, Any] = {
        "callback_query_id": callback_id,
        "show_alert": show_alert
    }

    # اگر متنی برای نمایش داری
    if text:
        payload["text"] = text

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(url, json=payload)
            if response.status_code != 200:
                logging.error(
                    f"❌ خطای HTTP در answerCallbackQuery: {response.status_code} → {response.text}"
                )
            else:
                logging.info(f"✅ answerCallbackQuery ارسال شد → {response.status_code}")

    except httpx.HTTPError as e:
        logging.error(f"❌ خطای شبکه/HTTP در answerCallbackQuery: {repr(e)}")

    except Exception as e:
        logging.error(f"❌ خطا در answerCallbackQuery: {repr(e)}")


# =============================================================================
# ۴) ارسال عکس + کپشن
# =============================================================================

async def send_photo_with_caption(
    bot_token: str,
    chat_id: int,
    photo: io.BytesIO,
    caption: str,
    reply_markup: Optional[Dict[str, Any]] = None
):
    if not bot_token:
        logging.error("❌ BOT_TOKEN خالی است! عکس ارسال نشد.")
        return {"ok": False}

    url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"

    # مطمئن شویم از ابتدای بایت‌ها خوانده می‌شود
    if hasattr(photo, "seek"):
        photo.seek(0)

    files = {
        "photo": ("chart.png", photo, "image/png")
    }

    data: Dict[str, Any] = {
        "chat_id": chat_id,
        "caption": caption,
        "parse_mode": "MarkdownV2"
    }

    if reply_markup is not None:
        data["reply_markup"] = json.dumps(reply_markup)

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, data=data, files=files)
            if response.status_code != 200:
                logging.error(
                    f"❌ خطای HTTP در sendPhoto: {response.status_code} → {response.text}"
                )
                await send_message(
                    bot_token,
                    chat_id,
                    escape_markdown_v2(f"❌ خطا در ارسال عکس:\n{response.status_code}")
                )
                return {"ok": False}

            logging.info(f"🖼 عکس ارسال شد → {response.status_code}")
            return response.json()

    except httpx.HTTPError as e:
        logging.error(f"❌ خطای شبکه/HTTP در sendPhoto: {repr(e)}")
        await send_message(
            bot_token,
            chat_id,
            escape_markdown_v2("❌ خطای شبکه در ارسال عکس.")
        )
        return {"ok": False}

    except Exception as e:
        logging.error(f"❌ خطای ناشناخته در sendPhoto: {repr(e)}")
        return {"ok": False}


# =============================================================================
# ۵) تبدیل تاریخ و زمان
# =============================================================================

def parse_persian_date(date_str: str) -> Optional[JalaliDate]:
    try:
        return JalaliDate.strptime(date_str, "%Y/%m/%d")
    except ValueError:
        return None


def parse_persian_time(time_str: str) -> Optional[str]:
    try:
        datetime.datetime.strptime(time_str, "%H:%M")
        return time_str
    except ValueError:
        return None


# =============================================================================
# ۶) جستجوی شهر
# =============================================================================

def get_city_lookup_data(city_name: str) -> Optional[Dict[str, Any]]:
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
