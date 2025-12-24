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
        
        # اصلاح: استفاده از کلیدهای مستقیم موجود در استیت برای اطمینان از عدم مقدار Null
        latitude = state_data.get('latitude')
        longitude = state_data.get('longitude')
        timezone = state_data.get('timezone')
        
        if not (birth_date_str and birth_time and city_name and latitude):
            msg = utils.escape_markdown_v2("❌ اطلاعات تولد کامل نیست. لطفاً تاریخ، ساعت و شهر را دوباره وارد کنید.")
            await utils.send_message(utils.BOT_TOKEN, chat_id, msg, keyboards.main_menu_keyboard())
            state['step'] = 'WELCOME' 
            await save_user_state_func(chat_id, state)
            return

        # 2. فراخوانی تابع محاسبه چارت (Core)
        # تغییر: اطمینان از فلوت بودن مختصات قبل از ارسال به هسته
        chart_result = astrology_core.calculate_natal_chart(
            birth_date=birth_date_str, 
            birth_time=birth_time, 
            latitude=float(latitude), 
            longitude=float(longitude), 
            timezone_str=timezone
        )

        # 4. پردازش و تولید خروجی
        if chart_result and 'error' in chart_result:
            msg = utils.escape_markdown_v2(f"❌ *خطای سیستمی در محاسبه چارت*:\n`{chart_result['error']}`")
        
        elif chart_result:
            # 4.1. تولید تصویر چارت
            try:
                if isinstance(chart_result, dict):
                    chart_result['date'] = birth_date_str 
                    chart_result['time'] = birth_time 
                    chart_result['city'] = city_name
                
                image_buffer = draw_chart_wheel_fa(chart_result) 
            except Exception as draw_e:
                logging.error(f"FATAL: Chart drawing failed: {draw_e}", exc_info=True)
                # تغییر: کد حذف نشد، فقط در صورت بروز خطا لاگ می‌شود تا برنامه متوقف نشود.
            
            # 4.2. تولید تفسیر متنی
            try:
                interpretation_text = astrology_interpretation.interpret_natal_chart(chart_result)
                final_interpretation_message = (
                    f"✨ **تفسیر کامل چارت تولد**\n"
                    f"تاریخ: {birth_date_str}، زمان: {birth_time}\n"
                    f"شهر: {city_name}\n\n"
                    f"{interpretation_text}"
                )
                msg = utils.escape_markdown_v2(final_interpretation_message)
            except Exception as interp_e:
                logging.error(f"FATAL: Interpretation failed: {interp_e}", exc_info=True)
                msg = utils.escape_markdown_v2(f"✅ چارت محاسبه شد اما در تفسیر خطایی رخ داد.")

        # 5. ارسال خروجی نهایی
        if image_buffer:
            caption_short = utils.escape_markdown_v2(f"✨ **نمودار چارت تولد شما**\nتاریخ: {birth_date_str}")
            await utils.send_photo_with_caption(utils.BOT_TOKEN, chat_id, photo=image_buffer, caption=caption_short)
        
        if msg:
             await utils.send_message(utils.BOT_TOKEN, chat_id, msg, keyboards.main_menu_keyboard())

    except Exception as e:
        error_msg = utils.escape_markdown_v2(f"❌ *خطای سیستمی بحرانی*:\n{e}")
        logging.critical(f"CRITICAL: Handler crashed: {e}", exc_info=True)
        await utils.send_message(utils.BOT_TOKEN, chat_id, error_msg, keyboards.main_menu_keyboard())

    state['step'] = 'WELCOME' 
    await save_user_state_func(chat_id, state)
