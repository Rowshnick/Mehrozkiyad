# test_polling.py — نسخه مخصوص Google Colab

import os
import logging
from telegram.ext import (
    Application,
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


logging.basicConfig(level=logging.INFO)
BOT_TOKEN = os.environ.get("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN تنظیم نشده است.")


async def get_state(chat_id):
    return await get_user_state_db(chat_id)

async def save_state(chat_id, state):
    await save_user_state_db(chat_id, state)


async def handle_message(update, context):
    message = update.message
    chat_id = message.chat_id
    text = message.text.strip()

    state = await get_state(chat_id)
    step = state.get("step", "START")

    if step == "START":
        await message.reply_text(
            "سلام! برای شروع یکی از گزینه‌های زیر را انتخاب کنید:",
            reply_markup=keyboards.main_menu_keyboard()
        )
        state["step"] = "WELCOME"
        await save_state(chat_id, state)
        return

    if step == "ASTRO_DATE":
        date_obj = utils.parse_persian_date(text)
        if not date_obj:
            await message.reply_text("❌ تاریخ نامعتبر است.")
            return

        state["data"]["birth_date"] = text
        state["step"] = "ASTRO_TIME"
        await save_state(chat_id, state)

        await message.reply_text(
            "⏰ لطفاً ساعت تولد را وارد کنید:",
            reply_markup=keyboards.time_input_keyboard()
        )
        return

    if step == "ASTRO_TIME":
        time_obj = utils.parse_persian_time(text)
        if not time_obj:
            await message.reply_text("❌ ساعت نامعتبر است.")
            return

        state["data"]["birth_time"] = text
        state["step"] = "ASTRO_CITY"
        await save_state(chat_id, state)

        await message.reply_text("📍 لطفاً نام شهر تولد را وارد کنید:")
        return

    if step == "ASTRO_CITY":
        city_info = utils.get_city_lookup_data(text)
        if not city_info:
            await message.reply_text("❌ شهر یافت نشد.")
            return

        state["data"]["city"] = text
        state["data"]["latitude"] = city_info["latitude"]
        state["data"]["longitude"] = city_info["longitude"]
        state["data"]["timezone"] = city_info["timezone"]

        state["step"] = "ASTRO_CALCULATE"
        await save_state(chat_id, state)

        await run_astrology_workflow(chat_id, state["data"], context)
        return


async def handle_callback(update, context):
    callback = update.callback_query
    chat_id = callback.message.chat_id
    data = callback.data

    await callback.answer()

    state = await get_state(chat_id)

    if data.startswith("MAIN|"):
        await callback.message.reply_text(
            "منوی اصلی:",
            reply_markup=keyboards.main_menu_keyboard()
        )
        state["step"] = "WELCOME"
        await save_state(chat_id, state)
        return

    if data == "SERVICES|ASTRO|0":
        state["step"] = "ASTRO_DATE"
        state["data"] = {}
        await save_state(chat_id, state)

        await callback.message.reply_text("لطفاً تاریخ تولد را وارد کنید:")
        return

    if data.startswith("TIME|DEFAULT"):
        default_time = data.split("|")[2]
        state["data"]["birth_time"] = default_time
        state["step"] = "ASTRO_CITY"
        await save_state(chat_id, state)

        await callback.message.reply_text("📍 لطفاً نام شهر تولد را وارد کنید:")
        return


async def run_astrology_workflow(chat_id, data, context):
    await context.bot.send_message(chat_id, "🔄 در حال محاسبه چارت...")

    chart = calculate_natal_chart(
        birth_date_jalali=data["birth_date"],
        birth_time_str=data["birth_time"],
        latitude=data["latitude"],
        longitude=data["longitude"],
        timezone_str=data["timezone"],
        house_system="K"
    )

    if "error" in chart:
        await context.bot.send_message(chat_id, f"❌ خطا:\n{chart['error']}")
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


# نسخه مخصوص Colab — بدون asyncio.run()
async def start_polling():
    await init_db()

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_callback))

    print("🤖 ربات در حالت Polling فعال شد (Colab-safe)...")
    await app.run_polling(close_loop=False)


import nest_asyncio
nest_asyncio.apply()

import asyncio
asyncio.get_event_loop().create_task(start_polling())
