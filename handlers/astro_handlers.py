# ----------------------------------------------------------------------
# astro_handlers.py - هندلر سرویس‌های آسترولوژی (نسخه نهایی و هماهنگ با astrology_core)
# ----------------------------------------------------------------------

import astrology_core
import utils
import keyboards
from typing import Dict, Any

async def handle_chart_calculation(chat_id: int, state: dict, save_user_state_func):
    """
    محاسبه چارت تولد با استفاده از داده‌های ذخیره‌شده کاربر.
    """
    state_data: Dict[str, Any] = state.get('data', {})
    
    # 1. بازیابی داده‌ها
    birth_date_str = state_data.get('birth_date')
    birth_time = state_data.get('birth_time')
    city_name = state_data.get('city_name')
    latitude = state_data.get('latitude')
    longitude = state_data.get('longitude')
    timezone = state_data.get('timezone')

    # بررسی صحت داده‌ها
    if not (birth_date_str and birth_time and city_name and latitude is not None and longitude is not None and timezone):
        msg = utils.escape_markdown_v2("❌ اطلاعات تولد کامل نیست. لطفاً تاریخ، ساعت و شهر را دوباره وارد کنید.")
        await utils.send_message(utils.BOT_TOKEN, chat_id, msg, keyboards.main_menu_keyboard())
        state['step'] = 'WELCOME'
        await save_user_state_func(chat_id, state)
        return

    try:
        # 2. محاسبه چارت
        chart_result = astrology_core.calculate_natal_chart(
            birth_date_jalali=birth_date_str,
            birth_time_str=birth_time,
            city_name=city_name,
            latitude=latitude,
            longitude=longitude,
            timezone_str=timezone
        )

        # 3. پردازش خروجی
        msg = ""
        if chart_result and 'error' in chart_result:
            msg = utils.escape_markdown_v2(f"❌ *خطای سیستمی در محاسبه چارت*:\n`{chart_result['error']}`")
        elif chart_result and chart_result.get("status") == "ok":
            planets_info_lines = []
            planets = chart_result.get("planets", {})

            for p, data in planets.items():
                if "error" not in data and "longitude_deg" in data:
                    try:
                        lon = data.get("longitude_deg")
                        sign = data.get("sign", "نامشخص")
                        planets_info_lines.append(f"*{p.capitalize()}*: {lon:.2f}° در برج {sign}")
                    except Exception:
                        planets_info_lines.append(f"*{p.capitalize()}*: [خطای فرمت‌دهی]")
                else:
                    planets_info_lines.append(f"*{p.capitalize()}*: {data.get('error', '❌ داده نامعتبر')}")

            planets_info = "\n".join(planets_info_lines)

            msg = utils.escape_markdown_v2(
                f"✨ **چارت تولد شما**\n"
                f"تاریخ: {birth_date_str}، زمان: {birth_time}\n"
                f"شهر: {city_name}\n\n"
                f"**موقعیت سیارات:**\n{planets_info}"
            )
        else:
            msg = utils.escape_markdown_v2("❌ *خطای نامشخص*: نتیجه محاسبه چارت خالی است.")

        # 4. ارسال پیام
        if msg:
            await utils.send_message(utils.BOT_TOKEN, chat_id, msg, keyboards.main_menu_keyboard())

    except Exception as e:
        error_msg = utils.escape_markdown_v2(f"❌ *خطای غیرمنتظره در هندلر چارت*:\n`{e}`")
        await utils.send_message(utils.BOT_TOKEN, chat_id, error_msg, keyboards.main_menu_keyboard())

    # 5. به‌روزرسانی وضعیت
    state['step'] = 'WELCOME'
    await save_user_state_func(chat_id, state)
