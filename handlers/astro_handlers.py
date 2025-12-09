# ----------------------------------------------------------------------
# astro_handlers.py - نسخه نهایی، پایدار و اصلاح‌شده
# ----------------------------------------------------------------------

import astrology_core
import utils
import keyboards
from typing import Dict, Any


async def handle_chart_calculation(chat_id: int, state: dict, save_user_state_func):
    state_data: Dict[str, Any] = state.get("data", {})

    birth_date_str = state_data.get("birth_date")
    birth_time = state_data.get("birth_time")
    city_name = state_data.get("city_name")
    latitude = state_data.get("latitude")
    longitude = state_data.get("longitude")
    timezone = state_data.get("timezone")

    # بررسی داده‌های ضروری
    if not (birth_date_str and birth_time and city_name and latitude is not None and longitude is not None and timezone):
        msg = utils.escape_markdown_v2("❌ اطلاعات تولد کامل نیست. دوباره وارد کنید.")
        await utils.send_message(utils.BOT_TOKEN, chat_id, msg, keyboards.main_menu_keyboard())
        state["step"] = "WELCOME"
        await save_user_state_func(chat_id, state)
        return

    try:
        chart_result = astrology_core.calculate_natal_chart(
            birth_date_jalali=birth_date_str,
            birth_time_str=birth_time,
            city_name=city_name,
            latitude=latitude,
            longitude=longitude,
            timezone_str=timezone
        )

        if chart_result and "error" in chart_result:
            err = utils.escape_markdown_v2(chart_result["error"])
            msg = f"❌ *خطا در محاسبه چارت*: \n{err}"
            await utils.send_message(utils.BOT_TOKEN, chat_id, msg, keyboards.main_menu_keyboard())
            return

        # ---------------------------------------------------------
        # ساخت خروجی سیارات
        # ---------------------------------------------------------
        planet_lines = []
        for p, data in chart_result.items():
            if "error" in data:
                planet_lines.append(f"{p.capitalize()}: خطا")
                continue

            deg = data.get("degree")
            if isinstance(deg, (int, float)):
                line = f"{p.capitalize()}: {deg:.2f}°"
            else:
                line = f"{p.capitalize()}: داده نامعتبر"

            planet_lines.append(line)

        planets_raw = "\n".join(planet_lines)
        planets_safe = utils.escape_markdown_v2(planets_raw)

        # Escape روی موارد ساده
        safe_date = utils.escape_markdown_v2(birth_date_str)
        safe_time = utils.escape_markdown_v2(birth_time)
        safe_city = utils.escape_markdown_v2(city_name)

        # پیام نهایی (بدون escape کلی)
        msg = (
            "✨ \\*\\*چارت تولد شما\\*\\*\n"
            f"تاریخ: {safe_date}، زمان: {safe_time}\n"
            f"شهر: {safe_city}\n\n"
            "\\*\\*موقعیت سیارات:\\*\\*\n"
            f"{planets_safe}"
        )

        await utils.send_message(utils.BOT_TOKEN, chat_id, msg, keyboards.main_menu_keyboard())

    except Exception as e:
        error_safe = utils.escape_markdown_v2(str(e))
        await utils.send_message(utils.BOT_TOKEN, chat_id, f"❌ خطای غیرمنتظره:\n{error_safe}",
                                 keyboards.main_menu_keyboard())

    state["step"] = "WELCOME"
    await save_user_state_func(chat_id, state)


