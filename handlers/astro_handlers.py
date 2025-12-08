# ----------------------------------------------------------------------
# astro_handlers.py - هندلر سرویس‌های آسترولوژی
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
    
    # --- 1. اعتبارسنجی ورودی‌ها (برای جلوگیری از خطای missing arguments) ---
    required_keys = ['birth_date', 'city_name', 'latitude', 'longitude', 'timezone']
    
    # 💡 تبدیل JalaliDateTime ذخیره شده به رشته تاریخ برای استفاده در تابع
    birth_date_str = ""
    if 'birth_date' in state_data and isinstance(state_data['birth_date'], JalaliDateTime):
        birth_date_str = state_data['birth_date'].strftime('%Y/%m/%d')
    else:
        # اگر birth_date موجود نباشد یا فرمت غلط داشته باشد
        required_keys.append('birth_date_missing') 

    # 💡 فرض زمان پیش‌فرض: 12:00 (نیاز به اضافه شدن مرحله دریافت زمان در bot_app.py دارد)
    birth_time = state_data.get('birth_time', '12:00')

    # بررسی صحت تمام داده‌های ضروری
    if not all(key in state_data for key in ['city_name', 'latitude', 'longitude', 'timezone']) or not birth_date_str:
        await utils.send_message(
            utils.BOT_TOKEN, 
            chat_id, 
            utils.escape_markdown_v2("❌ اطلاعات تولد کامل نیست (تاریخ، شهر، مختصات یا منطقه زمانی). لطفاً دوباره از منوی اصلی شروع کنید."),
            keyboards.main_menu_keyboard()
        )
        return

    # --- 2. فراخوانی تابع محاسبه چارت (FIX: ارسال تمام 6 آرگومان) ---
    try:
        chart_result = astrology_core.calculate_natal_chart(
            birth_date_jalali=birth_date_str,
            birth_time_str=birth_time, 
            city_name=state_data['city_name'],
            latitude=state_data['latitude'],
            longitude=state_data['longitude'],   # ✅ FIX: آرگومان طول جغرافیایی
            timezone_str=state_data['timezone']  # ✅ FIX: آرگومان منطقه زمانی
        )

        # --- 3. پردازش و ارسال نتیجه ---
        if 'error' in chart_result:
            msg = utils.escape_markdown_v2(f"❌ *خطای سیستمی در محاسبه چارت*:\n`{chart_result['error']}`")
        else:
            # ایجاد یک گزارش ساده از موقعیت سیارات
            planets_info = "\n".join([
                f"*{p.capitalize()}*: {data.get('degree'):.2f}° ({data.get('status')})" 
                for p, data in chart_result.items() if 'error' not in data
            ])
            msg = utils.escape_markdown_v2(
                f"✨ **چارت تولد شما**\n"
                f"تاریخ: {birth_date_str}، زمان: {birth_time}\n"
                f"شهر: {state_data['city_name']}\n\n"
                f"**موقعیت سیارات:**\n{planets_info}"
            )

        await utils.send_message(
            utils.BOT_TOKEN, 
            chat_id, 
            msg, 
            keyboards.main_menu_keyboard()
        )

    except Exception as e:
        error_msg = utils.escape_markdown_v2(f"❌ *خطای غیرمنتظره در هندلر چارت*:\n`{e}`")
        await utils.send_message(utils.BOT_TOKEN, chat_id, error_msg, keyboards.main_menu_keyboard())

    # --- 4. به‌روزرسانی وضعیت ---
    state['step'] = 'WELCOME' 
    await save_user_state_func(chat_id, state)


