# ----------------------------------------------------------------------
# astro_handlers.py - هندلر سرویس‌های آسترولوژی (نسخه نهایی با تفسیر)
# ----------------------------------------------------------------------

import astrology_core
import astrology_interpretation # 💡 وارد کردن ماژول تفسیر جدید
import utils
import keyboards
from persiantools.jdatetime import JalaliDateTime
from typing import Dict, Any
import logging 

# تنظیم لاگینگ
logging.basicConfig(level=logging.INFO)


async def handle_chart_calculation(chat_id: int, state: dict, save_user_state_func):
    """
    محاسبه چارت تولد و سپس تولید تفسیر کامل با استفاده از داده‌های ذخیره‌شده.
    """
    state_data: Dict[str, Any] = state.get('data', {})
    
    try:
        logging.info(f"DEBUG: Chart Calculation Data for chat {chat_id}: {state_data}")
        
        # 1. بازیابی داده‌های اصلی از وضعیت 
        birth_date_str = state_data.get('birth_date') 
        birth_time = state_data.get('birth_time') 
        city_name = state_data.get('city_name')
        
        # بررسی صحت تمام داده‌های ضروری
        if not (birth_date_str and birth_time and city_name):
            logging.error(f"FATAL: Missing mandatory Chart Data: Date={birth_date_str}, Time={birth_time}, City={city_name}")
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
        
        # استخراج مختصات
        latitude = city_lookup_data['latitude']
        longitude = city_lookup_data['longitude']
        timezone = city_lookup_data['timezone'] 
        
        
        chart_result = None

        # 3. فراخوانی تابع محاسبه چارت (محاسبه درجه‌ها)
        try:
            chart_result = astrology_core.calculate_natal_chart(
                birth_date_jalali=birth_date_str, 
                birth_time_str=birth_time, 
                city_name=city_name,
                latitude=float(latitude), 
                longitude=float(longitude), 
                timezone_str=timezone
            )

            # 4. پردازش و تولید تفسیر (منطق جدید)
            msg = ""
            
            if chart_result and 'error' in chart_result:
                # خطای کلی محاسبه
                msg = utils.escape_markdown_v2(f"❌ *خطای سیستمی در محاسبه چارت*:\n`{chart_result['error']}`")
            elif chart_result:
                
                # 💥💥💥 گام جدید: تولید تفسیر کامل (جایگزین منطق قدیمی فرمت‌دهی خام) 💥💥💥
                try:
                    
                    # 4.1. تولید متن تفسیر با استفاده از ماژول جدید
                    interpretation_text = astrology_interpretation.interpret_natal_chart(chart_result)
                    
                    # 4.2. ساختار نهایی پیام شامل اطلاعات اولیه و تفسیر کامل
                    final_interpretation_message = (
                        f"✨ **چارت تولد شما**\n"
                        f"تاریخ: {birth_date_str}، زمان: {birth_time}\n"
                        f"شهر: {city_name} (Lat: {latitude:.2f}, Lon: {longitude:.2f})\n"
                        f"منطقه زمانی: {timezone}\n\n"
                        f"{interpretation_text}"
                    )
                    
                    # اعمال Markdown Escaping
                    msg = utils.escape_markdown_v2(final_interpretation_message)
                    
                except Exception as interp_e:
                    # خطای تفسیر
                    error_msg_interp = f"✅ محاسبه چارت موفق بود، اما خطایی در تولید تفسیر رخ داد: `{interp_e}`"
                    logging.error(f"FATAL: Interpretation failed: {interp_e}", exc_info=True)
                    msg = utils.escape_markdown_v2(error_msg_interp)
                    
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
            # مدیریت خطاهای غیرمنتظره در طول محاسبه
            error_msg = utils.escape_markdown_v2(f"❌ *خطای محاسباتی غیرمنتظره*:\n`{e}`")
            logging.error(f"FATAL: Unhandled Exception during chart calculation: {e}", exc_info=True)
            await utils.send_message(utils.BOT_TOKEN, chat_id, error_msg, keyboards.main_menu_keyboard())

    except Exception as e:
        # مدیریت خطاهای سیستمی که کل هندلر را متوقف کرده‌اند
        error_msg = utils.escape_markdown_v2(f"❌ *خطای سیستمی بحرانی*:\nربات ناگهان متوقف شد. لطفاً دوباره تلاش کنید.")
        logging.critical(f"CRITICAL: Handler crashed completely outside inner block: {e}", exc_info=True)
        
        await utils.send_message(utils.BOT_TOKEN, chat_id, error_msg, keyboards.main_menu_keyboard())

    # 5. به‌روزرسانی وضعیت
    state['step'] = 'WELCOME' 
    await save_user_state_func(chat_id, state)
