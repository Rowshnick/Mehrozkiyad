# bot_app.py
# =============================================================================
# هسته‌ی اجرایی ربات تلگرام (FastAPI + Webhook)
# -----------------------------------------------------------------------------
# این فایل:
#   - پیام‌های ورودی را دریافت می‌کند
#   - state کاربر را مدیریت می‌کند
#   - ورودی تاریخ/زمان/شهر را جمع‌آوری می‌کند
#   - چارت تولد را محاسبه می‌کند
#   - تفسیر فارسی و تصویر چارت را ارسال می‌کند
# =============================================================================

import os
import logging
from fastapi import FastAPI, Request
from typing import Dict, Any

import utils
from state_manager import init_db, get_user_state_db, save_user_state_db

from astrology_core import calculate_natal_chart
from interpret_natal_chart import interpret_natal_chart
from chart_drawer_fa import draw_chart_wheel_fa

import keyboards

# -----------------------------------------------------------------------------
# تنظیمات اولیه
# -----------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
BOT_TOKEN = os.environ.get("BOT_TOKEN")

app = FastAPI()


# =============================================================================
# توابع کمکی State Machine
# =============================================================================

async def get_state(chat_id: int) -> Dict[str, Any]:
    return await get_user_state_db(chat_id)

async def save_state(chat_id: int, state: Dict[str, Any]):
    await save_user_state_db(chat_id, state)


# =============================================================================
# راه‌اندازی دیتابیس هنگام شروع
# =============================================================================

@app.on_event("startup")
async def startup_event():
    await init_db()
    logging.info("📦 دیتابیس state کاربران آماده شد.")


# =============================================================================
# وبهوک اصلی ربات
# =============================================================================

@app.post("/")
async def telegram_webhook(request: Request):
    update = await request.json()

    # پیام متنی
    if "message" in update:
        await handle_message(update["message"])

    # کلیک روی دکمه اینلاین
    if "callback_query" in update:
        await handle_callback(update["callback_query"])

    return {"ok": True}


# =============================================================================
# مدیریت پیام‌های متنی
# =============================================================================

async def handle_message(message: Dict[str, Any]):
    chat_id = message["chat"]["id"]
    text = message.get("text", "").strip()

    state = await get_state(chat_id)
    step = state.get("step", "START")

    # -------------------------------------------------------------------------
    # شروع ربات
    # -------------------------------------------------------------------------
    if step == "START":
        await utils.send_message(
            BOT_TOKEN,
            chat_id,
            utils.escape_markdown_v2("سلام! برای شروع یکی از گزینه‌های زیر را انتخاب کنید:"),
            keyboards.main_menu_keyboard()
        )
        state["step"] = "WELCOME"
        await save_state(chat_id, state)
        return

    # -------------------------------------------------------------------------
    # ورودی تاریخ تولد (شمسی)
    # -------------------------------------------------------------------------
    if step == "ASTRO_DATE":
        date_obj = utils.parse_persian_date(text)
        if not date_obj:
            await utils.send_message(
                BOT_TOKEN, chat_id,
                utils.escape_markdown_v2("❌ تاریخ نامعتبر است. لطفاً به‌صورت YYYY/MM/DD وارد کنید.")
            )
            return

        state["data"]["birth_date"] = text
        state["step"] = "ASTRO_TIME"
        await save_state(chat_id, state)

        await utils.send_message(
            BOT_TOKEN, chat_id,
            utils.escape_markdown_v2("⏰ لطفاً *ساعت تولد* را وارد کنید (مثلاً 14:25):"),
            keyboards.time_input_keyboard()
        )
        return

    # -------------------------------------------------------------------------
    # ورودی زمان تولد
    # -------------------------------------------------------------------------
    if step == "ASTRO_TIME":
        time_obj = utils.parse_persian_time(text)
        if not time_obj:
            await utils.send_message(
                BOT_TOKEN, chat_id,
                utils.escape_markdown_v2("❌ ساعت نامعتبر است. لطفاً به‌صورت HH:MM وارد کنید.")
            )
            return

        state["data"]["birth_time"] = text
        state["step"] = "ASTRO_CITY"
        await save_state(chat_id, state)

        await utils.send_message(
            BOT_TOKEN, chat_id,
            utils.escape_markdown_v2("📍 لطفاً *نام شهر تولد* را وارد کنید:")
        )
        return

    # -------------------------------------------------------------------------
    # ورودی شهر تولد
    # -------------------------------------------------------------------------
    if step == "ASTRO_CITY":
        city_info = utils.get_city_lookup_data(text)
        if not city_info:
            await utils.send_message(
                BOT_TOKEN, chat_id,
                utils.escape_markdown_v2("❌ شهر یافت نشد. لطفاً یک شهر معتبر وارد کنید.")
            )
            return

        state["data"]["city"] = text
        state["data"]["latitude"] = city_info["latitude"]
        state["data"]["longitude"] = city_info["longitude"]
        state["data"]["timezone"] = city_info["timezone"]

        state["step"] = "ASTRO_CALCULATE"
        await save_state(chat_id, state)

        await run_astrology_workflow(chat_id, state["data"])
        return


# =============================================================================
# مدیریت کلیک روی دکمه‌ها
# =============================================================================

async def handle_callback(callback: Dict[str, Any]):
    chat_id = callback["message"]["chat"]["id"]
    data = callback["data"]

    await utils.answer_callback_query(BOT_TOKEN, callback["id"])

    state = await get_state(chat_id)

    # -------------------------------------------------------------------------
    # منوی اصلی
    # -------------------------------------------------------------------------
    if data.startswith("MAIN|"):
        await utils.send_message(
            BOT_TOKEN, chat_id,
            utils.escape_markdown_v2("منوی اصلی:"),
            keyboards.main_menu_keyboard()
        )
        state["step"] = "WELCOME"
        await save_state(chat_id, state)
        return

    # -------------------------------------------------------------------------
    # خدمات → آسترولوژی
    # -------------------------------------------------------------------------
    if data == "SERVICES|ASTRO|0":
        await utils.send_message(
            BOT_TOKEN, chat_id,
            utils.escape_markdown_v2("لطفاً *تاریخ تولد* را وارد کنید (شمسی، YYYY/MM/DD):")
        )
        state["step"] = "ASTRO_DATE"
        await save_state(chat_id, state)
        return

    # -------------------------------------------------------------------------
    # انتخاب زمان پیش‌فرض
    # -------------------------------------------------------------------------
    if data.startswith("TIME|DEFAULT"):
        default_time = data.split("|")[2]
        state["data"]["birth_time"] = default_time
        state["step"] = "ASTRO_CITY"
        await save_state(chat_id, state)

        await utils.send_message(
            BOT_TOKEN, chat_id,
            utils.escape_markdown_v2("📍 لطفاً *نام شهر تولد* را وارد کنید:")
        )
        return


# =============================================================================
# اجرای کامل جریان آسترولوژی
# =============================================================================

async def run_astrology_workflow(chat_id: int, data: Dict[str, Any]):
    """
    ۱) محاسبه چارت
    ۲) تولید تفسیر
    ۳) رسم چارت
    ۴) ارسال خروجی به کاربر
    """

    await utils.send_message(
        BOT_TOKEN, chat_id,
        utils.escape_markdown_v2("🔄 در حال محاسبه چارت تولد شما... لطفاً صبر کنید.")
    )

    chart = calculate_natal_chart(
        birth_date_jalali=data["birth_date"],
        birth_time_str=data["birth_time"],
        latitude=data["latitude"],
        longitude=data["longitude"],
        timezone_str=data["timezone"],
        house_system="K"
    )

    if "error" in chart:
        await utils.send_message(
            BOT_TOKEN, chat_id,
            utils.escape_markdown_v2(f"❌ خطا در محاسبه چارت:\n{chart['error']}")
        )
        return

    # تفسیر
    interpretation = interpret_natal_chart(chart)

    # رسم چارت
    chart_image = draw_chart_wheel_fa(chart)

    # ارسال تصویر
    # 1) ارسال عکس بدون کپشن
    await utils.send_photo_with_caption(
    BOT_TOKEN, chat_id,
    chart_image,
    "",   # کپشن خالی
       None  # کیبورد هم بهتر است اینجا نباشد
     )

   # 2) ارسال تفسیر در پیام جداگانه
   await utils.send_message(
    BOT_TOKEN,
    chat_id,
    utils.escape_markdown_v2(interpretation),
    keyboards.main_menu_keyboard()
    )

    # بازگشت به منوی اصلی
    await utils.send_message(
        BOT_TOKEN, chat_id,
        utils.escape_markdown_v2("بازگشت به منوی اصلی:"),
        keyboards.main_menu_keyboard()
    )

    # ریست state
    await save_state(chat_id, {"step": "WELCOME", "data": {}})
