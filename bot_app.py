 # bot_app.py
# =============================================================================
# نسخهٔ دیباگ کامل — مدل سه‌مرحله‌ای
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
# تنظیمات لاگ
# -----------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bot-debug")

# -----------------------------------------------------------------------------
# تنظیمات ربات و FastAPI
# -----------------------------------------------------------------------------

BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

app = FastAPI()

# -----------------------------------------------------------------------------
# حافظهٔ state کاربران (در حافظهٔ RAM — فقط برای تست/دیباگ)
# -----------------------------------------------------------------------------

user_state = {}

# -----------------------------------------------------------------------------
# توابع ارسال پیام/عکس به تلگرام
# -----------------------------------------------------------------------------

async def send_message(chat_id: int, text: str):
    logger.info(f"📤 ارسال پیام به {chat_id}: {text}")
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.post(
                f"{TELEGRAM_API}/sendMessage",
                json={"chat_id": chat_id, "text": text}
            )
            logger.info(f"✅ sendMessage status: {resp.status_code}, body: {resp.text}")
        except Exception as e:
            logger.error(f"❌ خطا در sendMessage: {e}")


async def send_photo(chat_id: int, image_bytes: bytes, caption: str | None = None):
    logger.info(f"📤 ارسال عکس به {chat_id}")
    async with httpx.AsyncClient(timeout=30) as client:
        files = {"photo": ("chart.png", image_bytes, "image/png")}
        data = {"chat_id": chat_id}
        if caption:
            data["caption"] = caption

        try:
            resp = await client.post(
                f"{TELEGRAM_API}/sendPhoto",
                data=data,
                files=files
            )
            logger.info(f"✅ sendPhoto status: {resp.status_code}, body: {resp.text}")
        except Exception as e:
            logger.error(f"❌ خطا در sendPhoto: {e}")

# -----------------------------------------------------------------------------
# تبدیل تاریخ جلالی → میلادی
# -----------------------------------------------------------------------------

def jalali_to_gregorian(jdate: str) -> str:
    logger.info(f"🔄 تبدیل تاریخ جلالی: {jdate}")
    jdate = jdate.replace("-", "/")
    parts = jdate.split("/")
    if len(parts) != 3:
        raise ValueError("فرمت تاریخ جلالی صحیح نیست. مثال: 1359/05/29")

    jy, jm, jd = map(int, parts)
    g = jdatetime.date(jy, jm, jd).togregorian()
    g_date = g.strftime("%Y-%m-%d")
    logger.info(f"📌 تاریخ میلادی: {g_date}")
    return g_date

# -----------------------------------------------------------------------------
# Webhook اصلی ربات
# -----------------------------------------------------------------------------

@app.post("/")
async def telegram_webhook(request: Request):
    update = await request.json()
    logger.info(f"📩 Update دریافت شد:\n{update}")

    if "message" not in update:
        logger.warning("⚠️ پیام بدون message دریافت شد")
        return JSONResponse({"ok": True})

    message = update["message"]
    chat_id = message["chat"]["id"]
    text = message.get("text", "").strip()

    # -----------------------------
    # فرمان /start
    # -----------------------------
    if text.startswith("/start"):
        user_state[chat_id] = {"step": 1}
        logger.info(f"🚀 شروع گفتگو با کاربر {chat_id}")
        await send_message(chat_id, "تاریخ تولد را وارد کن (جلالی):\nمثال: 1359/05/29")
        return JSONResponse({"ok": True})

    # -----------------------------
    # اگر state وجود ندارد → شروع از اول
    # -----------------------------
    if chat_id not in user_state:
        logger.info(f"ℹ️ کاربر {chat_id} state نداشت → شروع از اول")
        user_state[chat_id] = {"step": 1}
        await send_message(chat_id, "تاریخ تولد را وارد کن (جلالی):")
        return JSONResponse({"ok": True})

    step = user_state[chat_id]["step"]
    logger.info(f"📌 مرحله فعلی کاربر {chat_id}: {step}")

    # -----------------------------
    # مرحله ۱ → تاریخ جلالی
    # -----------------------------
    if step == 1:
        try:
            g_date = jalali_to_gregorian(text)
            user_state[chat_id]["date"] = g_date
            user_state[chat_id]["jalali"] = text
            user_state[chat_id]["step"] = 2

            logger.info(f"✔ تاریخ ذخیره شد: {g_date}")
            await send_message(chat_id, "ساعت تولد را وارد کن:\nمثال: 17:35")

        except Exception as e:
            logger.error(f"❌ خطا در تاریخ: {e}")
            await send_message(chat_id, "فرمت تاریخ صحیح نیست. مثال: 1359/05/29")

        return JSONResponse({"ok": True})

    # -----------------------------
    # مرحله ۲ → ساعت
    # -----------------------------
    if step == 2:
        if ":" not in text:
            logger.error("❌ فرمت ساعت اشتباه است")
            await send_message(chat_id, "فرمت ساعت صحیح نیست. مثال: 17:35")
            return JSONResponse({"ok": True})

        user_state[chat_id]["time"] = text
        user_state[chat_id]["step"] = 3

        logger.info(f"✔ ساعت ذخیره شد: {text}")
        await send_message(chat_id, "شهر تولد را وارد کن:")

        return JSONResponse({"ok": True})

    # -----------------------------
    # مرحله ۳ → شهر
    # -----------------------------
    if step == 3:
        user_state[chat_id]["city"] = text
        logger.info(f"✔ شهر ذخیره شد: {text}")

        g_date = user_state[chat_id]["date"]
        j_date = user_state[chat_id]["jalali"]
        b_time = user_state[chat_id]["time"]
        b_city = user_state[chat_id]["city"]

        logger.info("📌 داده‌های نهایی کاربر:")
        logger.info(f"  - تاریخ جلالی: {j_date}")
        logger.info(f"  - تاریخ میلادی: {g_date}")
        logger.info(f"  - ساعت: {b_time}")
        logger.info(f"  - شهر: {b_city}")

        # پاک کردن state
        del user_state[chat_id]

        # -----------------------------
        # محاسبه چارت
        # -----------------------------
        try:
            logger.info("🔮 شروع محاسبه چارت...")
            
            # جدید (هات‌فیکس موقت)
            chart_data = calculate_natal_chart(
    j_date,         # تاریخ جلالی که خودت در state نگه داشته‌ای
    b_time,         # ساعت تولد به صورت "HH:MM"
    35.6892,        # latitude تهران - فعلاً پیش‌فرض
    51.3890,        # longitude تهران - فعلاً پیش‌فرض
    "Asia/Tehran"   # منطقهٔ زمانی
            )
            chart_data = calculate_natal_chart(g_date, b_time, b_city, None, "Asia/Tehran")
            #جدید
            #chart_data = calculate_natal_chart(g_date, b_time, b_city)

            logger.info("📌 خروجی calculate_natal_chart:")
            logger.info(chart_data)

            if not chart_data:
                raise ValueError("خروجی چارت خالی است!")

            if "planets_list" not in chart_data or not chart_data["planets_list"]:
                raise ValueError("لیست سیارات خالی است!")

            if "cusps" not in chart_data or not chart_data["cusps"]:
                raise ValueError("خانه‌ها خالی هستند!")

            if len(chart_data["cusps"]) != 12:
                raise ValueError("تعداد خانه‌ها باید ۱۲ باشد!")

            if "ascendant" not in chart_data:
                raise ValueError("صعودی (ASC) در چارت وجود ندارد!")

            logger.info("✔ چارت کامل و معتبر است")

            # -----------------------------
            # رسم چارت
            # -----------------------------
            logger.info("🎨 شروع رسم چارت...")
            image_bytes = draw_chart_advanced_fa(chart_data)

            if not image_bytes:
                raise ValueError("خروجی رسم چارت خالی است!")

            logger.info("✔ چارت با موفقیت رسم شد")

            # -----------------------------
            # ارسال عکس
            # -----------------------------
            await send_photo(
                chat_id,
                image_bytes,
                caption="چارت تولد شما آماده شد 🌟"
            )

            logger.info("📤 عکس با موفقیت ارسال شد")

        except Exception as e:
            logger.error(f"❌ خطا در محاسبه یا رسم چارت: {e}")
            await send_message(chat_id, f"خطا در محاسبه چارت:\n{e}")

        return JSONResponse({"ok": True})     
