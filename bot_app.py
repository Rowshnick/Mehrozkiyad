# ----------------------------------------------------------------------
# bot_app.py - FULL VERSION (200+ Lines) - NO DELETIONS
# ----------------------------------------------------------------------
import os
import logging
import asyncio
import datetime
from fastapi import FastAPI, Request
from typing import Dict, Any
from contextlib import asynccontextmanager
import swisseph

# ایمپورت ماژول‌های داخلی (مطابق ساختار پروژه شما)
import utils
import keyboards
import state_manager
from handlers import astro_handlers, sajil_handlers
import astrology_core

# تنظیمات لاگینگ برای عیب‌یابی در Railway
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CODE_VERSION = "2025-12-24-EMERGENCY-RECOVERY-V1"

# --- مدیریت وضعیت کاربر ---
async def get_user_state(chat_id: int) -> Dict[str, Any]:
    try:
        state = await state_manager.get_user_state_db(chat_id)
        return state if state else {'step': 'START', 'data': {}}
    except Exception as e:
        logger.error(f"Error fetching state: {e}")
        return {'step': 'START', 'data': {}}

async def save_user_state(chat_id: int, state: Dict[str, Any]):
    try:
        await state_manager.save_user_state_db(chat_id, state)
    except Exception as e:
        logger.error(f"Error saving state: {e}")

# --- هندلرهای اصلی دستورات ---
async def handle_start_command(chat_id: int):
    state = {'step': 'WELCOME', 'data': {}}
    welcome_text = utils.escape_markdown_v2(
        "✨ به ربات جامع طالع‌بینی و سجیل خوش آمدید!\n"
        "برای شروع از منوی زیر استفاده کنید."
    )
    await utils.send_message(BOT_TOKEN, chat_id, welcome_text, keyboards.main_menu_keyboard())
    await save_user_state(chat_id, state)

# --- هندلر پیام‌های متنی (بازسازی کامل منطق ورودی) ---
async def handle_text_message(chat_id: int, text: str):
    state = await get_user_state(chat_id)
    step = state.get('step')

    # بخش ورود اطلاعات چارت نجومی
    if step == 'AWAITING_DATE':
        jdate = utils.parse_persian_date(text)
        if jdate:
            state['data']['birth_date'] = jdate.strftime('%Y/%m/%d')
            state['step'] = 'AWAITING_TIME'
            await save_user_state(chat_id, state)
            msg = utils.escape_markdown_v2(f"✅ تاریخ {jdate.strftime('%Y/%m/%d')} ثبت شد.\nساعت تولد را وارد کنید (مثال: 14:30):")
            await utils.send_message(BOT_TOKEN, chat_id, msg, keyboards.time_input_keyboard())
        else:
            await utils.send_message(BOT_TOKEN, chat_id, utils.escape_markdown_v2("❌ فرمت تاریخ اشتباه است. مثال: 1370/01/01"))
        return

    elif step == 'AWAITING_TIME':
        birth_time = utils.parse_persian_time(text)
        if birth_time:
            state['data']['birth_time'] = birth_time
            state['step'] = 'AWAITING_CITY'
            await save_user_state(chat_id, state)
            await utils.send_message(BOT_TOKEN, chat_id, utils.escape_markdown_v2("✅ ثبت شد. حالا نام شهر تولد (به فارسی):"))
        else:
            await utils.send_message(BOT_TOKEN, chat_id, utils.escape_markdown_v2("❌ فرمت ساعت اشتباه است. مثال: 18:45"))
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
            msg = utils.escape_markdown_v2(f"✅ اطلاعات کامل شد. برای دریافت چارت ناتال دکمه زیر را بزنید.")
            kb = keyboards.create_keyboard([[keyboards.create_button("محاسبه چارت ناتال 📝", callback_data='SERVICES|ASTRO|CHART_CALC')]])
            await utils.send_message(BOT_TOKEN, chat_id, msg, kb)
        else:
            await utils.send_message(BOT_TOKEN, chat_id, utils.escape_markdown_v2("❌ شهر پیدا نشد. لطفاً نام مرکز استان را وارد کنید."))
        return

    # بخش هندلر سجیل (بدون حذفیات)
    elif step == 'SAJIL_INPUT':
        await sajil_handlers.run_sajil_workflow(chat_id, text, get_user_state, save_user_state)
        return

    if text == '/start':
        await handle_start_command(chat_id)

# --- هندلر دکمه‌های اینلاین ---
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
                await utils.answer_callback_query(BOT_TOKEN, callback_id, "در حال محاسبه...")
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

        await utils.answer_callback_query(BOT_TOKEN, callback_id)
        await save_user_state(chat_id, state)
    except Exception as e:
        logger.error(f"Callback Error: {e}")

# --- پیکربندی FastAPI و Lifespan ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # مقداردهی اولیه دیتابیس
    await state_manager.init_db()
    # تنظیم مسیر فایل‌های نجومی (بسیار مهم برای رفع خطای Tuple Index)
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        ephe_path = os.path.join(base_dir, "ephe")
        swisseph.set_ephe_path(ephe_path)
        logger.info(f"✅ Swiss Ephemeris Path confirmed: {ephe_path}")
    except Exception as e:
        logger.error(f"Failed to set Ephemeris path: {e}")
    yield

app = FastAPI(lifespan=lifespan)

@app.post(f"/{BOT_TOKEN}")
async def webhook_handler(request: Request):
    try:
        body = await request.json()
        if 'message' in body:
            msg = body['message']
            await handle_text_message(msg['chat']['id'], msg.get('text', ''))
        elif 'callback_query' in body:
            q = body['callback_query']
            await handle_callback_query(q['message']['chat']['id'], q['id'], q['data'])
        return {"ok": True}
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return {"ok": False}
