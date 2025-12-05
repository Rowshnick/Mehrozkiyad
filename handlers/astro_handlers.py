# ----------------------------------------------------------------------
# handlers/astro_handlers.py
# منطق هندلینگ محاسبات و منوهای آسترولوژی.
# ----------------------------------------------------------------------

from typing import Dict, Any
import utils
import keyboards
import astrology_core
import pytz

# 💡 [تکمیل]: این توابع باید از bot_app فراخوانی شوند.

async def handle_chart_calculation(chat_id: int, state: Dict[str, Any], save_state_func):
    """انجام محاسبات اصلی چارت تولد."""
    
    date = state['data'].get('birth_date')
    lat = state['data'].get('latitude')
    lon = state['data'].get('longitude')
    tz_zone = state['data'].get('timezone')
    
    if not all([date, lat, lon, tz_zone]):
        msg = utils.escape_markdown_v2("❌ اطلاعات کافی \\(تاریخ، شهر و منطقه زمانی\\) برای محاسبه چارت تولد وجود ندارد\\.")
        await utils.send_message(utils.BOT_TOKEN, chat_id, msg, keyboards.main_menu_keyboard())
        return

    # تبدیل رشته Timezone ذخیره شده به شیء pytz
    try:
        tz = pytz.timezone(tz_zone)
    except pytz.exceptions.UnknownTimeZoneError:
        tz = pytz.utc
        
    # ⚠️ زمان تولد فرض شده (ظهر 12:00:00)
    dt_gregorian = date.to_gregorian().replace(hour=12, minute=0, second=0) 
    
    chart_data = astrology_core.calculate_natal_chart(
        dt_gregorian, 
        lat, 
        lon, 
        tz
    )
    
    if chart_data.get('error'):
        msg = utils.escape_markdown_v2(f"❌ خطای محاسباتی\\: {chart_data['error']}")
        await utils.send_message(utils.BOT_TOKEN, chat_id, msg, keyboards.services_menu_keyboard())
        return

    # ذخیره داده‌های چارت برای نمایش‌های بعدی
    state['data']['chart_data'] = chart_data 
    state['step'] = 'CHART_READY'
    
    summary_text = astrology_core.format_chart_summary(chart_data, date, state['data']['city_name'])
    
    await utils.send_message(utils.BOT_TOKEN, chat_id, summary_text, keyboards.birth_chart_menu_keyboard())
    
    await save_state_func(chat_id, state)


async def handle_chart_menu_actions(chat_id: int, state: Dict[str, Any]):
    """هندل کردن اکشن‌های مربوط به نمایش چارت (مانند نمایش سیارات، خانه‌ها)."""
    
    chart_data = state['data'].get('chart_data')
    action = state['data'].get('last_chart_action', 'PLANETS') 

    if not chart_data:
        msg = utils.escape_markdown_v2("❌ لطفاً ابتدا چارت تولد خود را محاسبه کنید\\.")
        await utils.send_message(utils.BOT_TOKEN, chat_id, msg, keyboards.services_menu_keyboard())
        return
        
    response_text = ""
    
    if action == 'PLANETS':
        response_text = astrology_core.format_planet_positions(chart_data)
    elif action == 'HOUSES':
        response_text = utils.escape_markdown_v2(
            "🏡 **بخش خانه‌ها \\(Houses\\)**\n\n"
            "این بخش در حال حاضر نیازمند پیاده‌سازی سیستم‌های محاسبه خانه‌ها \\(مانند Koch یا Placidus\\) در هسته محاسباتی است\\."
        )
    elif action == 'ASPECTS':
        response_text = utils.escape_markdown_v2(
            "📐 **بخش زوایای سیارات \\(Aspects\\)**\n\n"
            "این بخش در حال حاضر نیازمند پیاده‌سازی منطق تشخیص و تحلیل زوایا در هسته محاسباتی است\\."
        )
    else:
        response_text = utils.escape_markdown_v2("❌ عملیات نامعتبر\\.")
        
    await utils.send_message(utils.BOT_TOKEN, chat_id, response_text, keyboards.birth_chart_menu_keyboard())
