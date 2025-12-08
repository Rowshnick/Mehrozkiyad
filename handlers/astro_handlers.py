# ----------------------------------------------------------------------
# astro_handlers.py - هندلر سرویس‌های آسترولوژی (تصحیح نهایی)
# ----------------------------------------------------------------------

import astrology_core
import utils
import keyboards
from persiantools.jdatetime import JalaliDateTime
from typing import Dict, Any

async def handle_chart_calculation(chat_id: int, state: dict, save_user_state_func):
    
    state_data: Dict[str, Any] = state.get('data', {})
    
    # ... (اعتبارسنجی ورودی‌ها بدون تغییر)

    # 💥 FIX NAME ERROR: تعریف متغیر نتیجه با مقدار پیش‌فرض قبل از try
    chart_result = None # یا {}

    # --- 2. فراخوانی تابع محاسبه چارت ---
    try:
        chart_result = astrology_core.calculate_natal_chart(
            birth_date_jalali=birth_date_str,
            birth_time_str=birth_time, 
            city_name=city_name,
            latitude=latitude,
            longitude=longitude,
            timezone_str=timezone
        )

        # --- 3. پردازش و ارسال نتیجه ---
        # اکنون chart_result حتماً تعریف شده است (یا None، یا نتیجه محاسبه)
        
        # 💡 اطمینان از تعریف chart_result قبل از استفاده
        if chart_result and 'error' in chart_result:
            msg = utils.escape_markdown_v2(f"❌ *خطای سیستمی در محاسبه چارت*:\n`{chart_result['error']}`")
        elif chart_result:
            # ایجاد یک گزارش ساده از موقعیت سیارات
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
            
            await utils.send_message(
                utils.BOT_TOKEN, 
                chat_id, 
                msg, 
                keyboards.main_menu_keyboard()
            )

    except Exception as e:
        # در صورت بروز خطای غیرمنتظره در حین اجرای تابع calculate_natal_chart
        error_msg = utils.escape_markdown_v2(f"❌ *خطای غیرمنتظره در هندلر چارت*:\n`{e}`")
        await utils.send_message(utils.BOT_TOKEN, chat_id, error_msg, keyboards.main_menu_keyboard())

    # --- 4. به‌روزرسانی وضعیت (این بخش باید همیشه اجرا شود) ---
    state['step'] = 'WELCOME' 
    await save_user_state_func(chat_id, state)
