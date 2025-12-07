# ----------------------------------------------------------------------
# هندلرهای مربوط به خدمات آسترولوژی (چارت تولد و غیره)
# ----------------------------------------------------------------------

import datetime
from typing import Dict, Any, Optional
from persiantools.jdatetime import JalaliDateTime
import pytz 

# ایمپورت‌های ماژول‌های داخلی
import utils
import astrology_core
import keyboards


async def handle_chart_calculation(chat_id: int, state: Dict[str, Any], save_user_state_func):
    """محاسبه نهایی چارت و ارسال خلاصه به کاربر."""
    
    # 1. بررسی وضعیت ورودی
    if state['step'] != 'CHART_INPUT_COMPLETE':
        msg = utils.escape_markdown_v2("❌ لطفاً ابتدا تاریخ و شهر تولد را از طریق منو وارد کنید.")
        await utils.send_message(utils.BOT_TOKEN, chat_id, msg, keyboards.astrology_menu_keyboard())
        return

    # 2. استخراج داده‌ها
    data = state['data']
    
    # اطمینان از وجود داده‌های کلیدی
    required_keys = ['birth_date', 'latitude', 'longitude', 'timezone']
    if not all(key in data for key in required_keys):
        # 💡 در صورتی که دیتابیس داده‌ها را ناقص ذخیره کرده باشد
        msg = utils.escape_markdown_v2("❌ خطای داده: اطلاعات تولد (تاریخ یا شهر) کامل نیست.")
        await utils.send_message(utils.BOT_TOKEN, chat_id, msg, keyboards.astrology_menu_keyboard())
        return
    
    # 3. تبدیل تاریخ و زمان
    try:
        # birth_date اکنون باید یک شیء JalaliDateTime باشد (اگر از state_manager و bot_app.py قبلی بیاید)
        # یا یک رشته تاریخ (اگر از دیتابیس خوانده شود).
        birth_date_obj = data['birth_date']
        
        if isinstance(birth_date_obj, str):
             # اگر از دیتابیس به صورت رشته ذخیره شده، دوباره آن را Parse می‌کنیم
            jdate = utils.parse_persian_date(birth_date_obj)
            if jdate is None:
                raise ValueError("تاریخ ذخیره شده در دیتابیس معتبر نیست.")
        elif isinstance(birth_date_obj, JalaliDateTime):
            jdate = birth_date_obj
        else:
            raise TypeError("فرمت تاریخ در دیتابیس نامعتبر است.")

        # تبدیل تاریخ شمسی به میلادی استاندارد
        # (زمان پیش‌فرض 12:00:00 ظهر در parse_persian_date تنظیم شده است)
        birth_datetime_gregorian: datetime.datetime = jdate.to_gregorian()
        
        # تنظیم Timezone
        tz = pytz.timezone(data['timezone'])
        
    except Exception as e:
        msg = utils.escape_markdown_v2(f"❌ خطای تبدیل تاریخ و زمان: {e}")
        await utils.send_message(utils.BOT_TOKEN, chat_id, msg)
        return
        
    lat = data['latitude']
    lon = data['longitude']
    city_name = data.get('city_name', 'نامشخص')


    # 4. انجام محاسبات اصلی
    try:
        # فراخوانی هسته محاسبات
        chart_data = astrology_core.calculate_natal_chart(birth_datetime_gregorian, lat, lon, tz)
        
        # 5. بررسی خطای محاسباتی
        if chart_data.get('error'):
            # 💡 اگر هسته محاسبات خطا برگرداند (مثلاً Ephemeris در دسترس نیست)
            msg = astrology_core.format_chart_summary(chart_data, jdate, city_name) 
        else:
            # ذخیره چارت محاسبه شده در وضعیت کاربر
            state['data']['calculated_chart'] = chart_data
            
            # تولید پیام خلاصه
            msg = astrology_core.format_chart_summary(chart_data, jdate, city_name)
            
        await save_user_state_func(chat_id, state)

        # 6. ارسال پیام و منو
        await utils.send_message(
            utils.BOT_TOKEN, 
            chat_id, 
            msg, 
            keyboards.chart_menu_keyboard() # منوی چارت (جزئیات، خانه، برگشت)
        )

    except Exception as e:
        # خطای غیرمنتظره در هندلر (بسیار بعید است با توجه به مدیریت خطای داخلی)
        print(f"FATAL ERROR in chart calculation handler: {e}")
        error_msg = utils.escape_markdown_v2("❌ خطای غیرمنتظره در محاسبه چارت. لطفاً دوباره تلاش کنید.")
        await utils.send_message(utils.BOT_TOKEN, chat_id, error_msg)


async def handle_chart_menu_actions(chat_id: int, state: Dict[str, Any]):
    """هندل کردن کلیک روی دکمه‌های منوی چارت (جزئیات، خانه‌ها و...)"""
    
    if state['step'] != 'CHART_INPUT_COMPLETE' or 'calculated_chart' not in state['data']:
        msg = utils.escape_markdown_v2("❌ ابتدا باید چارت خود را محاسبه کنید.")
        await utils.send_message(utils.BOT_TOKEN, chat_id, msg, keyboards.astrology_menu_keyboard())
        return

    chart_data = state['data']['calculated_chart']
    action = state['data'].get('last_chart_action')

    if action == 'DETAILS':
        msg = astrology_core.format_planet_positions(chart_data)
        await utils.send_message(utils.BOT_TOKEN, chat_id, msg, keyboards.chart_menu_keyboard())
    
    elif action == 'HOUSES':
        # ⚠️ (این قسمت در astology_core.py پیاده سازی نشده است، بنابراین پیام PLACEHOLDER را می‌فرستیم)
        msg = utils.escape_markdown_v2("🛠️ محاسبه خانه‌ها در حال پیاده‌سازی است.")
        await utils.send_message(utils.BOT_TOKEN, chat_id, msg, keyboards.chart_menu_keyboard())

    elif action == 'BACK':
        state['step'] = 'ASTRO_MENU'
        await utils.send_message(utils.BOT_TOKEN, chat_id, utils.escape_markdown_v2("خدمات آسترولوژی را انتخاب کنید:"), keyboards.astrology_menu_keyboard())

    else:
        # اگر کاربر دکمه‌ای را زد که هندلر ندارد، خلاصه را مجدداً ارسال می‌کنیم
        jdate_str = state['data']['birth_date']
        jdate = utils.parse_persian_date(jdate_str) if isinstance(jdate_str, str) else jdate_str
        
        msg = astrology_core.format_chart_summary(chart_data, jdate, state['data'].get('city_name', 'نامشخص'))
        await utils.send_message(utils.BOT_TOKEN, chat_id, msg, keyboards.chart_menu_keyboard())

# (تابع handle_chart_menu_actions ممکن است در سایر قسمت‌های کد فراخوانی شود،
# بنابراین آن را به صورت کامل اینجا آورده‌ایم)

# ----------------------------------------------------------------------
# سایر هندلرهای ASTRO (مثل handle_transit_calculation و...) اگر وجود دارند 
# باید در اینجا قرار بگیرند.
# ----------------------------------------------------------------------

