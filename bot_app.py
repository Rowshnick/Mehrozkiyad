# ----------------------------------------------------------------------
# bot_app.py - FULL VERSION (200+ Lines) - NO DELETIONS
# ----------------------------------------------------------------------

import os
import logging
import asyncio
import datetime
import pytz
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from persiantools.jdatetime import JalaliDateTime
import swisseph

# ایمپورت دقیق ماژول‌های پروژه شما
import utils
import keyboards
import state_manager
from handlers import astro_handlers, sajil_handlers
import astrology_core

# تنظیمات لاگینگ برای مانیتورینگ در Railway
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- متغیرهای محیطی ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CODE_VERSION = "2025-12-24-FULL-RECOVERY-REVISED"

# --- توابع مدیریت وضعیت (State Management) ---
async def get_user_state(chat_id: int):
    try:
        state = await state_manager.get_user_state_db(chat_id)
        if not state:
            return {'step': 'START', 'data': {}}
        return state
    except Exception as e:
        logger.error(f"Error getting state for {chat_id}: {e}")
        return {'step': 'START', 'data': {}}

async def save_user_state(chat_id: int, state: dict):
    try:
        await state_manager.save_user_state_db(chat_id, state)
    except Exception as e:
        logger.error(f"Error saving state for {chat_id}: {e}")

# --- هندلرهای دستورات ---
async def handle_start_command(chat_id: int):
    state = {'step': 'WELCOME', 'data': {}}
    # استفاده از تابع escape برای جلوگیری از خطای تلگرام
    welcome_text = utils.escape_markdown_v2(
        "✨ به ربات خدمات نجومی و سجیل خوش آمدید!\n"
        "لطفاً از منوی زیر یکی از گزینه‌ها را انتخاب کنید:"
    )
    await utils.send_message(BOT_TOKEN, chat_id, welcome_text, keyboards.main_menu_keyboard())
    await save_user_state(chat_id, state)

# --- هندلر پیام‌های متنی (بازسازی کامل منطق ورود داده) ---
async def handle_text_message(chat_id: int, text: str):
    state = await get_user_state(chat_id)
    step = state.get('step')

    if step == 'AWAITING_DATE':
        jdate = utils.parse_persian_date(text)
        if jdate:
            state['data']['birth_date'] = jdate.strftime('%Y/%m/%d')
            state['step'] = 'AWAITING_TIME'
            await save_user_state(chat_id, state)
            # اصلاح کاراکترهای راهنما
            msg = utils.escape_markdown_v2(
                f"✅ تاریخ {jdate.strftime('%Y/%m/%d')} ثبت شد.\n"
                "حالا ساعت تولد را وارد کنید (مثال: 14:30):"
            )
            await utils.send_message(BOT_TOKEN, chat_id, msg, keyboards.time_input_keyboard())
        else:
            err = utils.escape_markdown_v2("❌ فرمت اشتباه است. مثال: 1370/01/01")
            await utils.send_message(BOT_TOKEN, chat_id, err)

    elif step == 'AWAITING_TIME':
        birth_time = utils.parse_persian_time(text)
        if birth_time:
            state['data']['birth_time'] = birth_time
            state['step'] = 'AWAITING_CITY'
            await save_user_state(chat_id, state)
            msg = utils.escape_markdown_v2("✅ ساعت ثبت شد. نام شهر تولد را به فارسی وارد کنید:")
            await utils.send_message(BOT_TOKEN, chat_id, msg)
        else:
            err = utils.escape_markdown_v2("❌ ساعت نامعتبر است. مثال: 18:45")
            await utils.send_message(BOT_TOKEN, chat_id, err, keyboards.time_input_keyboard())

    elif step == 'AWAITING_CITY':
        city_data = utils.get_city_lookup_data(text)
        if city_data:
            state['data'].update({
                'city_name': text,
                'latitude': city_data['latitude'],
                'longitude': city_data['longitude'],
                'timezone': city_data['timezone']
            })
            state['step'] = 'CHART_INPUT_COMPLETE'
            await save_user_state(chat_id, state)
            msg = utils.escape_markdown_v2(f"✅ شهر {text} تایید شد. برای محاسبه نهایی کلیک کنید:")
            kb = keyboards.create_keyboard([[keyboards.create_button("محاسبه چارت ناتال 📝", callback_data='SERVICES|ASTRO|CHART_CALC')]])
            await utils.send_message(BOT_TOKEN, chat_id, msg, kb)
        else:
            await utils.send_message(BOT_TOKEN, chat_id, utils.escape_markdown_v2("❌ شهر پیدا نشد. نام شهر را دقیق‌تر وارد کنید."))

    elif step == 'SAJIL_INPUT':
        # هندلر کامل سجیل که قبلاً حذف شده بود
        await sajil_handlers.run_sajil_workflow(chat_id, text, get_user_state, save_user_state)

    elif text == '/start':
        await handle_start_command(chat_id)

# --- هندلر Callback Query (دکمه‌های اینلاین) ---
async def handle_callback_query(chat_id: int, callback_id: str, data: str):
    try:
        state = await get_user_state(chat_id)
        parts = data.split('|')
        menu, submenu = parts[0], parts[1]
        param = parts[2] if len(parts) > 2 else '0'

        if menu == 'MAIN':
            if submenu == 'SERVICES':
                await utils.send_message(BOT_TOKEN, chat_id, "🔮 منوی خدمات:", keyboards.services_menu_keyboard())
            elif submenu == 'WELCOME':
                await handle_start_command(chat_id)
            elif submenu in ['SHOP', 'SOCIALS', 'ABOUT']:
                await utils.send_message(BOT_TOKEN, chat_id, "⏳ این بخش به زودی فعال می‌شود.", keyboards.back_to_main_menu_keyboard())

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
                await utils.send_message(BOT_TOKEN, chat_id, "کلمه یا نیت خود را برای سجیل وارد کنید:")
            elif submenu == 'GEM':
                await utils.send_message(BOT_TOKEN, chat_id, "بخش سنگ‌شناسی و چاکرا:", keyboards.gem_menu_keyboard())

        elif menu == 'TIME':
            if submenu == 'DEFAULT':
                state['data']['birth_time'] = param
                state['step'] = 'AWAITING_CITY'
                await save_user_state(chat_id, state)
                await utils.send_message(BOT_TOKEN, chat_id, utils.escape_markdown_v2(f"✅ ساعت {param} ثبت شد. نام شهر؟"))
            elif submenu == 'BACK':
                state['step'] = 'AWAITING_DATE'
                await utils.send_message(BOT_TOKEN, chat_id, "لطفاً تاریخ را وارد کنید:")

        await utils.answer_callback_query(BOT_TOKEN, callback_id)
        await save_user_state(chat_id, state)
    except Exception as e:
        logger.error(f"Callback error: {e}")

# --- پیکربندی FastAPI ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    await state_manager.init_db()
    # تنظیم مسیر فایل‌های نجومی
    base_path = os.path.dirname(os.path.abspath(__file__))
    se_path = os.path.join(base_path, "ephe")
    swisseph.set_ephe_path(se_path)
    logger.info(f"✅ Swiss Ephemeris Path: {se_path}")
    yield

app = FastAPI(lifespan=lifespan)

@app.post(f"/{BOT_TOKEN}")
async def webhook_handler(request: Request):
    try:
        body = await request.json()
    except Exception as e:
        logger.error(f"JSON Error: {e}")
        return {"ok": False}
    
    if 'message' in body:
        msg = body['message']
        chat_id = msg['chat']['id']
        text = msg.get('text', '')
        if text.startswith('/start'):
            await handle_start_command(chat_id)
        else:
            await handle_text_message(chat_id, text)
    elif 'callback_query' in body:
        cb = body['callback_query']
        await handle_callback_query(cb['message']['chat']['id'], cb['id'], cb['data'])
    
    return {"ok": True}
