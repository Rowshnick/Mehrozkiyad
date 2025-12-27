# handlers/astro_handlers.py
import os
import io
import logging
from typing import Dict, Any, Optional

import astrology_core
import utils
import keyboards
from chart_drawer_fa import draw_chart_wheel_fa

BOT_TOKEN = os.environ.get("BOT_TOKEN")
logging.basicConfig(level=logging.INFO)

async def handle_chart_calculation(chat_id: int, state: dict, save_user_state_func):

    state.setdefault("data", {})
    data: Dict[str, Any] = state["data"]

    birth_date = data.get("birth_date")
    birth_time = data.get("birth_time")
    city = data.get("city_name")

    try:
        lat = float(data.get("latitude", 0))
        lon = float(data.get("longitude", 0))
    except (TypeError, ValueError):
        lat, lon = 0.0, 0.0

    tz = data.get("timezone", "Asia/Tehran")

    if not all([birth_date, birth_time, city]):
        await utils.send_message(
            BOT_TOKEN,
            chat_id,
            utils.escape_markdown_v2("❌ اطلاعات تولد ناقص است."),
            keyboards.main_menu_keyboard()
        )
        return

    chart = astrology_core.calculate_natal_chart(
        birth_date_jalali=birth_date,
        birth_time=birth_time,
        city_name=city,
        lat=lat,
        lon=lon,
        tz_name=tz
    )

    if "error" in chart:
        await utils.send_message(
            BOT_TOKEN,
            chat_id,
            utils.escape_markdown_v2(f"❌ خطا: {chart['error']}"),
            keyboards.main_menu_keyboard()
        )
        return

    text = (
        f"✨ *چارت تولد شما* ✨\n\n"
        f"📍 شهر: {city}\n"
        f"📅 تاریخ: {birth_date}\n"
        f"⏰ ساعت: {birth_time}\n"
        f"──────────────────\n"
    )

    for planet, pdata in chart["planets"].items():
        if "degree" in pdata:
            text += f"🔹 *{planet.title()}*: `{pdata['degree']}°`\n"
        else:
            text += f"🔹 *{planet.title()}*: ❌ خطا\n"

    image_buffer: Optional[io.BytesIO] = None
    try:
        image_buffer = draw_chart_wheel_fa(chart)
        await utils.send_photo_with_caption(
            BOT_TOKEN,
            chat_id,
            image_buffer,
            utils.escape_markdown_v2("📊 نمودار چارت تولد")
        )
    except Exception as e:
        logging.warning(f"Chart image skipped: {e}")
    finally:
        if image_buffer:
            image_buffer.close()

    await utils.send_message(
        BOT_TOKEN,
        chat_id,
        utils.escape_markdown_v2(text),
        keyboards.main_menu_keyboard()
    )

    state["step"] = "WELCOME"
    await save_user_state_func(chat_id, state)
