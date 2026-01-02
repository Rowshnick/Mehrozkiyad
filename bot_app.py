# bot_app.py
# =============================================================================
# نسخهٔ پیشرفته و چندحالته ربات:
# ۱) چارت تولد + تفسیر حرفه‌ای با نکات/هشدار/پیشنهاد
# ۲) پیش‌بینی سالانه (Solar Return)
# ۳) سینستری (تطبیق دو نفر)
# ۴) آماده برای تولید گزارش چندصفحه‌ای (PDF) در لایهٔ جداگانه
# =============================================================================

import os
import logging
from typing import Dict, Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx
import jdatetime

from astrology_core import calculate_natal_chart
from chart_drawer_fa import draw_chart_advanced_fa

# تفسیر ناتال (فایل قبلی که ساختیم)
from interpretations_natal import interpret_natal_chart, format_natal_for_user

# توجه: این سه ماژول را باید جداگانه پیاده‌سازی کنی
# (امضاها را این‌جا مشخص می‌کنم که bot_app.py آماده باشد)
# از الان فقط import می‌کنیم؛ بعداً فایل‌ها را می‌سازیم.
try:
    from solar_return import calculate_solar_return_chart, interpret_solar_return, format_solar_for_user
except ImportError:
    calculate_solar_return_chart = None
    interpret_solar_return = None
    format_solar_for_user = None

try:
    from synastry import calculate_synastry_chart, interpret_synastry, format_synastry_for_user
except ImportError:
    calculate_synastry_chart = None
    interpret_synastry = None
    format_synastry_for_user = None

try:
    from report_builder import build_natal_pdf_report, build_solar_pdf_report, build_synastry_pdf_report
except ImportError:
    build_natal_pdf_report = None
    build_solar_pdf_report = None
    build_synastry_pdf_report = None

# -----------------------------------------------------------------------------
# لاگ
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
# state کاربران
# -----------------------------------------------------------------------------

# ساختار نمونه:
# user_state[chat_id] = {
#   "mode": "natal" | "solar" | "synastry",
#   "step": 1/2/3/4...,
#   ...
# }
user_state: Dict[int, Dict[str, Any]] = {}

# -----------------------------------------------------------------------------
# توابع ارسال به تلگرام
# -----------------------------------------------------------------------------

async def send_message(chat_id: int, text: str):
    logger.info(f"📤 ارسال پیام به {chat_id}: {text}")
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.post(
                f"{TELEGRAM_API}/sendMessage",
                json={"chat_id": chat_id, "text": text}
            )
            logger.info(f"✅ sendMessage {resp.status_code}: {resp.text}")
        except Exception as e:
            logger.error(f"❌ خطا در sendMessage: {e}")


async def send_photo(chat_id: int, image_bytes: bytes, caption: str | None = None):
    logger.info(f"📤 ارسال عکس به {chat_id}")
    async with httpx.AsyncClient(timeout=40) as client:
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
            logger.info(f"✅ sendPhoto {resp.status_code}: {resp.text}")
        except Exception as e:
            logger.error(f"❌ خطا در sendPhoto: {e}")


async def send_document(chat_id: int, file_bytes: bytes, filename: str, caption: str | None = None):
    """
    ارسال فایل (برای گزارش PDF چندصفحه‌ای).
    """
    logger.info(f"📤 ارسال فایل به {chat_id}: {filename}")
    async with httpx.AsyncClient(timeout=60) as client:
        files = {"document": (filename, file_bytes, "application/pdf")}
        data = {"chat_id": chat_id}
        if caption:
            data["caption"] = caption
        try:
            resp = await client.post(
                f"{TELEGRAM_API}/sendDocument",
                data=data,
                files=files
            )
            logger.info(f"✅ sendDocument {resp.status_code}: {resp.text}")
        except Exception as e:
            logger.error(f"❌ خطا در sendDocument: {e}")

# -----------------------------------------------------------------------------
# ابزار تاریخ
# -----------------------------------------------------------------------------

def jalali_to_gregorian(jdate: str) -> str:
    """
    ورودی: '1359/05/29' یا '1359-05-29'
    خروجی: 'YYYY-MM-DD'
    """
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
# دیتابیس سادهٔ شهرها
# -----------------------------------------------------------------------------

CITY_DB = {
    "تهران":  (35.6892, 51.3890),
    "اراک":   (34.0954, 49.7013),
    "مشهد":   (36.2605, 59.6168),
    "اصفهان": (32.6546, 51.6680),
    "شیراز":  (29.5918, 52.5837),
    "تبریز":  (38.0962, 46.2738),
    # شهرهای بیشتر را می‌توانی اضافه کنی
}

# -----------------------------------------------------------------------------
# شروع گفتگو / انتخاب حالت
# -----------------------------------------------------------------------------

START_TEXT = (
    "سلام 🌟\n"
    "نوع گزارش مورد نظر را انتخاب کن:\n\n"
    "1️⃣ چارت تولد + تفسیر حرفه‌ای (شخصیت، عشق، شغل، چالش، شانس)\n"
    "2️⃣ پیش‌بینی سالانه (Solar Return)\n"
    "3️⃣ سینستری (تطبیق رابطهٔ دو نفر)\n\n"
    "فقط شماره را بفرست (۱ یا ۲ یا ۳)."
)

# -----------------------------------------------------------------------------
# Webhook اصلی
# -----------------------------------------------------------------------------

@app.post("/")
async def telegram_webhook(request: Request):
    update = await request.json()
    logger.info(f"📩 Update:\n{update}")

    if "message" not in update:
        return JSONResponse({"ok": True})

    message = update["message"]
    chat_id = message["chat"]["id"]
    text = message.get("text", "").strip()

    # /start → نمایش منو
    if text.startswith("/start"):
        user_state[chat_id] = {"step": 0, "mode": None}
        await send_message(chat_id, START_TEXT)
        return JSONResponse({"ok": True})

    # اگر state وجود ندارد → از منو شروع کنیم
    if chat_id not in user_state:
        user_state[chat_id] = {"step": 0, "mode": None}
        await send_message(chat_id, START_TEXT)
        return JSONResponse({"ok": True})

    state = user_state[chat_id]
    step = state.get("step", 0)
    mode = state.get("mode")

    # -------------------------------------------------------------------------
    # مرحله ۰: انتخاب نوع گزارش
    # -------------------------------------------------------------------------
    if step == 0:
        if text in ["1", "۱"]:
            state["mode"] = "natal"
            state["step"] = 1
            await send_message(chat_id, "🔹 حالت: چارت تولد + تفسیر حرفه‌ای\nتاریخ تولد را وارد کن (جلالی):\nمثال: 1359/05/29")
        elif text in ["2", "۲"]:
            state["mode"] = "solar"
            state["step"] = 1
            await send_message(chat_id, "🔹 حالت: پیش‌بینی سالانه (Solar Return)\nتاریخ تولد را وارد کن (جلالی):")
        elif text in ["3", "۳"]:
            state["mode"] = "synastry"
            state["step"] = 1
            await send_message(chat_id, "🔹 حالت: سینستری (تطبیق دو نفر)\nتاریخ تولد نفر اول را وارد کن (جلالی):")
        else:
            await send_message(chat_id, "لطفاً یکی از گزینه‌های ۱، ۲ یا ۳ را انتخاب کن.")
        return JSONResponse({"ok": True})

    # از اینجا به بعد بر اساس mode به سه شاخه می‌رویم
    if mode == "natal":
        return await handle_natal(chat_id, text)
    elif mode == "solar":
        return await handle_solar(chat_id, text)
    elif mode == "synastry":
        return await handle_synastry(chat_id, text)
    else:
        # اگر به هر دلیل mode خراب شد، از نو
        user_state[chat_id] = {"step": 0, "mode": None}
        await send_message(chat_id, START_TEXT)
        return JSONResponse({"ok": True})


# -----------------------------------------------------------------------------
# ۱) ناتال + تفسیر حرفه‌ای
# -----------------------------------------------------------------------------

async def handle_natal(chat_id: int, text: str):
    state = user_state[chat_id]
    step = state["step"]

    # مرحله ۱: تاریخ
    if step == 1:
        try:
            g_date = jalali_to_gregorian(text)
            state["jalali"] = text
            state["date"] = g_date
            state["step"] = 2
            await send_message(chat_id, "ساعت تولد را وارد کن:\nمثال: 17:35")
        except Exception:
            await send_message(chat_id, "فرمت تاریخ صحیح نیست. مثال: 1359/05/29")
        return JSONResponse({"ok": True})

    # مرحله ۲: ساعت
    if step == 2:
        if ":" not in text:
            await send_message(chat_id, "فرمت ساعت صحیح نیست. مثال: 17:35")
            return JSONResponse({"ok": True})
        state["time"] = text
        state["step"] = 3
        await send_message(chat_id, "شهر تولد را وارد کن:")
        return JSONResponse({"ok": True})

    # مرحله ۳: شهر → محاسبه چارت، رسم، تفسیر، PDF
    if step == 3:
        b_city = text.strip()
        j_date = state["jalali"]
        g_date = state["date"]
        b_time = state["time"]

        logger.info("📌 داده‌های ناتال:")
        logger.info(f"  - تاریخ جلالی: {j_date}")
        logger.info(f"  - تاریخ میلادی: {g_date}")
        logger.info(f"  - ساعت: {b_time}")
        logger.info(f"  - شهر: {b_city}")

        # state را پاک می‌کنیم
        del user_state[chat_id]

        lat, lon = CITY_DB.get(b_city, (35.6892, 51.3890))
        logger.info(f"📌 مختصات شهر: lat={lat}, lon={lon}")

        try:
            logger.info("🔮 شروع محاسبه چارت ناتال...")
            chart_data = calculate_natal_chart(
                j_date,
                b_time,
                lat,
                lon,
                "Asia/Tehran"
            )

            if not chart_data:
                raise ValueError("خروجی چارت خالی است.")
            if "planets_list" not in chart_data or not chart_data["planets_list"]:
                raise ValueError("لیست سیارات خالی است.")
            if "cusps" not in chart_data or len(chart_data["cusps"]) != 12:
                raise ValueError("خانه‌ها ناقص هستند.")

            logger.info("🎨 شروع رسم چارت ناتال...")
            image_bytes = draw_chart_advanced_fa(chart_data)
            await send_photo(chat_id, image_bytes, caption="چارت تولد شما آماده شد 🌟")

            logger.info("🧠 شروع تفسیر ناتال حرفه‌ای...")
            ints = interpret_natal_chart(chart_data)
            text_out = format_natal_for_user(ints)
            await send_message(chat_id, text_out)

            # اگر ماژول PDF موجود بود، گزارش چندصفحه‌ای بفرست
            if build_natal_pdf_report is not None:
                logger.info("📄 ساخت گزارش PDF ناتال...")
                pdf_bytes = build_natal_pdf_report(chart_data, text_out)
                await send_document(chat_id, pdf_bytes, "natal_report.pdf", caption="گزارش کامل ناتال شما (PDF)")

        except Exception as e:
            logger.error(f"❌ خطا در چارت ناتال: {e}")
            await send_message(chat_id, f"خطا در محاسبه یا تفسیر چارت تولد:\n{e}")

        return JSONResponse({"ok": True})

    # اگر به هر دلیل step غیرمنتظره بود:
    user_state[chat_id] = {"step": 0, "mode": None}
    await send_message(chat_id, START_TEXT)
    return JSONResponse({"ok": True})


# -----------------------------------------------------------------------------
# ۲) Solar Return (پیش‌بینی سالانه)
# -----------------------------------------------------------------------------

async def handle_solar(chat_id: int, text: str):
    state = user_state[chat_id]
    step = state["step"]

    if calculate_solar_return_chart is None:
        await send_message(chat_id, "بخش پیش‌بینی سالانه هنوز در حال تکمیل است. به‌زودی فعال می‌شود 🌙")
        state["step"] = 0
        state["mode"] = None
        await send_message(chat_id, START_TEXT)
        return JSONResponse({"ok": True})

    # طراحی ورودی ساده:
    # مرحله ۱: تاریخ تولد (جلالی)
    # مرحله ۲: ساعت تولد
    # مرحله ۳: شهر تولد
    # مرحله ۴: سال مورد نظر (مثلاً 1403)

    if step == 1:
        try:
            g_date = jalali_to_gregorian(text)
            state["jalali"] = text
            state["date"] = g_date
            state["step"] = 2
            await send_message(chat_id, "ساعت تولد را وارد کن (برای محاسبه دقیق Solar):")
        except Exception:
            await send_message(chat_id, "فرمت تاریخ صحیح نیست. مثال: 1359/05/29")
        return JSONResponse({"ok": True})

    if step == 2:
        if ":" not in text:
            await send_message(chat_id, "فرمت ساعت صحیح نیست. مثال: 17:35")
            return JSONResponse({"ok": True})
        state["time"] = text
        state["step"] = 3
        await send_message(chat_id, "شهر تولد را وارد کن:")
        return JSONResponse({"ok": True})

    if step == 3:
        state["city"] = text.strip()
        state["step"] = 4
        await send_message(chat_id, "سال مورد نظر برای پیش‌بینی را وارد کن (مثلاً 1403):")
        return JSONResponse({"ok": True})

    if step == 4:
        year_text = text.strip()
        if not year_text.isdigit():
            await send_message(chat_id, "سال را به‌صورت عددی وارد کن، مثلاً 1403.")
            return JSONResponse({"ok": True})
        target_year = int(year_text)

        j_date = state["jalali"]
        g_date = state["date"]
        b_time = state["time"]
        b_city = state["city"]
        del user_state[chat_id]

        lat, lon = CITY_DB.get(b_city, (35.6892, 51.3890))
        logger.info("📌 داده‌های Solar:")
        logger.info(f"  - تاریخ جلالی: {j_date}")
        logger.info(f"  - تاریخ میلادی: {g_date}")
        logger.info(f"  - ساعت: {b_time}")
        logger.info(f"  - شهر: {b_city}")
        logger.info(f"  - سال هدف: {target_year}")

        try:
            logger.info("🔮 محاسبه چارت Solar Return...")
            solar_chart = calculate_solar_return_chart(
                j_date,
                b_time,
                lat,
                lon,
                "Asia/Tehran",
                target_year
            )

            logger.info("🎨 رسم چارت Solar (با همان تابع ناتال یا نسخهٔ جداگانه)...")
            image_bytes = draw_chart_advanced_fa(solar_chart)
            await send_photo(chat_id, image_bytes, caption=f"چارت Solar سال {target_year} شما 🌞")

            logger.info("🧠 تفسیر سالانه...")
            sols = interpret_solar_return(solar_chart)
            text_out = format_solar_for_user(sols)
            await send_message(chat_id, text_out)

            if build_solar_pdf_report is not None:
                logger.info("📄 ساخت گزارش PDF Solar...")
                pdf_bytes = build_solar_pdf_report(solar_chart, text_out, target_year)
                await send_document(chat_id, pdf_bytes, f"solar_{target_year}.pdf", caption="گزارش کامل سالانه (PDF)")

        except Exception as e:
            logger.error(f"❌ خطا در Solar Return: {e}")
            await send_message(chat_id, f"خطا در محاسبه یا تفسیر Solar Return:\n{e}")

        return JSONResponse({"ok": True})

    user_state[chat_id] = {"step": 0, "mode": None}
    await send_message(chat_id, START_TEXT)
    return JSONResponse({"ok": True})


# -----------------------------------------------------------------------------
# ۳) سینستری (تطبیق دو نفر)
# -----------------------------------------------------------------------------

async def handle_synastry(chat_id: int, text: str):
    state = user_state[chat_id]
    step = state["step"]

    if calculate_synastry_chart is None:
        await send_message(chat_id, "بخش سینستری (تطبیق دو نفر) هنوز در حال تکمیل است. به‌زودی فعال می‌شود 💞")
        state["step"] = 0
        state["mode"] = None
        await send_message(chat_id, START_TEXT)
        return JSONResponse({"ok": True})

    # طراحی ورودی:
    # نفر ۱: تاریخ، ساعت، شهر (سه مرحله)
    # نفر ۲: تاریخ، ساعت، شهر (سه مرحله)

    # نفر ۱
    if step == 1:
        try:
            _ = jalali_to_gregorian(text)
            state["p1_jalali"] = text
            state["step"] = 2
            await send_message(chat_id, "ساعت تولد نفر اول را وارد کن:")
        except Exception:
            await send_message(chat_id, "فرمت تاریخ صحیح نیست. مثال: 1359/05/29")
        return JSONResponse({"ok": True})

    if step == 2:
        if ":" not in text:
            await send_message(chat_id, "فرمت ساعت صحیح نیست. مثال: 17:35")
            return JSONResponse({"ok": True})
        state["p1_time"] = text
        state["step"] = 3
        await send_message(chat_id, "شهر تولد نفر اول را وارد کن:")
        return JSONResponse({"ok": True})

    if step == 3:
        state["p1_city"] = text.strip()
        state["step"] = 4
        await send_message(chat_id, "تاریخ تولد نفر دوم را وارد کن (جلالی):")
        return JSONResponse({"ok": True})

    # نفر ۲
    if step == 4:
        try:
            _ = jalali_to_gregorian(text)
            state["p2_jalali"] = text
            state["step"] = 5
            await send_message(chat_id, "ساعت تولد نفر دوم را وارد کن:")
        except Exception:
            await send_message(chat_id, "فرمت تاریخ صحیح نیست. مثال: 1365/01/15")
       -

async def handle_synastry(chat_id: int, text: str):
    state = user_state[chat_id]
    step = state["step"]

    if calculate_synastry_chart is None:
        await send_message(chat_id, "بخش سینستری (تطبیق دو نفر) هنوز در حال تکمیل است. به‌زودی فعال می‌شود 💞")
        state["step"] = 0
        state["mode"] = None
        await send_message(chat_id, START_TEXT)
        return JSONResponse({"ok": True})

    # طراحی ورودی:
    # نفر ۱: تاریخ، ساعت، شهر (سه مرحله)
    # نفر ۲: تاریخ، ساعت، شهر (سه مرحله)

    # نفر ۱
    if step == 1:
        try:
            _ = jalali_to_gregorian(text)
            state["p1_jalali"] = text
            state["step"] = 2
            await send_message(chat_id, "ساعت تولد نفر اول را وارد کن:")
        except Exception:
            await send_message(chat_id, "فرمت تاریخ صحیح نیست. مثال: 1359/05/29")
        return JSONResponse({"ok": True})

    if step == 2:
        if ":" not in text:
            await send_message(chat_id, "فرمت ساعت صحیح نیست. مثال: 17:35")
            return JSONResponse({"ok": True})
        state["p1_time"] = text
        state["step"] = 3
        await send_message(chat_id, "شهر تولد نفر اول را وارد کن:")
        return JSONResponse({"ok": True})

    if step == 3:
        state["p1_city"] = text.strip()
        state["step"] = 4
        await send_message(chat_id, "تاریخ تولد نفر دوم را وارد کن (جلالی):")
        return JSONResponse({"ok": True})

    # نفر ۲
    if step == 4:
        try:
            _ = jalali_to_gregorian(text)
            state["p2_jalali"] = text
            state["step"] = 5
            await send_message(chat_id, "ساعت تولد نفر دوم را وارد کن:")
        except Exception:
            await send_message(chat_id, "فرمت تاریخ صحیح نیست. مثال: 1365/01/15")
