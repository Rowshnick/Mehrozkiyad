# ----------------------------------------------------------------------
# astro_handlers.py - هندلر سرویس‌های آسترولوژی (نسخه نهایی و کاملاً دفاعی)
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
    
    # 1. تعریف متغیرها و بازیابی از وضعیت (اطمینان از وجود متغیر birth_time)
    birth_date_str = state_data.get('birth_date') 
    birth_time = state_data.get('birth_time') 
    city_name = state_data.get('city_name')
    latitude = state_data.get('latitude')
    longitude = state_data.get('longitude')
    timezone = state_data.get('timezone')

    # بررسی صحت تمام داده‌های ضروری (birth_time نیز اکنون ضروری است)
    if not (birth_date_str and birth_time and city_name and latitude is not None and longitude is not None and timezone):
        # ❌ اگر هر کدام از مقادیر None یا رشته خالی باشند
        msg = utils.escape_markdown_v2("❌ اطلاعات تولد کامل نیست. لطفاً دوباره از منوی اصلی شروع کنید.")
        await utils.send_message(
            utils.BOT_TOKEN, 
            chat_id, 
            msg,
            keyboards.main_menu_keyboard()
        )
        state['step'] = 'WELCOME' 
        await save_user_state_func(chat_id, state)
        return

    chart_result = None 

    # 2. فراخوانی تابع محاسبه چارت
    try:
        chart_result = astrology_core.calculate_natal_chart(
            birth_date_jalali=birth_date_str, 
            birth_time_str=birth_time, # استفاده از متغیر ساعت جدید
            city_name=city_name,
            latitude=latitude,
            longitude=longitude,
            timezone_str=timezone
        )

        # 3. پردازش و ارسال نتیجه
        msg = ""
        
        if chart_result and 'error' in chart_result:
            msg = utils.escape_markdown_v2(f"❌ *خطای سیستمی در محاسبه چارت*:\n`{chart_result['error']}`")
        elif chart_result:
            
            # حلقه کاملاً دفاعی: تولید گزارش سیارات با مدیریت خطاهای فرمت‌دهی
            planets_info_lines = []
            for p, data in chart_result.items():
                if 'error' not in data and 'degree' in data and 'status' in data:
                    degree_value = data.get('degree') 
                    status_value = data.get('status', 'Unknown')
                    
                    try:
                        # تلاش برای فرمت‌دهی امن
                        if isinstance(degree_value, (int, float)):
                            planets_info_lines.append(
                                f"*{p.capitalize()}*: {degree_value:.2f}° ({status_value})"
                            )
                        else:
                            planets_info_lines.append(
                                f"*{p.capitalize()}*: [درجه نامعتبر] ({status_value})"
                            )
                            
                    except Exception:
                        planets_info_lines.append(
                            f"*{p.capitalize()}*: [خطای فرمت‌دهی درجه] ({status_value})"
                        )
                        
            planets_info = "\n".join(planets_info_lines)

            # ساختار نهایی پیام
            msg = utils.escape_markdown_v2(
                f"✨ **چارت تولد شما**\n"
                f"تاریخ: {birth_date_str}، زمان: {birth_time}\n"
                f"شهر: {city_name}\n\n"
                f"**موقعیت سیارات:**\n{planets_info}"
            )
        else:
             msg = utils.escape_markdown_v2("❌ *خطای نامشخص*: نتیجه محاسبه چارت خالی است.")

        # ارسال پیام نهایی
        if msg:
            await utils.send_message(
                utils.BOT_TOKEN, 
                chat_id, 
                msg, 
                keyboards.main_menu_keyboard()
            )

    except Exception as e:
        # مدیریت خطاهای بسیار غیرمنتظره
        error_msg = utils.escape_markdown_v2(f"❌ *خطای غیرمنتظره در هندلر چارت*:\n`{e}`")
        await utils.send_message(utils.BOT_TOKEN, chat_id, error_msg, keyboards.main_menu_keyboard())

    # 4. به‌روزرسانی وضعیت (این بخش باید همیشه اجرا شود)
    state['step'] = 'WELCOME' 
    await save_user_state_func(chat_id, state)
