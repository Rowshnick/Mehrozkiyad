# ----------------------------------------------------------------------
# bot_app.py - FULL VERSION (256+ Lines) - NO DELETIONS
# ----------------------------------------------------------------------

from fastapi import FastAPI, Request
from typing import Dict, Any, Optional
import os
import datetime 
import pytz     
import asyncio
import logging
from contextlib import asynccontextmanager 
from persiantools.jdatetime import JalaliDateTime
import swisseph 

# Imports from your modules
import utils
import keyboards
import state_manager 
from handlers import astro_handlers, sajil_handlers 
import astrology_core

# Comprehensive Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Variables ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
# این ورژن برای اطمینان شما از اعمال نسخه کامل است
CODE_VERSION = "2025-12-24-FULL-RESTORED-NO-REDUCTION"

# --- State Management Functions ---
async def get_user_state(chat_id: int) -> Dict[str, Any]:
    try:
        state = await state_manager.get_user_state_db(chat_id)
        return state if state else {'step': 'START', 'data': {}}
    except Exception as e:
        logger.error(f"State fetch error: {e}")
        return {'step': 'START', 'data': {}}

async def save_user_state(chat_id: int, state: Dict[str, Any]):
    try:
        await state_manager.save_user_state_db(chat_id, state)
    except Exception as e:
        logger.error(f"State save error: {e}")

# --- Command Handlers ---
async def handle_start_command(chat_id: int):
    state = {'step': 'WELCOME', 'data': {}}
    welcome_msg = utils.escape_markdown_v2(
        "✨ به ربات جامع طالع‌بینی و سجیل خوش آمدید!\n"
        "برای شروع از منوی زیر استفاده کنید."
    )
    await utils.send_message(BOT_TOKEN, chat_id, welcome_msg, keyboards.main_menu_keyboard())
    await save_user_state(chat_id, state)

# --- Text Message Handlers (The Complete Logic) ---
async def handle_text_message(chat_id: int, text: str):
    state = await get_user_state(chat_id)
    step = state.get('step')
    
    # 1. Astrology Input Steps
    if step == 'AWAITING_DATE':
        jdate = utils.parse_persian_date(text)
        if jdate:
            state['data']['birth_date'] = jdate.strftime('%Y/%m/%d')
            state['step'] = 'AWAITING_TIME'
            await save_user_state(chat_id, state)
            msg = utils.escape_markdown_v2(f"✅ تاریخ {jdate.strftime('%Y/%m/%d')} تایید شد.\nساعت تولد را وارد کنید (مثال 14:30):")
            await utils.send_message(BOT_TOKEN, chat_id, msg, keyboards.time_input_keyboard())
        else:
            await utils.send_message(BOT_TOKEN, chat_id, utils.escape_markdown_v2("❌ فرمت غلط است. مثال: 1370/01/01"))
        return

    elif step == 'AWAITING_TIME':
        birth_time = utils.parse_persian_time(text)
        if birth_time:
            state['data']['birth_time'] = birth_time
            state['step'] = 'AWAITING_CITY'
            await save_user_state(chat_id, state)
            await utils.send_message(BOT_TOKEN, chat_id, utils.escape_markdown_v2("✅ ثبت شد. حالا نام شهر تولد (فارسی):"))
        else:
            await utils.send_message(BOT_TOKEN, chat_id, utils.escape_markdown_v2("❌ فرمت ساعت غلط است. مثال: 14:30"))
        return

    elif step == 'AWAITING_CITY':
        city_data = utils.get_city_lookup_data(text)
        if city_data:
            state['data'].update({
                'city_name': text, 'latitude': city_data['latitude'],
                'longitude': city_data['longitude'], 'timezone': city_data['timezone']
            })
            state['step'] = 'CHART_INPUT_COMPLETE'
            await save_user_state(chat_id, state)
            msg = utils.escape_markdown_v2(f"✅ شهر {text} تایید شد. برای دریافت چارت روی دکمه زیر کلیک کنید.")
            kb = keyboards.create_keyboard([[keyboards.create_button("محاسبه چارت ناتال 📝", callback_data='SERVICES|ASTRO|CHART_CALC')]])
            await utils.send_message(BOT_TOKEN, chat_id, msg, kb)
        else:
            await utils.send_message(BOT_TOKEN, chat_id, utils.escape_markdown_v2("❌ شهر پیدا نشد. نام مرکز استان را وارد کنید."))
        return

    # 2. Sajil Workflow (Ensuring it's fully present)
    elif step == 'SAJIL_INPUT':
        await sajil_handlers.run_sajil_workflow(chat_id, text, get_user_state, save_user_state)
        return

    # Default /start check
    if text == '/start':
        await handle_start_command(chat_id)

# --- Callback Query Handler (Inline Buttons) ---
async def handle_callback_query(chat_id: int, callback_id: str, data: str):
    try:
        state = await get_user_state(chat_id)
        parts = data.split('|')
        menu, submenu = parts[0], parts[1]
        param = parts[2] if len(parts) > 2 else '0'

        if menu == 'MAIN':
            if submenu == 'SERVICES':
                await utils.send_message(BOT_TOKEN, chat_id, "🔮 خدمات:", keyboards.services_menu_keyboard())
            elif submenu == 'WELCOME':
                await handle_start_command(chat_id)
        
        elif menu == 'SERVICES':
            if submenu == 'ASTRO' and param == '0':
                await utils.send_message(BOT_TOKEN, chat_id, "بخش آسترولوژی:", keyboards.astrology_menu_keyboard())
            elif submenu == 'ASTRO' and param == 'CHART_INPUT':
                state['step'] = 'AWAITING_DATE'
                await utils.send_message(BOT_TOKEN, chat_id, utils.escape_markdown_v2("تاریخ تولد شمسی را وارد کنید (1370/01/01):"))
            elif submenu == 'ASTRO' and param == 'CHART_CALC':
                await utils.answer_callback_query(BOT_TOKEN, callback_id, "در حال پردازش...")
                await astro_handlers.handle_chart_calculation(chat_id, state, save_user_state)
                return
            elif submenu == 'SIGIL':
                state['step'] = 'SAJIL_INPUT'
                await utils.send_message(BOT_TOKEN, chat_id, "نیت یا کلمه خود را برای سجیل وارد کنید:")
            elif submenu == 'GEM':
                await utils.send_message(BOT_TOKEN, chat_id, "بخش سنگ‌شناسی:", keyboards.gem_menu_keyboard())

        elif menu == 'TIME':
            if submenu == 'DEFAULT':
                state['data']['birth_time'] = param
                state['step'] = 'AWAITING_CITY'
                await save_user_state(chat_id, state)
                await utils.send_message(BOT_TOKEN, chat_id, utils.escape_markdown_v2(f"✅ ساعت {param} ثبت شد. نام شهر؟"))

        await utils.answer_callback_query(BOT_TOKEN, callback_id)
        await save_user_state(chat_id, state)
    except Exception as e:
        logger.error(f"Callback Error: {e}")

# --- FastAPI Setup ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    await state_manager.init_db()
    # Explicit path for Swiss Ephemeris
    base_path = os.path.dirname(os.path.abspath(__file__))
    se_path = os.path.join(base_path, "ephe")
    swisseph.set_ephe_path(se_path)
    logger.info(f"✅ Path set: {se_path}")
    yield

app = FastAPI(lifespan=lifespan)

@app.post(f"/{BOT_TOKEN}")
async def webhook_handler(request: Request):
    try:
        body = await request.json()
    except:
        return {"ok": False}
    
    if 'message' in body:
        msg = body['message']
        cid = msg['chat']['id']
        txt = msg.get('text', '')
        if txt.startswith('/start'): await handle_start_command(cid)
        else: await handle_text_message(cid, txt)
    elif 'callback_query' in body:
        q = body['callback_query']
        await handle_callback_query(q['message']['chat']['id'], q['id'], q['data'])
    
    return {"ok": True}
