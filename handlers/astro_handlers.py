# astro_handlers.py - هندلر سرویس‌های آسترولوژی (نسخه نهایی و تصحیح شده)
import astrology_core
import astrology_interpretation 
import utils
import keyboards
from chart_drawer_fa import draw_chart_wheel_fa 
from persiantools.jdatetime import JalaliDateTime
from typing import Dict, Any, Optional
import logging 
import io 

# تنظیم لاگینگ
logging.basicConfig(level=logging.INFO)

async def handle_chart_calculation(chat_id: int, state: dict, save_user_state_func):
    """
    محاسبه چارت تولد، تولید تصویر چارت و سپس تولید تفسیر کامل با استفاده از داده‌های ذخیره‌شده.
    """
    state_data: Dict[str, Any] = state.get('data', {})
    
    # اصلاح: تعریف متغیرها در سطح بالا برای جلوگیری از UnboundLocalError در صورت وقوع خطا در میانه کد
    chart_result = None
    interpretation_text = ""
    msg = ""
    image_buffer: Optional[io.BytesIO] = None 

    try:
        logging.info(f"DEBUG: Chart Calculation Data for chat {chat_id}: {state_data}")
        
        # 1. بازیابی داده‌ها
        birth_date_str = state_data.get('birth_date') 
        birth_time = state_data.get('birth_time') 
        city_name = state_data.get('city_name')
        
        # تغییر: تبدیل صریح به float برای جلوگیری از خطای tuple index out of range در موتور نجومی
        # علت: گاهی مقادیر دیتابیس به صورت رشته ذخیره می‌شوند که باعث خطای محاسبات خانه‌ها می‌شود.
        latitude = float(state_data.get('latitude', 0))
        longitude = float(state_data.get('longitude', 0))
        timezone = state_data.get('timezone', 'Asia/Tehran')
        
        if not (birth_date_str and birth_time and city_name):
            msg = utils.escape_markdown_v2("❌ اطلاعات تولد کامل نیست. لطفاً تاریخ، ساعت و شهر را دوباره وارد کنید.")
            await utils.send_message(utils.BOT_TOKEN, chat_id, msg, keyboards.main_menu_keyboard())
            state['step'] = 'WELCOME' 
            await save_user_state_func(chat_id, state)
            return

        # 2. فراخوانی تابع محاسبه چارت (Core)
        chart_result = astrology_core.calculate_natal_chart(
            birth_date=birth_date_str, 
            birth_time=birth_time, 
            latitude=latitude, 
            longitude=longitude, 
            timezone_str=timezone
        )

        # 3. پردازش خروجی
        if chart_result and 'error' in chart_result:
            msg = utils.escape_markdown_v2(f"❌ *خطای سیستمی در محاسبه چارت*:\n`{chart_result['error']}`")
        
        elif chart_result:
            # 3.1. تولید تصویر چارت
            try:
                if isinstance(chart_result, dict):
                    chart_result['date'] = birth_date_str 
                    chart_result['time'] = birth_time 
                    chart_result['city'] = city_name
                
                image_buffer = draw_chart_wheel_fa(chart_result) 
            except Exception as draw_e:
                logging.error(f"FATAL: Chart drawing failed: {draw_e}")
            
            # 3.2. تولید تفسیر متنی
            try:
                interpretation_text = astrology_interpretation.interpret_natal_chart(chart_result)
                final_interpretation_message = f"✨ **تفسیر کامل چارت تولد**\n\n{interpretation_text}"
                msg = utils.escape_markdown_v2(final_interpretation_message)
            except Exception as interp_e:
                logging.error(f"FATAL: Interpretation failed: {interp_e}")
                msg = utils.escape_markdown_v2(f"✅ چارت با موفقیت محاسبه شد.")

        # 4. ارسال خروجی نهایی
        if image_buffer:
            caption_short = utils.escape_markdown_v2(f"✨ نمودار چارت تولد شما\nتاریخ: {birth_date_str}")
            await utils.send_photo_with_caption(utils.BOT_TOKEN, chat_id, photo=image_buffer, caption=caption_short)
        
        if msg:
             await utils.send_message(utils.BOT_TOKEN, chat_id, msg, keyboards.main_menu_keyboard())

    except Exception as e:
        error_msg = utils.escape_markdown_v2(f"❌ *خطای سیستمی بحرانی*:\n{e}")
        logging.critical(f"CRITICAL: Handler crashed: {e}", exc_info=True)
        await utils.send_message(utils.BOT_TOKEN, chat_id, error_msg, keyboards.main_menu_keyboard())

    state['step'] = 'WELCOME' 
    await save_user_state_func(chat_id, state)
