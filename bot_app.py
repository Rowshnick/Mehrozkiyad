# bot_app.py
# =============================================================================
# FastAPI Telegram Webhook Handler
# مدل سه‌مرحله‌ای: تاریخ جلالی → ساعت → شهر
# =============================================================================

import os
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx
import jdatetime

from astrology_core import calculate_natal_chart
from chart_drawer_fa import draw_chart_advanced_fa

# -----------------------------------------------------------------------------
# تنظیمات
# -----------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bot")

BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

app = FastAPI()

# -----------------------------------------------------------------------------
# حافظهٔ ساده برای نگه‌داری state کاربران
# -----------------------------------------------------------------------------

user_state = {}  
# ساختار:
# user_state[chat_id] = {
#     "step": 1/2/3,
#     "date": "",
#     "time": "",
#     "city": ""
# }


# -----------------------------------------------------------------------------
# توابع ارسال پیام
# -----------------------------------------------------------------------------

async def send_message(chat_id: int, text: str):
    async with httpx.AsyncClient(timeout=10) as client:
        await client.post(
            f"{TELEGRAM_API}/sendMessage",
            json={"chat_id": chat_id, "text": text}
        )


async def send_photo(chat_id: int, image_bytes, caption: str = None):
    async with httpx.AsyncClient(timeout=20) as client:
        files = {"photo": ("chart.png", image_bytes, "image/png")}
        data = {"chat_id": chat_id}
        if caption:
            data["caption"] = caption

        await client.post(
            f"{TELEGRAM_API}/sendPhoto",
            data=data,
            files=files
        )


# -----------------------------------------------------------------------------
# تبدیل تاریخ جلالی → میلادی
# -----------------------------------------------------------------------------

def jalali_to_gregorian(jdate: str) -> str:
    jdate = jdate.replace("-", "/")
    parts = jdate.split("/")
    if len(parts) != 3:
        raise ValueError("فرمت تاریخ جلالی صحیح نیست. مثال: 1359/05/29")

    jy, jm, jd = map(int, parts)
    g = jdatetime.date(jy, jm, jd).togregorian()
    return g.strftime("%Y-%m-%d")


# -----------------------------------------------------------------------------
# Webhook
# -----------------------------------------------------------------------------

@app.post("/")
async def telegram_webhook(request: Request):
    update = await request.json()
    logger.info(f"📩 Update: {update}")

    if "message" not in update:
        return JSONResponse({"ok": True})

    message = update["message"]
    chat_id = message["chat"]["id"]
    text = message.get("text", "").strip()

    # -----------------------------
    # فرمان /start
    # -----------------------------
    if text.startswith("/start"):
        user_state[chat_id] = {"step": 1}
        await send_message(chat_id, "تاریخ تولد را وارد کن (جلالی):\nمثال: 1359/05/29")
        return JSONResponse({"ok": True})

    # -----------------------------
    # اگر کاربر در state نیست → شروع از اول
    # -----------------------------
    if chat_id not in user_state:
        user_state[chat_id] = {"step": 1}
        await send_message(chat_id, "تاریخ تولد را وارد کن (جلالی):")
        return JSONResponse({"ok": True})

    step = user_state[chat_id]["step"]

    # -----------------------------
    # مرحله ۱ → تاریخ جلالی
    # -----------------------------
    if step == 1:
        try:
            gregorian_date = jalali_to_gregorian(text)
            user_state[chat_id]["date"] = gregorian_date
            user_state[chat_id]["jalali"] = text
            user_state[chat_id]["step"] = 2
            await send_message(chat_id, "ساعت تولد را وارد کن:\nمثال: 17:35")
        except Exception:
            await send_message(chat_id, "فرمت تاریخ صحیح نیست. مثال: 1359/05/29")
        return JSONResponse({"ok": True})

    # -----------------------------
    # مرحله ۲ → ساعت تولد
    # -----------------------------
    if step == 2:
        if ":" not in text:
            await send_message(chat_id, "فرمت ساعت صحیح نیست. مثال: 17:35")
            return JSONResponse({"ok": True})

        user_state[chat_id]["time"] = text
        user_state[chat_id]["step"] = 3
        await send_message(chat_id, "شهر تولد را وارد کن:")
        return JSONResponse({"ok": True})

    # -----------------------------
    # مرحله ۳ → شهر تولد
    # -----------------------------
    if step == 3:
        user_state[chat_id]["city"] = text

        # گرفتن داده‌ها
        g_date = user_state[chat_id]["date"]
        j_date = user_state[chat_id]["jalali"]
        b_time = user_state[chat_id]["time"]
        b_city = user_state[chat_id]["city"]

        # پاک کردن state
        del user_state[chat_id]

        # محاسبه چارت
        try:
            chart_data = calculate_natal_chart(g_date, b_time, b_city)
            image_bytes = draw_chart_advanced_fa(chart_data)

            caption = (
                "چارت نجومی شما آماده شد 🌙\n\n"
                f"تاریخ (جلالی): {j_date}\n"
                f"تاریخ (میلادی): {g_date}\n"
                f"ساعت: {b_time}\n"
                f"شهر: {b_city}"
            )

            await send_photo(chat_id, image_bytes, caption)

        except Exception as e:
            logger.error(f"❌ خطا در محاسبه چارت: {e}")
            await send_message(chat_id, "خطا در محاسبه چارت. لطفاً دوباره تلاش کن.")

        return JSONResponse({"ok": True})


# -----------------------------------------------------------------------------
# Health Check
# -----------------------------------------------------------------------------

@app.get("/")
async def root():
    return {"status": "ok", "service": "mehrozkiyad-bot"}
