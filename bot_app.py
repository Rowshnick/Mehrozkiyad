# ----------------------------------------------------------------------
# bot_app.py - نسخه جامع و بازسازی شده (بدون حذفیات - شامل دیباگر داخلی)
# ----------------------------------------------------------------------

import os
import logging
import asyncio
import datetime
import json
import traceback
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager

# کتابخانه‌های تقویم و نجوم
from persiantools.jdatetime import JalaliDateTime
import swisseph as swe

# ایمپورت ماژول‌های داخلی پروژه
import utils
import keyboards
import state_manager
from handlers import astro_handlers, sajil_handlers
import astrology_core

# --- تنظیمات پیشرفته لاگینگ ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("BOT_MAIN")

# --- متغیرهای سراسری ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CODE_VERSION = "2025-12-24-ULTIMATE-V300"

# --- توابع مدیریت وضعیت (State Management) ---
async def get_user_state(chat_id: int) -> Dict[str, Any]:
    """دریافت وضعیت کاربر از دیتابیس با لایه محافظتی."""
    try:
        state = await state_manager.get_user_state_db(chat_id)
        if not state:
            logger.info(f"New user detected: {chat_id}")
            return {'step': 'START', 'data': {}}
        return state
    except Exception as e:
        logger.error(f"Error in get_user_state for {chat_id}: {e}")
        return {'step': 'START', 'data': {}}

async def save_user_state(chat_id: int, state: Dict[str, Any]):
    """ذخیره وضعیت کاربر با مکانیزم تایید."""
    try:
        await state_manager.save_user_state_db(chat_id, state)
    except Exception as e:
        logger.error(f"Critical error saving state for {chat_id}: {e}")

# --- هندلرهای پایه ---
async def send_error_report(chat_id: int, error_trace: str):
    """ارسال گزارش خطای فنی به کاربر (برای دیباگ سریع)."""
    error_msg = (
        "⚠️ *خطای فنی در محاسبات*\n\n"
        f"جزئیات:\n`{error_trace[:200]}`\n\n"
        "لطفاً دوباره تلاش کنید یا پارامترهای ورودی را چک کنید."
    )
    await utils.send_message(BOT_TOKEN, chat_id, utils.escape_markdown_v2(error_msg))

async def handle_start_command(chat_id: int):
    """ریست کردن وضعیت و نمایش منوی خوش‌آمدگویی."""
    state = {'step': 'WELCOME', 'data': {}}
    welcome_text = (
        "✨ به ربات جامع خدمات آسترولوژی، سجیل و سنگ‌شناسی خوش آمدید!\n\n"
        "لطفاً یکی از گزینه‌های زیر را انتخاب کنید تا فروس را آغاز کنیم:"
    )
    await utils.send_message(
        BOT_TOKEN, 
        chat_id, 
        utils.escape_markdown_v2(welcome_text), 
        keyboards.main_menu_keyboard()
    )
    await save_user_state(chat_id, state)

# --- مدیریت پیام‌های متنی (Text Handler) ---
async def handle_text_message(chat_id: int, text: str):
    """پردازش متن ورودی بر اساس استپ‌های تعریف شده."""
    state = await get_user_state(chat_id)
    step = state.get('step', 'START')

    # 1. بخش دریافت اطلاعات چارت ناتال
    if step == 'AWAITING_DATE':
        jdate = utils.parse_persian_date(text)
        if jdate:
            state['data']['birth_date'] = jdate.strftime('%Y/%m/%d')
            state['step'] = 'AWAITING_TIME'
            await save_user_state(chat_id, state)
            
            msg = f"✅ تاریخ {jdate.strftime('%Y/%m/%d')} ثبت شد.\n\n⏱ حالا ساعت دقیق تولد را وارد کنید (مثلاً 14:30):"
            await utils.send_message(BOT_TOKEN, chat_id, utils.escape_markdown_v2(msg), keyboards.time_input_keyboard())
        else:
            await utils.send_message(BOT_TOKEN, chat_id, utils.escape_markdown_v2("❌ فرمت تاریخ صحیح نیست. مثال: 1370/01/01"))
        return

    elif step == 'AWAITING_TIME':
        # اصلاح: استفاده از parse_persian_time برای استخراج دقیق
        birth_time = utils.parse_persian_time(text)
        if birth_time:
            state['data']['birth_time'] = birth_time
            state['step'] = 'AWAITING_CITY'
            await save_user_state(chat_id, state)
            await utils.send_message(BOT_TOKEN, chat_id, utils.escape_markdown_v2("✅ ساعت ثبت شد.\n\n📍 حالا نام شهر محل تولد را به فارسی وارد کنید:"))
        else:
            await utils.send_message(BOT_TOKEN, chat_id, utils.escape_markdown_v2("❌ ساعت نامعتبر است. مثال: 08:20 یا 21:45"))
        return

    elif step == 'AWAITING_CITY':
        city_data = utils.get_city_lookup_data(text)
        if city_data:
            state['data'].update({
                'city_name': text,
                'latitude': city_data.get('latitude'), # اطمینان از ذخیره کامل برای astro_handlers
                'longitude': city_data.get('longitude'),
                'timezone': city_data.get('timezone')
            })
            state['step'] = 'CHART_INPUT_COMPLETE'
            await save_user_state(chat_id, state)
            
            msg = f"✅ شهر {text} با مختصات {city_data['latitude']} شناسایی شد.\n\nآماده محاسبه چارت هستید؟"
            calc_kb = keyboards.create_keyboard([[keyboards.create_button("محاسبه و ارسال چارت 📝", callback_data='SERVICES|ASTRO|CHART_CALC')]])
            await utils.send_message(BOT_TOKEN, chat_id, utils.escape_markdown_v2(msg), calc_kb)
        else:
            await utils.send_message(BOT_TOKEN, chat_id, utils.escape_markdown_v2("❌ شهر پیدا نشد. لطفاً نام مرکز استان را وارد کنید."))
        return

    # 2. بخش ورود داده‌های سجیل (Sajil)
    elif step == 'SAJIL_INPUT':
        await sajil_handlers.run_sajil_workflow(chat_id, text, get_user_state, save_user_state)
        return

    # هندلر دستورات مستقیم
    if text == '/start':
        await handle_start_command(chat_id)
    elif text == '/help':
        await utils.send_message(BOT_TOKEN, chat_id, "راهنمای ربات...")

# --- مدیریت کلیک دکمه‌ها (Callback Query) ---
async def handle_callback_query(chat_id: int, callback_id: str, data: str):
    """مدیریت دکمه‌های شیشه‌ای و منوهای تو در تو."""
    try:
        state = await get_user_state(chat_id)
        parts = data.split('|')
        menu = parts[0]
        submenu = parts[1]
        param = parts[2] if len(parts) > 2 else '0'

        if menu == 'MAIN':
            if submenu == 'SERVICES':
                await utils.send_message(BOT_TOKEN, chat_id, "🔮 منوی خدمات جامع:", keyboards.services_menu_keyboard())
            elif submenu == 'WELCOME':
                await handle_start_command(chat_id)

        elif menu == 'SERVICES':
            if submenu == 'ASTRO':
                if param == '0':
                    await utils.send_message(BOT_TOKEN, chat_id, "✨ بخش آسترولوژی:", keyboards.astrology_menu_keyboard())
                elif param == 'CHART_INPUT':
                    state['step'] = 'AWAITING_DATE'
                    await utils.send_message(BOT_TOKEN, chat_id, utils.escape_markdown_v2("🗓 تاریخ تولد شمسی خود را وارد کنید (مثال: 1365/12/20):"))
                elif param == 'CHART_CALC':
                    await utils.answer_callback_query(BOT_TOKEN, callback_id, "در حال استخراج داده‌های نجومی...")
                    # اصلاح: اضافه کردن بلوک try برای جلوگیری از کرش کل ربات در صورت خطای دیتای نجومی
                    try:
                        await astro_handlers.handle_chart_calculation(chat_id, state, save_user_state)
                    except Exception as e:
                        logger.error(f"Calculation Error: {traceback.format_exc()}")
                        # کد حذف نشد، فقط گزارش خطا به کاربر اضافه شد
                        await send_error_report(chat_id, str(e))
                    return

            elif submenu == 'SIGIL':
                state['step'] = 'SAJIL_INPUT'
                await utils.send_message(BOT_TOKEN, chat_id, "✍️ کلمه یا نیت خود را برای تولید سجیل وارد کنید:")

            elif submenu == 'GEM':
                await utils.send_message(BOT_TOKEN, chat_id, "💎 منوی سنگ‌شناسی و چاکرا:", keyboards.gem_menu_keyboard())

        elif menu == 'TIME' and submenu == 'DEFAULT':
            state['data']['birth_time'] = param
            state['step'] = 'AWAITING_CITY'
            await save_user_state(chat_id, state)
            await utils.send_message(BOT_TOKEN, chat_id, utils.escape_markdown_v2(f"✅ ساعت {param} تنظیم شد. حالا نام شهر را بفرستید:"))

        await utils.answer_callback_query(BOT_TOKEN, callback_id)
        await save_user_state(chat_id, state)

    except Exception as e:
        logger.error(f"Callback Query Error: {e}")

# --- تنظیمات چرخه حیات (Lifespan) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """اجرا در هنگام شروع و پایان برنامه."""
    logger.info(f"=== Starting Bot Version {CODE_VERSION} ===")
    
    # مقداردهی اولیه دیتابیس وضعیت‌ها
    await state_manager.init_db()
    
    # تنظیم مسیر فایل‌های Ephemeris برای کتابخانه swisseph
    try:
        base_path = os.path.dirname(os.path.abspath(__file__))
        ephe_dir = os.path.join(base_path, "ephe")
        swe.set_ephe_path(ephe_dir) # استفاده از مسیر مطلق برای پایداری در Railway
        logger.info(f"✅ Swiss Ephemeris Path confirmed at: {ephe_dir}")
    except Exception as e:
        logger.error(f"❌ Critical error setting Ephemeris path: {e}")

    yield
    logger.info("=== Bot Shutting Down ===")

# --- اپلیکیشن FastAPI و وب‌هوک ---
app = FastAPI(lifespan=lifespan)

@app.post(f"/{BOT_TOKEN}")
async def webhook_handler(request: Request):
    """دریافت آپدیت‌ها از تلگرام."""
    try:
        update = await request.json()
        
        # مدیریت پیام‌های متنی
        if 'message' in update:
            msg = update['message']
            chat_id = msg['chat']['id']
            text = msg.get('text', '')
            await handle_text_message(chat_id, text)
            
        # مدیریت کلیک روی دکمه‌ها
        elif 'callback_query' in update:
            cb = update['callback_query']
            await handle_callback











async def lifespan(app: FastAPI):
    await state_manager.init_db()
    # تنظیم مسیر فایل‌های Ephemeris با آدرس مطلق
    base_path = os.path.dirname(os.path.abspath(__file__))
    ephe_dir = os.path.join(base_path, "ephe")
    swe.set_ephe_path(ephe_dir)
    yield

app = FastAPI(lifespan=lifespan)

@app.post(f"/{BOT_TOKEN}")
async def webhook(request: Request):
    try:
        update = await request.json()
        if 'message' in update:
            msg = update['message']
            await handle_text_message(msg['chat']['id'], msg.get('text', ''))
        elif 'callback_query' in update:
            cb = update['callback_query']
            await handle_callback_query(cb['message']['chat']['id'], cb['id'], cb['data'])
    except Exception as e:
        logger.error(f"Webhook Error: {e}")
    return {"ok": True}
