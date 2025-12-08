# ----------------------------------------------------------------------
# astro_handlers.py - هندلر سرویس‌های آسترولوژی (تصحیح نهایی)
# ----------------------------------------------------------------------

import astrology_core
import utils
import keyboards
from persiantools.jdatetime import JalaliDateTime
from typing import Dict, Any

async def handle_chart_calculation(chat_id: int, state: dict, save_user_state_func):
    """
    محاسبه چارت تولد با استفاده از داده‌های ذخیره‌شده کاربر.
    """
    state_data: Dict[str, Any] = state.get('data', {})
    
    # --- 1. اعتبارسنجی و تعریف متغیرها (این بخش باید در ابتدای تابع باشد) ---
    # 💥 FIX CRITICAL: اطمینان از تعریف متغیرها در بالاترین سطح تابع برای رفع NameError
    birth_date_str = state_data.get('birth_date') 
    birth_time = state_data.get('birth_time', '12:00') 
    city_name = state_data.get('city_name')
    latitude = state_data.get('latitude')
    longitude = state_data.get('longitude')
    timezone = state_data.get('timezone')

    # بررسی صحت تمام داده‌های ضروری
    if not (birth_date_str and city_name and latitude is not None and longitude is not None and timezone):
        # ❌ اگر هر کدام از مقادیر None یا رشته خالی باشند
        await utils.send_message(
            utils.BOT_TOKEN, 
            chat_id, 
            utils.escape_markdown_v2("❌ اطلاعات تولد کامل نیست. لطفاً دوباره از منوی اصلی شروع کنید."),
            keyboards.main_menu_keyboard()
        )
        # 💡 به‌روزرسانی وضعیت در این حالت
        state['step'] = 'WELCOME' 
        await save_user_state_func(chat_id, state)
        return

    # 💡 مقداردهی اولیه برای جلوگیری از NameError در بلوک except
    chart_result = None 

    # --- 2. فراخوانی تابع محاسبه چارت ---
    try:
        # 💥 FIX: astrology_core اکنون دیکشنری خطا را برمی‌گرداند، نه Exception
        chart_result = astrology_core.calculate_natal_chart(
            birth_date_jalali=birth_date_str, 
            birth_time_str=birth_time, 
            city_name=city_name,
            latitude=latitude,
            longitude=longitude,
            timezone_str=timezone
        )

        # --- 3. پردازش و ارسال نتیجه ---
        msg = ""
        
        # 💡 مدیریت خطای برگشتی از calculate_natal_chart
        if chart_result and 'error' in chart_result:
            msg = utils.escape_markdown_v2(f"❌ *خطای سیستمی در محاسبه چارت*:\n`{chart_result['error']}`")
        elif chart_result:
            planets_info = "\n".join([
                f"*{p.capitalize()}*: {data.get('degree'):.2f}° ({data.get('status')})" 
                for p, data in chart_result.items() if 'error' not in data
            ])
            msg = utils.escape_markdown_v2(
                f"✨ **چارت تولد شما**\n"
                f"تاریخ: {birth_date_str}، زمان: {birth_time}\n"
                f"شهر: {city_name}\n\n"
                f"**موقعیت سیارات:**\n{planets_info}"
            )
        else:
             msg = utils.escape_markdown_v2("❌ *خطای نامشخص*: نتیجه محاسبه چارت خالی است.")

        await utils.send_message(
            utils.BOT_TOKEN, 
            chat_id, 
            msg, 
            keyboards.main_menu_keyboard()
        )

    except Exception as e:
        # این بلوک فقط خطاهای بسیار غیرمنتظره را مدیریت می‌کند
        error_msg = utils.escape_markdown_v2(f"❌ *خطای غیرمنتظره در هندلر چارت*:\n`{e}`")
        await utils.send_message(utils.BOT_TOKEN, chat_id, error_msg, keyboards.main_menu_keyboard())

    # --- 4. به‌روزرسانی وضعیت (این بخش باید همیشه اجرا شود) ---
    state['step'] = 'WELCOME' 
    await save_user_state_func(chat_id, state)
