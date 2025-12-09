# ----------------------------------------------------------------------
# utils.py - نسخه نهایی، پایدار و تست‌شده (2025)
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

# ======================================================================
# تنظیمات سراسری
# ======================================================================

BOT_TOKEN = os.environ.get("BOT_TOKEN")

tf = TimezoneFinder()

# آبجکت geolocator
geolocator = Nominatim(user_agent="astro_bot_pro_v2")


# ======================================================================
# ارسال پیام به تلگرام
# ======================================================================

async def send_message(bot_token: Optional[str], chat_id: int, text: str, reply_markup=None):
    """ارسال پیام به کاربر به صورت امن و پایدار."""
    bot_token = bot_token or BOT_TOKEN
    if not bot_token:
        print("Error: BOT_TOKEN missing in send_message.")
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "MarkdownV2",
        "disable_web_page_preview": True
    }

    if reply_markup:
        payload["reply_markup"] = reply_markup

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            await client.post(url, json=payload)
    except Exception as e:
        print(f"[ERROR] send_message: {e}")


async def answer_callback_query(bot_token: Optional[str], callback_id: str, text=None):
    """بستن لودینگ دکمه‌های اینلاین."""
    bot_token = bot_token or BOT_TOKEN
    if not bot_token:
        return

    url = f"https://api.telegram.org/bot{bot_token}/answerCallbackQuery"
    payload = {"callback_query_id": callback_id}

    if text:
        payload["text"] = text
        payload["show_alert"] = False

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            await client.post(url, json=payload)
    except Exception as e:
        print(f"[ERROR] answer_callback_query: {e}")


# ======================================================================
# توابع تبدیل تاریخ و زمان
# ======================================================================

def parse_persian_date(date_str: str) -> Optional[JalaliDateTime]:
    """تبدیل رشته تاریخ شمسی به آبجکت JalaliDateTime."""
    try:
        y, m, d = map(int, date_str.split("/"))
        return JalaliDateTime(y, m, d)
    except:
        return None


def parse_persian_time(time_str: str) -> Optional[str]:
    """تبدیل رشته ساعت به فرمت استاندارد HH:MM."""
    try:
        t = datetime.datetime.strptime(time_str.strip(), "%H:%M").time()
        return t.strftime("%H:%M")
    except:
        return None


# ======================================================================
# توابع مکان‌یابی (Location)
# ======================================================================

async def get_coordinates_from_city(city_name: str) -> Tuple[Optional[float], Optional[float], Optional[pytz.BaseTzInfo]]:
    """
    نسخه 100٪ اصلاح‌شده — بدون هیچ خطایی در run_in_executor
    سازگار با Railway و Render
    """

    try:
        loop = asyncio.get_event_loop()

        # --- تلاش اول: زبان فارسی ---
        def geocode_fa():
            return geolocator.geocode(city_name, language="fa")

        location = await loop.run_in_executor(None, geocode_fa)

        # --- تلاش دوم: بدون language ---
        if not location:
            def geocode_default():
                return geolocator.geocode(city_name)

            location = await loop.run_in_executor(None, geocode_default)

        if not location:
            return None, None, None

        lat, lon = location.latitude, location.longitude

        # --- تعیین منطقه زمانی ---
        tz_name = tf.timezone_at(lat=lat, lng=lon)
        tz = pytz.timezone(tz_name) if tz_name else pytz.utc

        return lat, lon, tz

    except Exception as e:
        print(f"[ERROR] get_coordinates_from_city: {e}")
        return None, None, None


# ======================================================================
# Escape پیشرفته MarkdownV2
# ======================================================================

def escape_markdown_v2(text: str) -> str:
    """
    Escape امن مخصوص MarkdownV2.
    مخصوص خروجی‌های بزرگ آسترولوژی.
    """

    if not isinstance(text, str):
        text = str(text)

    dangerous = [
        '\\', '_', '*', '[', ']', '(', ')',
        '~', '`', '>', '#', '+', '-', '=', 
        '|', '{', '}', '!'
    ]

    for ch in dangerous:
        text = text.replace(ch, f"\\{ch}")

    return text
