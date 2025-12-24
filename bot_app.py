# ----------------------------------------------------------------------
# bot_app.py - ماژول اصلی ربات تلگرام (نسخه کامل و اصلاح شده بدون حذفیات)
# ----------------------------------------------------------------------

from fastapi import FastAPI, Request
from typing import Dict, Any, Optional
import os
import datetime 
import pytz     
import asyncio
from contextlib import asynccontextmanager 
from persiantools.jdatetime import JalaliDateTime
import logging 

# 💡 ایمپورت ماژول‌های داخلی 
import utils
import keyboards
import state_manager 
from handlers import astro_handlers, sajil_handlers 
import astrology_core

# 🛠️ اصلاح شده: ایمپورت کتابخانه swisseph
import swisseph 

# --- تنظیمات ضروری ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")

if not BOT_TOKEN:
    logging.error("FATAL ERROR: BOT_TOKEN environment variable is not set.")

# --- توابع مدیریت وضعیت (Wrapper برای State Manager) ---
async def get_user_state(chat_id: int) -> Dict[str, Any]:
    """دریافت وضعیت کاربر از دیتابیس."""
    try:
        return await state_manager.get_user_state_db(chat_id)
    except Exception:
        return {'step': 'START', 'data': {}}

async def save_user_state(chat_id: int, state: Dict[str, Any]):
    """ذخیره وضعیت کاربر در دیتابیس."""
    try:
        await state_manager.save_user_state_db(chat_id, state)
    except Exception as e:
        logging.error(f"Failed to save state for chat {chat_id}: {e}")


# --- توابع هندلینگ پیام و دستور /start ---

async def handle_start_command(chat_id: int):
    """هندل کردن دستور /start یا بازگشت به منوی اصلی."""
    state = await get_user_state(chat_id)
    state['step'] = 'WELCOME'
    state['data'] = {} 
    
    welcome_message = utils.escape_markdown_v2(
        "✨ به ربات طالع‌بینی و سجیل خوش آمدید!\n"
        "برای شروع، می‌توانید از منوی خدمات در زیر استفاده کنید."
    )
    
    await utils.send_message(BOT_TOKEN, chat_id, welcome_message, keyboards.main_menu_keyboard())
    await save_user_state(chat_id, state)


async def handle_text_message(chat_id: int, text: str):
    """هندل کردن پیام‌های متنی بر اساس وضعیت فعلی کاربر."""
    state = await get_user_state(chat_id)
    step = state.get('step')
    
    # 1. هندلینگ ورود داده برای چارت تولد (تاریخ)
    if step == 'AWAITING_DATE':
        jdate = utils.parse_persian_date(text)
        if jdate:
            state['data']['birth_date'] = jdate.strftime('%Y/%m/%d')
            state['step'] = 'AWAITING_TIME' 
            await save_user_state(chat_id, state)

            msg = utils.escape_markdown_v2(
                f"✅ تاریخ تولد شما ({jdate.strftime('%Y/%m/%d')}) ثبت شد.\n"
                "*لطفاً ساعت تولد خود را به صورت HH:MM (مثلاً 14:30) وارد کنید.*\n"
                "اگر نمی‌دانید، از دکمه زیر استفاده کنید."
            )
            await utils.send_message(BOT_TOKEN, chat_id, msg, keyboards.time_input_keyboard())
            return 

        else:
            msg = utils.escape_markdown_v2("❌ فرمت تاریخ نامعتبر است.\n لطفاً تاریخ را به صورت YYYY/MM/DD (مثلاً 1370/01/01) وارد کنید.")
            await utils.send_message(BOT_TOKEN, chat_id, msg)
            return 
    
    # 1.5. هندلینگ ورود داده برای چارت تولد (زمان)
    elif step == 'AWAITING_TIME':
        birth_time = utils.parse_persian_time(text)
        if birth_time:
            state['data']['birth_time'] = birth_time
            state['step'] = 'AWAITING_CITY'
            await save_user_state(chat_id, state)

            msg = utils.escape_markdown_v2(
                f"✅ ساعت تولد شما ({birth_time}) ثبت شد.\n"
                "حالا نام *شهر تولد* خود را به فارسی وارد کنید."
            )
            await utils.send_message(BOT_TOKEN, chat_id, msg)
            return
        else:
            msg = utils.escape_markdown_v2("❌ فرمت ساعت نامعتبر است.\n لطفاً ساعت را به صورت HH:MM (مثلاً 02:30 یا 14:30) وارد کنید.")
            await utils.send_message(BOT_TOKEN, chat_id, msg, keyboards.time_input_keyboard())
            return

    # 2. هندلینگ ورود داده برای چارت تولد (شهر)
    elif step == 'AWAITING_CITY':
        city_name = text
        city_data = utils.get_city_lookup_data(city_name)
        
        if city_data:
            state['data'].update({
                'city_name': city_name,
                'latitude': city_data.get('latitude'),
                'longitude': city_data.get('longitude'),
                'timezone': city_data.get('timezone')
            })
            state['step'] = 'CHART_INPUT_COMPLETE'
            await save_user_state(chat_id, state)
            
            msg = utils.escape_markdown_v2(
                f"✅ شهر *{city_name}* ثبت شد.\n"
                f"مختصات: {city_data['latitude']:.4f}, {city_data['longitude']:.4f}\n"
                "*آماده برای محاسبه چارت تولد*."
            )
            await utils.send_message(BOT_TOKEN, chat_id, msg, keyboards.create_keyboard([[keyboards.create_button("محاسبه چارت ناتال 📝", callback_data='SERVICES|ASTRO|CHART_CALC')]]))
            return 

        else:
            msg = utils.escape_markdown_v2("❌ شهر مورد نظر پیدا نشد. نام شهر را دقیق‌تر وارد کنید.")
            await utils.send_message(BOT_TOKEN, chat_id, msg)
            return 

    # 3. هندلینگ ورود داده برای سجیل
    elif step == 'SAJIL_INPUT':
        await sajil_handlers.run_sajil_workflow(chat_id, text, get_user_state, save_user_state)
        return 

    # 4. هندلینگ در حالات دیگر
    else:
        await handle_start_command(chat_id)


# --- تابع اصلی هندلینگ کلیک‌های اینلاین (Callback Query) ---
async def handle_callback_query(chat_id: int, callback_id: str, data: str):
    try:
        state = await get_user_state(chat_id) 
        parts = data.split('|')
        menu = parts[0]
        submenu = parts[1]
        param = parts[2] if len(parts) > 2 else '0'
        
        logging.info(f"Callback Query Received: {data}")
        state['data']['last_action'] = data 
        
        if menu == 'MAIN':
            if submenu == 'SERVICES':
                state['step'] = 'WELCOME' 
                await utils.send_message(BOT_TOKEN, chat_id, "🔮 خدمت مورد نظر را انتخاب کنید:", keyboards.services_menu_keyboard())
            elif submenu == 'SHOP' or submenu == 'SOCIALS' or submenu == 'ABOUT':
                await utils.send_message(BOT_TOKEN, chat_id, "⏳ این بخش در دست توسعه است.", keyboards.back_to_main_menu_keyboard())
            elif submenu == 'WELCOME':
                await handle_start_command(chat_id)
        
        elif menu == 'SERVICES':
            if submenu == 'ASTRO' and param == '0': 
                await utils.send_message(BOT_TOKEN, chat_id, "خدمات آسترولوژی:", keyboards.astrology_menu_keyboard())
            elif submenu == 'ASTRO' and param == 'CHART_INPUT':
                state['step'] = 'AWAITING_DATE'
                await utils.send_message(BOT_TOKEN, chat_id, "لطفاً تاریخ تولد (شمسی) خود را وارد کنید (مثال 1370/01/01):")
            elif submenu == 'ASTRO' and param == 'CHART_CALC':
                await utils.answer_callback_query(BOT_TOKEN, callback_id, text="محاسبه چارت در حال انجام است...") 
                await astro_handlers.handle_chart_calculation(chat_id, state, save_user_state)
                return
            elif submenu == 'SIGIL' and param == '0': 
                state['step'] = 'SAJIL_INPUT'
                await utils.send_message(BOT_TOKEN, chat_id, "لطفاً کلمه یا اعداد مورد نظر برای تولید سجیل را وارد کنید.")
            elif submenu == 'GEM' and param == '0':
                await utils.send_message(BOT_TOKEN, chat_id, "خدمات سنگ‌شناسی انتخاب شد:", keyboards.gem_menu_keyboard())

        elif menu == 'TIME':
            if submenu == 'DEFAULT':
                state['data']['birth_time'] = param
                state['step'] = 'AWAITING_CITY'
                await save_user_state(chat_id, state)
                await utils.send_message(BOT_TOKEN, chat_id, f"✅ ساعت {param} ثبت شد. نام شهر تولد را وارد کنید:")
            elif submenu == 'BACK':
                state['step'] = 'AWAITING_DATE'
                await utils.send_message(BOT_TOKEN, chat_id, "لطفاً تاریخ تولد را وارد کنید:")

        await utils.answer_callback_query(BOT_TOKEN, callback_id) 
        await save_user_state(chat_id, state)
            
    except Exception as e:
        logging.error(f"Error in callback: {e}", exc_info=True)
        await utils.send_message(BOT_TOKEN, chat_id, "❌ خطایی رخ داد. مجدداً تلاش کنید.")


# --- پیکربندی FastAPI ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    await state_manager.init_db() 
    
    # 🛠️ اصلاح شده: تنظیم مسیر مطلق به پوشه جدید ephe
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        EPHEMERIS_PATH = os.path.join(base_dir, "ephe")
        swisseph.set_ephe_path(EPHEMERIS_PATH)
        logging.info(f"✅ مسیر Swiss Ephemeris تنظیم شد: {EPHEMERIS_PATH}")
    except Exception as e:
        logging.error(f"FATAL: Failed to set swisseph path: {e}")

    try:
        if hasattr(astrology_core, 'setup_ephemeris'):
            await astrology_core.setup_ephemeris()
    except Exception as e:
        logging.warning(f"Optional setup failed: {e}")

    yield

app = FastAPI(lifespan=lifespan)

@app.post(f"/{BOT_TOKEN}")
async def webhook_handler(request: Request):
    """هندلر اصلی وب‌هوک تلگرام."""
    try:
        body = await request.json()
    except Exception as e:
        logging.error(f"Error parsing JSON body: {e}")
        return {"ok": False}
    
    if 'message' in body:
        message = body['message']
        chat_id = message['chat']['id']
        text = message.get('text', '')
        
        if text.startswith('/start'):
            await handle_start_command(chat_id)
        else:
            await handle_text_message(chat_id, text)

    elif 'callback_query' in body:
        query = body['callback_query']
        chat_id = query['message']['chat']['id']
        callback_id = query['id']
        data = query['data']
        await handle_callback_query(chat_id, callback_id, data)
        
    return {"ok": True}

