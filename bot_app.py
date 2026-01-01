# bot_app.py
# =============================================================================
# FastAPI Telegram Webhook Handler
# نسخهٔ پیشرفته، سازگار با Render + چارت فارسی پیشرفته
# =============================================================================

import os
import logging
from typing import Tuple, Optional

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse
import httpx

from astrology_core import calculate_natal_chart
from chart_drawer_fa import draw_chart_advanced_fa

# -----------------------------------------------------------------------------
# تنظیمات اولیه و لاگ
# -----------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger("bot_app")

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # اگر خواستی به‌صورت خودکار ست کنیم
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

if not BOT_TOKEN:
    logger.error("❌ متغیر محیطی BOT_TOKEN تنظیم نشده است!")

app = FastAPI(title="Mehrozkiyad Telegram Bot")


# -----------------------------------------------------------------------------
# توابع کمکی تلگرام
# -----------------------------------------------------------------------------

async def send_message(
    chat_id: int,
    text: str,
    reply_markup: Optional[dict] = None,
    parse_mode: Optional[str] = None,
):
    payload = {
        "chat_id": chat_id,
        "text": text,
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    if parse_mode:
        payload["parse_mode"] = parse_mode

    async with httpx.AsyncClient(timeout=15) as client:
        try:
            await client.post(f"{TELEGRAM_API}/sendMessage", json=payload)
        except Exception as e:
            logger.error(f"❌ خطا در ارسال پیام: {e}")


async def send_chat_action(chat_id: int, action: str = "upload_photo"):
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            await client.post(
                f"{TELEGRAM_API}/sendChatAction",
                json={"chat_id": chat_id, "action": action},
            )
        except Exception as e:
            logger.error(f"❌ خطا در ارسال chat_action: {e}")


async def send_photo(
    chat_id: int,
    image_bytes,
    caption: Optional[str] = None,
    reply_markup: Optional[dict] = None,
):
    data = {"chat_id": chat_id}
    if caption:
        data["caption"] = caption

    if reply_markup:
        data["reply_markup"] = reply_markup

    files = {"photo": ("chart.png", image_bytes, "image/png")}

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            await client.post(
                f"{TELEGRAM_API}/sendPhoto",
                data=data,
                files=files,
            )
        except Exception as e:
            logger.error(f"❌ خطا در ارسال عکس: {e}")


# -----------------------------------------------------------------------------
# Keyboardها
# -----------------------------------------------------------------------------

def main_menu_keyboard() -> dict:
    return {
        "keyboard": [
            [{"text": "📅 راهنمای فرمت تاریخ تولد"}],
            [{"text": "ℹ️ درباره ربات"}],
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False,
    }


# -----------------------------------------------------------------------------
# پردازش و اعتبارسنجی ورودی تولد
# -----------------------------------------------------------------------------

def parse_birth_input(text: str) -> Tuple[str, str, str]:
    """
    انتظار: چیزی شبیه:
    1990-05-12 14:30 Tehran
    یا:
    1990-05-12 14:30 تهران
    """
    parts = text.strip().split()

    if len(parts) < 2:
        raise ValueError(
            "لطفاً حداقل تاریخ و ساعت را به این شکل بفرست:\n"
            "`YYYY-MM-DD HH:MM شهر`\nمثال:\n`1990-05-12 14:30 Tehran`"
        )

    birth_date = parts[0]  # YYYY-MM-DD
    birth_time = parts[1]  # HH:MM
    birth_city = " ".join(parts[2:]) if len(parts) > 2 else "Tehran"

    # چک خیلی ساده روی فرمت (می‌توانیم بعداً سخت‌گیرتر کنیم)
    if len(birth_date.split("-")) != 3 or ":" not in birth_time:
        raise ValueError(
            "فرمت ورودی درست نیست.\n"
            "مثال صحیح:\n`1990-05-12 14:30 Tehran`"
        )

    return birth_date, birth_time, birth_city


# -----------------------------------------------------------------------------
# فرمان‌ها
# -----------------------------------------------------------------------------

async def handle_start(chat_id: int):
    text = (
        "سلام 🌙\n\n"
        "من ربات محاسبه و ترسیم چارت نجومی هستم.\n"
        "برای شروع، تاریخ و ساعت و شهر تولدت را به این شکل بفرست:\n\n"
        "`YYYY-MM-DD HH:MM City`\n"
        "مثال:\n"
        "`1990-05-12 14:30 Tehran`\n\n"
        "می‌توانی از دکمهٔ «📅 راهنمای فرمت تاریخ تولد» هم استفاده کنی."
    )
    await send_message(chat_id, text, reply_markup=main_menu_keyboard(), parse_mode="Markdown")


async def handle_help(chat_id: int):
    text = (
        "📅 راهنمای ارسال اطلاعات تولد:\n\n"
        "فرمت پیشنهادی:\n"
        "`YYYY-MM-DD HH:MM City`\n\n"
        "مثال:\n"
        "`1990-05-12 14:30 Tehran`\n\n"
        "- تاریخ: سال-ماه-روز (تقویم میلادی)\n"
        "- ساعت: به‌وقت محلی شهر تولد\n"
        "- شهر: نام شهر به انگلیسی یا فارسی (مثلاً Tehran یا تهران)\n\n"
        "بعد از ارسال، چارت نجومی کامل برایت ارسال می‌شود 🌟"
    )
    await send_message(chat_id, text, reply_markup=main_menu_keyboard(), parse_mode="Markdown")


async def handle_about(chat_id: int):
    text = (
        "ℹ️ دربارهٔ این ربات:\n\n"
        "این ربات با استفاده از Swiss Ephemeris و محاسبات دقیق نجومی، "
        "چارت تولد تو را محاسبه و به‌صورت چرخ فارسی با سیارات، خانه‌ها و زوایا ترسیم می‌کند.\n\n"
        "خروجی برای استفاده در موبایل و تلگرام بهینه شده است."
    )
    await send_message(chat_id, text, reply_markup=main_menu_keyboard())


# -----------------------------------------------------------------------------
# تولید و ارسال چارت
# -----------------------------------------------------------------------------

async def handle_birth_message(chat_id: int, text: str):
    try:
        birth_date, birth_time, birth_city = parse_birth_input(text)
    except ValueError as ve:
        await send_message(chat_id, str(ve), reply_markup=main_menu_keyboard(), parse_mode="Markdown")
        return

    await send_chat_action(chat_id, "upload_photo")

    try:
        # محاسبه چارت
        chart_data = calculate_natal_chart(birth_date, birth_time, birth_city)
    except Exception as e:
        logger.error(f"❌ خطا در calculate_natal_chart: {e}")
        await send_message(chat_id, "در محاسبهٔ چارت خطایی رخ داد. لطفاً بعداً دوباره تلاش کن.")
        return

    try:
        # رسم چارت با نسخهٔ پیشرفته
        image_bytes = draw_chart_advanced_fa(chart_data)
    except Exception as e:
        logger.error(f"❌ خطا در رسم چارت: {e}")
        await send_message(chat_id, "در ترسیم چارت خطایی رخ داد. لطفاً بعداً دوباره تلاش کن.")
        return

    caption = (
        "چارت نجومی تولد شما آماده شد 🌟\n\n"
        f"تاریخ: {birth_date}\n"
        f"ساعت: {birth_time}\n"
        f"شهر: {birth_city}"
    )

    await send_photo(chat_id, image_bytes, caption=caption, reply_markup=main_menu_keyboard())


# -----------------------------------------------------------------------------
# Webhook اصلی تلگرام
# -----------------------------------------------------------------------------

@app.post("/")
async def telegram_webhook(request: Request):
    update = await request.json()
    logger.info(f"📩 Update: {update}")

    message = update.get("message") or update.get("edited_message")
    if not message:
        return JSONResponse({"ok": True})

    chat_id = message["chat"]["id"]
    text = message.get("text", "") or ""

    # فرمان‌ها
    if text.startswith("/start"):
        await handle_start(chat_id)
        return JSONResponse({"ok": True})

    if text.startswith("/help") or text == "📅 راهنمای فرمت تاریخ تولد":
        await handle_help(chat_id)
        return JSONResponse({"ok": True})

    if text.startswith("/about") or text == "ℹ️ درباره ربات":
        await handle_about(chat_id)
        return JSONResponse({"ok": True})

    # هر چیز دیگری → تلاش برای تفسیر به‌عنوان اطلاعات تولد
    await handle_birth_message(chat_id, text)
    return JSONResponse({"ok": True})


# -----------------------------------------------------------------------------
# Root / Health Check
# -----------------------------------------------------------------------------

@app.get("/")
async def root():
    return {"status": "ok", "service": "mehrozkiyad-bot"}


@app.get("/health")
async def health():
    return PlainTextResponse("OK")
