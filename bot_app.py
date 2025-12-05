# ======================================================================
# ماژول اصلی ربات تلگرام با استفاده از FastAPI (نسخه نهایی و اصلاح شده)
# ======================================================================

from fastapi import FastAPI, Request, HTTPException, Body
from typing import Dict, Any, Optional
import os
import datetime 
import pytz     
import asyncio
from contextlib import asynccontextmanager # 👈 برای Lifespan

# ایمپورت‌های ماژول‌های داخلی
import utils
import keyboards
import astrology_core
import main_sajil
from persiantools.jdatetime import JalaliDateTime

# --- تنظیمات ضروری ---

BOT_TOKEN = os.environ.get("BOT_TOKEN")

if not BOT_TOKEN:
    print("FATAL ERROR: BOT_TOKEN environment variable is not set.")
    # می‌توانیم اینجا یک Exception پرتاب کنیم یا از یک مقدار پیش‌فرض استفاده کنیم.

# --- وضعیت کاربر (User State) ---

USER_STATE: Dict[int, Dict[str, Any]] = {}

def get_user_state(chat_id: int) -> Dict[str, Any]:
    """دریافت یا ایجاد وضعیت کاربر."""
    if chat_id not in USER_STATE:
        USER_STATE[chat_id] = {
            'step': 'START',  # وضعیت فعلی کاربر: START, AWAITING_DATE, AWAITING_CITY, SAJIL_INPUT
            'data': {}        # داده‌های موقت (مانند تاریخ تولد یا شهر)
        }
    return USER_STATE[chat_id]


# --- توابع هندلینگ پیام ---

# 🛠️ تابع جدید برای ارسال پیام خوش آمدگویی
async def handle_start_command(chat_id: int):
    state = get_user_state(chat_id)
    state['step'] = 'WELCOME'
    state['data'] = {}
    
    welcome_message = utils.escape_markdown_v2(
        "✨ به ربات طالع‌بینی و سجیل خوش آمدید\\!\\n"\
        "برای شروع، می‌توانید از منوی خدمات در زیر استفاده کنید\\."
    )
    
    # 💡 استفاده از send_message که به صورت پیش‌فرض MarkdownV2 را اعمال می‌کند
    await utils.send_message(BOT_TOKEN, chat_id, welcome_message, keyboards.main_menu_keyboard())


async def handle_text_message(chat_id: int, text: str):
    state = get_user_state(chat_id)
    step = state['step']
    
    # 1. هندلینگ ورود داده برای چارت تولد (تاریخ)
    if step == 'AWAITING_DATE':
        jdate = utils.parse_persian_date(text)
        if jdate:
            state['data']['birth_date'] = jdate
            state['step'] = 'AWAITING_CITY'
            # 💡 Escape کردن متن خروجی
            msg = utils.escape_markdown_v2(
                f"✅ تاریخ تولد شما \\({jdate.strftime('%Y/%m/%d')}\\) ثبت شد\\.\\n"\
                "حالا نام *شهر تولد* خود را به فارسی وارد کنید\\."
            )
            await utils.send_message(BOT_TOKEN, chat_id, msg)
        else:
            msg = utils.escape_markdown_v2("❌ فرمت تاریخ نامعتبر است\\.\\n لطفاً تاریخ را به صورت YYYY/MM/DD (مثلاً 1370/01/01) وارد کنید\\.")
            await utils.send_message(BOT_TOKEN, chat_id, msg)

    # 2. هندلینگ ورود داده برای چارت تولد (شهر)
    elif step == 'AWAITING_CITY':
        city_name = text
        # ⚠️ عملیات شبکه (geopy) باید در یک Executor اجرا شود
        lat, lon, tz = await utils.get_coordinates_from_city(city_name)
        
        if lat is not None and lon is not None:
            state['data']['city_name'] = city_name
            state['data']['latitude'] = lat
            state['data']['longitude'] = lon
            state['data']['timezone'] = tz
            
            state['step'] = 'CHART_READY'
            
            # 💡 Escape کردن متن خروجی (به خصوص مختصات اعشاری)
            msg = utils.escape_markdown_v2(
                f"✅ شهر *{city_name}* ثبت شد\\.\\n"\
                f"مختصات\\: {lat}, {lon}\\n"\
                f"منطقه زمانی\\: {tz}\\n\\n"\
                "آماده برای محاسبه چارت تولد\\."
            )
            
            await utils.send_message(BOT_TOKEN, chat_id, msg, keyboards.birth_chart_menu_keyboard())
            
        else:
            msg = utils.escape_markdown_v2("❌ شهر مورد نظر پیدا نشد\\.\\n لطفاً نام شهر را دقیق‌تر وارد کنید\\.")
            await utils.send_message(BOT_TOKEN, chat_id, msg)

    # 3. هندلینگ ورود داده برای سجیل
    elif step == 'SAJIL_INPUT':
        await main_sajil.run_sajil_workflow(chat_id, text)
        state['step'] = 'WELCOME' # بازگشت به منوی اصلی

    # 4. هندلینگ در حالات دیگر (مانند WELCOME یا CHART_READY)
    else:
        msg = utils.escape_markdown_v2("لطفاً از دکمه‌های منوی زیر استفاده کنید یا /start را بزنید\\.")
        await utils.send_message(BOT_TOKEN, chat_id, msg, keyboards.main_menu_keyboard())


async def handle_callback_query(chat_id: int, callback_id: str, data: str):
    state = get_user_state(chat_id)
    parts = data.split('|')
    menu = parts[0]
    submenu = parts[1]
    param = parts[2] if len(parts) > 2 else '0'

    # 1. هندلینگ منوی اصلی
    if menu == 'MAIN':
        if submenu == 'SERVICES':
            state['step'] = 'SERVICES_MENU'
            await utils.send_message(BOT_TOKEN, chat_id, utils.escape_markdown_v2("لطفاً سرویس مورد نظر را انتخاب کنید\\."), keyboards.services_menu_keyboard())
        elif submenu == 'SHOP':
            state['step'] = 'SHOP_MENU'
            await utils.send_message(BOT_TOKEN, chat_id, utils.escape_markdown_v2("به فروشگاه خدمات خوش آمدید\\!"), keyboards.shop_menu_keyboard())
        elif submenu == 'SOCIALS':
            state['step'] = 'SOCIALS_MENU'
            await utils.send_message(BOT_TOKEN, chat_id, utils.escape_markdown_v2("لینک‌های ارتباطی ما\\:"), keyboards.socials_menu_keyboard())
        elif submenu == 'WELCOME':
            await handle_start_command(chat_id) # بازگشت به منوی اصلی

    # 2. هندلینگ زیرمنوی خدمات
    elif menu == 'SERVICES':
        if submenu == 'ASTRO':
            if param == 'CHART_INPUT':
                state['step'] = 'AWAITING_DATE'
                await utils.send_message(BOT_TOKEN, chat_id, utils.escape_markdown_v2("لطفاً تاریخ تولد خود را به صورت شمسی \\(مثلاً 1370/01/01\\) وارد کنید\\."))
            elif param == 'CHART_CALC':
                await handle_chart_calculation(chat_id, state)
                
        elif submenu == 'SAJIL':
            state['step'] = 'SAJIL_INPUT'
            await utils.send_message(BOT_TOKEN, chat_id, utils.escape_markdown_v2("لطفاً کلمه یا اعداد مورد نظر برای تولید سجیل را وارد کنید\\."))
            
        elif submenu == 'GEM':
            # بازگشت به منوی خدمات
             state['step'] = 'SERVICES_MENU'
             await utils.send_message(BOT_TOKEN, chat_id, utils.escape_markdown_v2("لطفاً سرویس مورد نظر را انتخاب کنید\\."), keyboards.services_menu_keyboard())


    # 3. هندلینگ زیرمنوی چارت تولد
    elif menu == 'CHART':
        await handle_chart_menu_actions(chat_id, state, param)


    # 4. بستن اخطار Callback
    await utils.answer_callback_query(BOT_TOKEN, callback_id)


async def handle_chart_calculation(chat_id: int, state: Dict[str, Any]):
    """انجام محاسبات اصلی چارت تولد."""
    
    date = state['data'].get('birth_date')
    lat = state['data'].get('latitude')
    lon = state['data'].get('longitude')
    tz = state['data'].get('timezone')
    
    if not all([date, lat, lon, tz]):
        msg = utils.escape_markdown_v2("❌ اطلاعات کافی \\(تاریخ، شهر\\) برای محاسبه چارت تولد وجود ندارد\\.")
        await utils.send_message(BOT_TOKEN, chat_id, msg, keyboards.main_menu_keyboard())
        return

    # ⚠️ در اینجا باید زمان پیش‌فرض را فرض کنیم (مثلاً ظهر 12:00)
    # ⚠️ Skyfield با تاریخ میلادی کار می‌کند
    dt_gregorian = date.to_gregorian().replace(hour=12, minute=0, second=0) 
    
    # 💡 محاسبات اصلی نجومی
    chart_data = astrology_core.calculate_birth_chart(
        dt_gregorian, 
        lat, 
        lon, 
        tz
    )
    
    # ذخیره داده‌های چارت برای نمایش‌های بعدی
    state['data']['chart_data'] = chart_data 
    
    # تولید پیام خلاصه
    summary_text = astrology_core.format_chart_summary(chart_data, date, state['data']['city_name'])
    
    await utils.send_message(BOT_TOKEN, chat_id, summary_text, keyboards.birth_chart_menu_keyboard())


async def handle_chart_menu_actions(chat_id: int, state: Dict[str, Any], action: str):
    """هندل کردن اکشن‌های مربوط به نمایش چارت (مانند نمایش سیارات، خانه‌ها)."""
    
    chart_data = state['data'].get('chart_data')
    if not chart_data:
        msg = utils.escape_markdown_v2("❌ لطفاً ابتدا چارت تولد خود را محاسبه کنید\\.")
        await utils.send_message(BOT_TOKEN, chat_id, msg, keyboards.services_menu_keyboard())
        return
        
    response_text = ""
    
    if action == 'PLANETS':
        response_text = astrology_core.format_planet_positions(chart_data)
    elif action == 'HOUSES':
        # ⚠️ نیاز به منطق House System
        response_text = utils.escape_markdown_v2("🏡 محاسبه خانه‌ها نیاز به پیاده‌سازی سیستم‌های House \\(مانند Koch/Placidus\\) دارد\\.")
    elif action == 'ASPECTS':
        # ⚠️ نیاز به منطق Aspects
        response_text = utils.escape_markdown_v2("📐 محاسبه زوایای سیارات \\(Aspects\\) نیاز به منطق تخصصی دارد\\.")
        
    await utils.send_message(BOT_TOKEN, chat_id, response_text, keyboards.birth_chart_menu_keyboard())
    
    
# --- پیکربندی FastAPI ---

# 🛠️ [اصلاح حیاتی]: حذف تابع تنظیم وب‌هوک در startup
# تابع lifespan برای تنظیم Webhook که باعث خطا می‌شد، حذف شد.
@asynccontextmanager
async def lifespan(app: FastAPI):
    # این بخش در صورت نیاز به اجرای کدهای آسنکرون در هنگام شروع یا پایان برنامه استفاده می‌شود
    print("INFO: FastAPI Bot Application Starting...")
    # ⚠️ بخش مربوط به set_webhook که باعث خطای "failed to resolve host" می‌شد، حذف شد.
    yield
    print("INFO: FastAPI Bot Application Shutting Down...")

app = FastAPI(lifespan=lifespan)

# ⚠️ مسیر وب‌هوک به توکن ربات شما گره خورده است.
@app.post(f"/{BOT_TOKEN}")
async def webhook_handler(request: Request):
    """هندلر اصلی وب‌هوک تلگرام."""
    
    body = await request.json()
    
    if 'message' in body:
        message = body['message']
        chat_id = message['chat']['id']
        text = message.get('text', '')
        
        # هندل دستور /start
        if text.startswith('/start'):
            await handle_start_command(chat_id)
        # هندل پیام متنی عادی
        elif text and get_user_state(chat_id)['step'] != 'START':
            await handle_text_message(chat_id, text)
        # اگر کاربر در حالت START چیزی نوشت (به جز /start)
        else:
             await handle_start_command(chat_id)

    elif 'callback_query' in body:
        query = body['callback_query']
        chat_id = query['message']['chat']['id']
        callback_id = query['id']
        data = query['data']
        
        await handle_callback_query(chat_id, callback_id, data)
        
    # تلگرام انتظار پاسخ 200 را دارد تا بداند پیام دریافت شده است.
    return {"ok": True}
