# ----------------------------------------------------------------------
# astro_handlers.py - هندلر سرویس‌های آسترولوژی (نسخه اصلاح‌شده نهایی)
# ----------------------------------------------------------------------

import astrology_core
import utils
import keyboards
from persiantools.jdatetime import JalaliDateTime
from typing import Dict, Any
import logging 

# تنظیم لاگینگ
logging.basicConfig(level=logging.INFO)


async def handle_chart_calculation(chat_id: int, state: dict, save_user_state_func):
    """
    محاسبه چارت تولد با استفاده از داده‌های ذخیره‌شده کاربر و جستجوی مختصات در لحظه.
    """
    state_data: Dict[str, Any] = state.get('data', {})
    
    logging.info(f"DEBUG: Chart Calculation Data for chat {chat_id}: {state_data}")
    
    # 1. بازیابی داده‌های اصلی از وضعیت
    birth_date_str = state_data.get('birth_date') 
    birth_time = state_data.get('birth_time') 
    city_name = state_data.get('city_name')
    
    # ❌ حذف بازیابی latitude, longitude, timezone از state:
    # latitude = state_data.get('latitude') 
    # longitude = state_data.get('longitude')
    # timezone = state_data.get('timezone')

    # بررسی صحت تمام داده‌های ضروری قبل از جستجو
    if not (birth_date_str and birth_time and city_name):
        logging.error(f"FATAL: Missing mandatory Chart Data: Date={birth_date_str}, Time={birth_time}, City={city_name}")
        msg = utils.escape_markdown_v2("❌ اطلاعات تولد کامل نیست. لطفاً تاریخ، ساعت و شهر را دوباره وارد کنید.")
        await utils.send_message(utils.BOT_TOKEN, chat_id, msg, keyboards.main_menu_keyboard())
        state['step'] = 'WELCOME' 
        await save_user_state_func(chat_id, state)
        return

    # 💥💥💥 [جدید] گام ۲: جستجوی مختصات شهر در لحظه (با اولویت محلی) 💥💥💥
    city_lookup_data = utils.get_city_lookup_data(city_name)
    
    if city_lookup_data is None:
        # اگر شهر در دیتابیس محلی یا سرویس خارجی (اگر فعال باشد) یافت نشد
        msg = utils.escape_markdown_v2("❌ شهر مورد نظر پیدا نشد.\nلطفاً نام شهر را دقیق‌تر وارد کنید.")
        await utils.send_message(utils.BOT_TOKEN, chat_id, msg, keyboards.main_menu_keyboard())
        state['step'] = 'WELCOME' 
        await save_user_state_func(chat_id, state)
        # ❌ در صورت عدم موفقیت در جستجو، تابع پایان می‌یابد
        return
    
    # استخراج مختصات از نتیجه جستجوی موفق
    latitude = city_lookup_data['latitude']
    longitude = city_lookup_data['longitude']
    timezone = city_lookup_data['timezone'] # نام منطقه زمانی (مثل Asia/Tehran)
    
    # ---------------------------------------------------
    # ادامه کد شما برای محاسبه چارت
    # ---------------------------------------------------
    
    chart_result = None

    # 3. فراخوانی تابع محاسبه چارت
    try:
        chart_result = astrology_core.calculate_natal_chart(
            birth_date_jalali=birth_date_str, 
            birth_time_str=birth_time, 
            city_name=city_name,
            latitude=latitude, # 💥 مختصات جدید
            longitude=longitude, # 💥 مختصات جدید
            timezone_str=timezone # 💥 منطقه زمانی جدید
        )

        # 4. پردازش و ارسال نتیجه
        msg = ""
        
        if chart_result and 'error' in chart_result:
            # خطای کلی محاسبه (مانند خطای تبدیل تاریخ و زمان)
            # این خطا شامل خطاهای swisseph نیز می‌شود
            msg = utils.escape_markdown_v2(f"❌ *خطای سیستمی در محاسبه چارت*:\n`{chart_result['error']}`")
        elif chart_result:
            
            # حلقه کاملاً دفاعی: تولید گزارش سیارات
            planets_info_lines = []
            
            # 💡 اصلاح: برای چاپ زیبا و منطقی داده‌های سیارات و خانه‌ها، باید آن را از کلیدهای ثابت chart_result['planets'] و chart_result['houses'] بخوانیم.
            # ساختار فعلی شما: for p, data in chart_result.items() شامل planet و houses و jd_utc می‌شود. بهتر است فقط planets را پیمایش کنید.
            
            planets_data = chart_result.get('planets', {})
            houses_data = chart_result.get('houses', {})
            
            # 4.1. اطلاعات سیارات
            for p, data in planets_data.items():
                if 'error' in data:
                    error_detail = data.get('error', 'خطای ناشناخته در محاسبه.')
                    planets_info_lines.append(
                        f"*{p.capitalize()}*: ❌ {error_detail}"
                    )
                    continue
                
                elif 'degree' in data and 'status' in data:
                    degree_value = data.get('degree') 
                    status_value = data.get('status', 'Direct')
                    
                    try:
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
                else:
                    planets_info_lines.append(
                        f"*{p.capitalize()}*: [داده ناقص یا نامعتبر]"
                    )
                        
            planets_info = "\n".join(planets_info_lines)

            # 4.2. اطلاعات آسندانت (اختیاری: برای نمایش خانه ها)
            asc_degree = houses_data.get('ascendant')
            mc_degree = houses_data.get('midheaven')
            
            houses_info = ""
            if asc_degree is not None and mc_degree is not None:
                 houses_info = (
                    f"**زوایای اصلی:**\n"
                    f"*Ascendant*: {asc_degree:.2f}°\n"
                    f"*Midheaven*: {mc_degree:.2f}°\n\n"
                )

            # ساختار نهایی پیام
            msg = utils.escape_markdown_v2(
                f"✨ **چارت تولد شما**\n"
                f"تاریخ: {birth_date_str}، زمان: {birth_time}\n"
                f"شهر: {city_name} (Lat: {latitude:.2f}, Lon: {longitude:.2f})\n\n"
                f"{houses_info}"
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

    # 5. به‌روزرسانی وضعیت (این بخش باید همیشه اجرا شود)
    state['step'] = 'WELCOME' 
    await save_user_state_func(chat_id, state)
