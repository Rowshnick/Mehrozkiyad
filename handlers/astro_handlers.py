# astro_handlers.py - هندلر سرویس‌های آسترولوژی (نسخه نهایی با اضافه شدن گرافیک)

import astrology_core
import astrology_interpretation # 💡 وارد کردن ماژول تفسیر
import utils
import keyboards
# 💥💥💥 ایمپورت ماژول ترسیم چارت (جدید) 💥💥💥
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
    
    try:
        logging.info(f"DEBUG: Chart Calculation Data for chat {chat_id}: {state_data}")
        
        # 1. بازیابی داده‌ها
        birth_date_str = state_data.get('birth_date') 
        birth_time = state_data.get('birth_time') 
        city_name = state_data.get('city_name')
        
        if not (birth_date_str and birth_time and city_name):
            # اگر داده‌ای گم شده بود، کاربر را به منوی اصلی برگردان
            msg = utils.escape_markdown_v2("❌ اطلاعات تولد کامل نیست. لطفاً تاریخ، ساعت و شهر را دوباره وارد کنید.")
            await utils.send_message(utils.BOT_TOKEN, chat_id, msg, keyboards.main_menu_keyboard())
            state['step'] = 'WELCOME' 
            await save_user_state_func(chat_id, state)
            return

        # 2. جستجوی مختصات شهر
        city_lookup_data = utils.get_city_lookup_data(city_name)
        if city_lookup_data is None:
            msg = utils.escape_markdown_v2("❌ شهر مورد نظر پیدا نشد.\nلطفاً نام شهر را دقیق‌تر وارد کنید.")
            await utils.send_message(utils.BOT_TOKEN, chat_id, msg, keyboards.main_menu_keyboard())
            state['step'] = 'WELCOME' 
            await save_user_state_func(chat_id, state)
            return
        
        latitude = city_lookup_data['latitude']
        longitude = city_lookup_data['longitude']
        timezone = city_lookup_data['timezone'] 
        
        chart_result = None
        interpretation_text = ""
        msg = ""

        # 3. فراخوانی تابع محاسبه چارت (Core)
        chart_result = astrology_core.calculate_natal_chart(
            birth_date_jalali=birth_date_str, 
            birth_time_str=birth_time, 
            city_name=city_name,
            latitude=float(latitude), 
            longitude=float(longitude), 
            timezone_str=timezone
        )

        
        # 4. پردازش و تولید خروجی (گرافیک و متن)
        
        if chart_result and 'error' in chart_result:
            # خطای کلی محاسبه
            msg = utils.escape_markdown_v2(f"❌ *خطای سیستمی در محاسبه چارت*:\n`{chart_result['error']}`")
        
        elif chart_result:
            
            # 💥💥💥 4.1. تولید تصویر چارت (گرافیک) 💥💥💥
            image_buffer: Optional[io.BytesIO] = None
            try:
                # فراخوانی تابع ترسیم چارت
                image_buffer = draw_chart_wheel_fa(chart_result) 
            except Exception as draw_e:
                logging.error(f"FATAL: Chart drawing failed: {draw_e}", exc_info=True)
            
            
            # 💥💥💥 4.2. تولید تفسیر متنی 💥💥💥
            try:
                interpretation_text = astrology_interpretation.interpret_natal_chart(chart_result)
                
                # ساختار نهایی پیام شامل اطلاعات اولیه و تفسیر کامل
                final_interpretation_message = (
                    f"✨ **تفسیر کامل چارت تولد**\n"
                    f"تاریخ: {birth_date_str}، زمان: {birth_time}\n"
                    f"شهر: {city_name}\n\n"
                    f"{interpretation_text}"
                )
                
                # اعمال Markdown Escaping
                msg = utils.escape_markdown_v2(final_interpretation_message)
                
            except Exception as interp_e:
                error_msg_interp = f"✅ محاسبه چارت موفق بود، اما خطایی در تولید تفسیر رخ داد: `{interp_e}`"
                logging.error(f"FATAL: Interpretation failed: {interp_e}", exc_info=True)
                msg = utils.escape_markdown_v2(error_msg_interp)

        
        # 5. ارسال خروجی نهایی به کاربر
        if image_buffer:
            
            # 5.1. ارسال عکس با یک کپشن کوتاه
            caption_short = utils.escape_markdown_v2(
                f"✨ **نمودار چارت تولد شما**\n"
                f"تاریخ: {birth_date_str}، زمان: {birth_time}"
            )
            
            await utils.send_photo_with_caption(
                utils.BOT_TOKEN, 
                chat_id, 
                photo=image_buffer, 
                caption=caption_short
            )
        
        # 5.2. ارسال تفسیر متنی کامل 
        if msg:
             await utils.send_message(
                utils.BOT_TOKEN, 
                chat_id, 
                msg, 
                keyboards.main_menu_keyboard()
             )
        elif not image_buffer:
             # اگر نه عکس و نه متن تفسیر ارسال شد (خطای بحرانی)
             await utils.send_message(
                utils.BOT_TOKEN, 
                chat_id, 
                utils.escape_markdown_v2("❌ *خطای سیستمی*: خروجی چارت و تفسیر خالی است."), 
                keyboards.main_menu_keyboard()
             )


    except Exception as e:
        # مدیریت خطاهای سیستمی که کل هندلر را متوقف کرده‌اند
        error_msg = utils.escape_markdown_v2(f"❌ *خطای سیستمی بحرانی*:\nربات ناگهان متوقف شد. لطفاً دوباره تلاش کنید.")
        logging.critical(f"CRITICAL: Handler crashed completely outside inner block: {e}", exc_info=True)
        
        await utils.send_message(utils.BOT_TOKEN, chat_id, error_msg, keyboards.main_menu_keyboard())

    # 6. به‌روزرسانی وضعیت در انتها
    state['step'] = 'WELCOME' 
    await save_user_state_func(chat_id, state)
