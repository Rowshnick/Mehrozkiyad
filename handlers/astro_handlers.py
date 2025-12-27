# astro_handlers.py - نسخه اصلاح شده برای پایداری در Railway و مدیریت حافظه
import astrology_core
import astrology_interpretation 
import utils
import keyboards
from chart_drawer_fa import draw_chart_wheel_fa 
from typing import Dict, Any, Optional
import logging 
import io 

logging.basicConfig(level=logging.INFO)

async def handle_chart_calculation(chat_id: int, state: dict, save_user_state_func):
    state_data: Dict[str, Any] = state.get('data', {})
    chart_result = None
    msg = ""
    image_buffer: Optional[io.BytesIO] = None 

    try:
        logging.info(f"DEBUG: شروع محاسبه چارت برای کاربر {chat_id}")
        
        # 1. بازیابی و تبدیل امن داده‌ها
        birth_date_str = state_data.get('birth_date') 
        birth_time = state_data.get('birth_time') 
        city_name = state_data.get('city_name')
        
        # تبدیل امن به عدد اعشاری برای جلوگیری از کرش
        try:
            latitude = float(state_data.get('latitude') or 0.0)
            longitude = float(state_data.get('longitude') or 0.0)
        except (ValueError, TypeError):
            logging.error("خطا در تبدیل مختصات")
            latitude, longitude = 0.0, 0.0

        timezone = state_data.get('timezone', 'Asia/Tehran')
        
        if not (birth_date_str and birth_time and city_name):
            msg = utils.escape_markdown_v2("❌ اطلاعات تولد (تاریخ، ساعت یا شهر) کامل نیست.")
            await utils.send_message(utils.BOT_TOKEN, chat_id, msg, keyboards.main_menu_keyboard())
            return

        # 2. فراخوانی تابع محاسبه چارت (Core)
        logging.info(f"DEBUG: فراخوانی هسته نجومی برای ساعت {birth_time}")
        chart_result = astrology_core.calculate_natal_chart(
            birth_date=birth_date_str, 
            birth_time=birth_time, 
            latitude=latitude, 
            longitude=longitude, 
            timezone_str=timezone
        )

        # 3. پردازش و تولید خروجی
        if chart_result and 'error' in chart_result:
            msg = utils.escape_markdown_v2(f"❌ خطای محاسبه: {chart_result['error']}")
        
        elif chart_result:
            logging.info("DEBUG: محاسبه با موفقیت انجام شد. در حال تولید خروجی...")
            
            # الف) تولید تصویر چارت (بخش حساس به رم)
            try:
                chart_result.update({'date': birth_date_str, 'time': birth_time, 'city': city_name})
                image_buffer = draw_chart_wheel_fa(chart_result) 
            except Exception as draw_e:
                logging.error(f"خطا در ترسیم گرافیکی: {draw_e}")

            # ب) تولید متن گزارش جزئیات
            # استفاده از نام‌های فارسی سیارات اگر در هسته تعریف شده باشند
            report_text = (
                f"✨ *چارت تولد شما آماده شد* ✨\n\n"
                f"📍 مکان: {city_name}\n"
                f"🌅 *طالع (Asc):* {chart_result['ascendant']:.2f}°\n"
                f"──────────────────\n"
            )

            for p in chart_result['planets']:
                retro = " ℞ (برگشتی)" if p.get('retrograde') else ""
                report_text += (
                    f"🔹 *{p['name']}*:\n"
                    f"   ▫️ موقعیت: {p['sign_degree']:.2f}° {p['sign']}{retro}\n"
                    f"   ▫️ عرض جغرافیایی: {p.get('latitude', 0):.2f}°\n"
                    f"   ▫️ در {p['house_name']}\n\n"
                )

            # ج) دریافت تفسیر
            try:
                interpretation = astrology_interpretation.interpret_natal_chart(chart_result)
                if interpretation:
                    report_text += f"──────────────────\n🔍 *تفسیر کوتاه:*\n{interpretation}"
            except Exception as int_e:
                logging.warning(f"Interpretation skipped: {int_e}")

            msg = utils.escape_markdown_v2(report_text)

        # 4. ارسال نهایی
        if image_buffer:
            caption = utils.escape_markdown_v2(f"✨ نمودار چارت تولد\n📅 {birth_date_str}")
            await utils.send_photo_with_caption(utils.BOT_TOKEN, chat_id, photo=image_buffer, caption=caption)
            # آزادسازی حافظه رم بلافاصله بعد از ارسال (بسیار مهم برای Railway)
            image_buffer.close()
            logging.info("DEBUG: تصویر ارسال و حافظه آزاد شد.")
        
        if msg:
             await utils.send_message(utils.BOT_TOKEN, chat_id, msg, keyboards.main_menu_keyboard())

    except Exception as e:
        logging.critical(f"Handler crashed: {e}", exc_info=True)
        error_msg = utils.escape_markdown_v2("❌ متاسفانه در پردازش نهایی چارت خطایی رخ داد.")
        await utils.send_message(utils.BOT_TOKEN, chat_id, error_msg, keyboards.main_menu_keyboard())

    # بازگشت به منوی اصلی
    state['step'] = 'WELCOME' 
    await save_user_state_func(chat_id, state)
