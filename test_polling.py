# test_polling.py
# =============================================================================
# نسخه‌ی تستی ربات تلگرام با Polling (بدون Webhook)
# مناسب برای Google Colab یا اجرای محلی
# =============================================================================

import os
import logging
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)

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

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN در محیط تنظیم نشده است.")


# =============================================================================
# توابع کمکی State Machine
# =============================================================================

async def get_state(chat_id):
    return await get_user_state_db(chat_id)

async def save_state(chat_id, state):
    await save_user_state_db(chat_id, state)


# =============================================================================
# مدیریت پیام‌های متنی
# =============================================================================

async def handle_message(update, context):
    message = update.message
    chat_id = message.chat_id
    text = message.text.strip()

    state = await get_state(chat_id)
    step = state.get("step", "START")

    # -------------------------------------------------------------------------
    # شروع ربات
    # -------------------------------------------------------------------------
    if step == "START":
        await message.reply_text(
            "سلام! برای شروع یکی از گزینه‌های زیر را انتخاب کنید:",
            reply_markup=keyboards.main_menu_keyboard()
        )
        state["step"] = "WELCOME"
        await save_state(chat_id, state)
        return

    # -------------------------------------------------------------------------
    # ورودی تاریخ تولد
    # -------------------------------------------------------------------------
    if step == "ASTRO_DATE":
        date_obj = utils.parse_persian_date(text)
        if not date_obj:
            await message.reply_text("❌ تاریخ نامعتبر است. لطفاً به‌صورت YYYY/MM/DD وارد کنید.")
            return

        state["data"]["birth_date"] = text
        state["step"] = "ASTRO_TIME"
        await save_state(chat_id, state)

        await message.reply_text(
            "⏰ لطفاً *ساعت تولد* را وارد کنید (مثلاً 14:25):",
            reply_markup=keyboards.time_input_keyboard()
        )
        return

    # -------------------------------------------------------------------------
    # ورودی زمان تولد
    # -------------------------------------------------------------------------
    if step == "ASTRO_TIME":
        time_obj = utils.parse_persian_time(text)
        if not time_obj:
            await message.reply_text("❌ ساعت نامعتبر است. لطفاً به‌صورت HH:MM وارد کنید.")
            return

        state["data"]["birth_time"] = text
        state["step"] = "ASTRO_CITY"
        await save_state(chat_id, state)

        await message.reply_text("📍 لطفاً *نام شهر تولد* را وارد کنید:")
        return

    # -------------------------------------------------------------------------
    # ورودی شهر تولد
    # -------------------------------------------------------------------------
    if step == "ASTRO_CITY":
        city_info = utils.get_city_lookup_data(text)
        if not city_info:
            await message.reply_text("❌ شهر یافت نشد. لطفاً یک شهر معتبر وارد کنید.")
            return

        state["data"]["city"] = text
        state["data"]["latitude"] = city_info["latitude"]
        state["data"]["longitude"] = city_info["longitude"]
        state["data"]["timezone"] = city_info["timezone"]

        state["step"] = "ASTRO_CALCULATE"
        await save_state(chat_id, state)

        await run_astrology_workflow(chat_id, state["data"], context)
        return


# =============================================================================
# مدیریت کلیک روی دکمه‌ها
# =============================================================================

async def handle_callback(update, context):
    callback = update.callback_query
    chat_id = callback.message.chat_id
    data = callback.data

    await callback.answer()

    state = await get_state(chat_id)

    # -------------------------------------------------------------------------
    # منوی اصلی
    # -------------------------------------------------------------------------
    if data.startswith("MAIN|"):
        await callback.message.reply_text(
            "منوی اصلی:",
            reply_markup=keyboards.main_menu_keyboard()
        )
        state["step"] = "WELCOME"
        await save_state(chat_id, state)
        return

    # -------------------------------------------------------------------------
    # خدمات → آسترولوژی
    # -------------------------------------------------------------------------
    if data == "SERVICES|ASTRO|0":
        state["step"] = "ASTRO_DATE"
        state["data"] = {}
        await save_state(chat_id, state)

        await callback.message.reply_text("لطفاً *تاریخ تولد* را وارد کنید (شمسی، YYYY/MM/DD):")
        return

    # -------------------------------------------------------------------------
    # انتخاب زمان پیش‌فرض
    # -------------------------------------------------------------------------
    if data.startswith("TIME|DEFAULT"):
        default_time = data.split("|")[2]
        state["data"]["birth_time"] = default_time
        state["step"] = "ASTRO_CITY"
        await save_state(chat_id, state)

        await callback.message.reply_text("📍 لطفاً *نام شهر تولد* را وارد کنید:")
        return


# =============================================================================
# اجرای کامل جریان آسترولوژی
# =============================================================================

async def run_astrology_workflow(chat_id, data, context):
    await context.bot.send_message(chat_id, "🔄 در حال محاسبه چارت تولد شما... لطفاً صبر کنید.")

    chart = calculate_natal_chart(
        birth_date_jalali=data["birth_date"],
        birth_time_str=data["birth_time"],
        latitude=data["latitude"],
        longitude=data["longitude"],
        timezone_str=data["timezone"],
        house_system="K"
    )

    if "error" in chart:
        await context.bot.send_message(chat_id, f"❌ خطا در محاسبه چارت:\n{chart['error']}")
        return

    interpretation = interpret_natal_chart(chart)
    chart_image = draw_chart_wheel_fa(chart)

    await context.bot.send_photo(chat_id, chart_image, caption=interpretation)

    await context.bot.send_message(
        chat_id,
        "بازگشت به منوی اصلی:",
        reply_markup=keyboards.main_menu_keyboard()
    )

    await save_state(chat_id, {"step": "WELCOME", "data": {}})


# =============================================================================
# اجرای Polling
# =============================================================================

async def main():
    await init_db()

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_callback))

    print("🤖 ربات در حالت Polling فعال شد...")
    await app.run_polling()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
