# ----------------------------------------------------------------------
# bot_app.py - ماژول اصلی ربات تلگرام (نسخه نهایی، کامل و مقاوم در برابر خطا)
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

# 🛠️ FIX 1: ایمپورت کتابخانه swisseph
import swisseph 

# --- تنظیمات ضروری ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")

if not BOT_TOKEN:
    print("FATAL ERROR: BOT_TOKEN environment variable is not set.")

# --- توابع مدیریت وضعیت (Wrapper برای State Manager) ---
async def get_user_state(chat_id: int) -> Dict[str, Any]:
    """دریافت وضعیت وضعیت کاربر از دیتابیس."""
    # اگر state_manager.get_user_state_db با خطا مواجه شود، یک دیکشنری اولیه برگردانده می‌شود
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
    # در شروع مجدد، داده‌های موقت قبلی پاک می‌شوند
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
    step = state['step']
    
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
            await save_user_state(chat_id, state) 
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
            await save_user_state(chat_id, state)
            return


    # 2. هندلینگ ورود داده برای چارت تولد (شهر)
    elif step == 'AWAITING_CITY':
        city_name = text
        city_data = utils.get_city_lookup_data(city_name)
        
        if city_data:
            lat = city_data.get('latitude')
            lon = city_data.get('longitude')
            timezone_str = city_data.get('timezone')
            
            if lat is None or lon is None or timezone_str is None:
                msg = utils.escape_markdown_v2("❌ خطای داده‌ی شهر. لطفاً نام شهر را دقیق‌تر وارد کنید.")
                await utils.send_message(BOT_TOKEN, chat_id, msg)
                await save_user_state(chat_id, state) 
                return
            
            state['data']['city_name'] = city_name
            state['data']['latitude'] = lat
            state['data']['longitude'] = lon
            state['data']['timezone'] = timezone_str 
            
            state['step'] = 'CHART_INPUT_COMPLETE'
            await save_user_state(chat_id, state)
            
            msg = utils.escape_markdown_v2(
                f"✅ شهر *{city_name}* ثبت شد.\n"
                f"مختصات: {lat:.4f}, {lon:.4f}\n"
                f"منطقه زمانی: {timezone_str}\n\n"
                "*آماده برای محاسبه چارت تولد*."
            )
            await utils.send_message(
                BOT_TOKEN, 
                chat_id, 
                msg, 
                keyboards.create_keyboard([[keyboards.create_button("محاسبه چارت ناتال 📝", callback_data='SERVICES|ASTRO|CHART_CALC')]])
            )
            return 

        else:
            msg = utils.escape_markdown_v2("❌ شهر مورد نظر پیدا نشد.\n لطفاً نام شهر را دقیق‌تر وارد کنید.")
            await utils.send_message(BOT_TOKEN, chat_id, msg)
            await save_user_state(chat_id, state) 
            return 

    # 3. هندلینگ ورود داده برای سجیل
    elif step == 'SAJIL_INPUT':
        # این تابع باید در ماژول handlers/sajil_handlers.py تعریف شده باشد.
        await sajil_handlers.run_sajil_workflow(chat_id, text, get_user_state, save_user_state)
        return 

    # 4. هندلینگ در حالات دیگر
    else:
        msg = utils.escape_markdown_v2("لطفاً از دکمه‌های منوی زیر استفاده کنید یا /start را بزنید.")
        await utils.send_message(BOT_TOKEN, chat_id, msg, keyboards.main_menu_keyboard())
        await save_user_state(chat_id, state) 
        return


# --- تابع اصلی هندلینگ کلیک‌های اینلاین (Callback Query) ---
async def handle_callback_query(chat_id: int, callback_id: str, data: str):
    """
    هندل کردن کلیک‌های کاربر روی دکمه‌های اینلاین.
    شامل مدیریت خطای دو لایه برای جلوگیری از سکوت ربات.
    """
    
    state = {} # تعریف اولیه وضعیت
    
    # 💥💥💥 مرحله 1: بلوک مدیریت خطای بازیابی وضعیت (خطای دیتابیس) 💥💥💥
    try:
        state = await get_user_state(chat_id) 
        
        # 💥💥💥 مرحله 2: بلوک مدیریت خطای پردازش منطق (خطای داخلی) 💥💥💥
        try:
            parts = data.split('|')
            menu = parts[0]
            submenu = parts[1]
            param = parts[2] if len(parts) > 2 else '0'
            
            logging.info(f"Callback Query Received: Chat ID: {chat_id}, Data: {data}")
            state['data']['last_action'] = data 
            
            # 1. هندلینگ منوی اصلی (MAIN)
            if menu == 'MAIN':
                if submenu == 'SERVICES':
                    # ✅ FIX: این همان خطی است که قبلاً کرش می‌کرد.
                    state['step'] = 'WELCOME' 
                    msg = utils.escape_markdown_v2("🔮 لطفا خدمت مورد نظر خود را انتخاب کنید:")
                    await utils.send_message(BOT_TOKEN, chat_id, msg, keyboards.services_menu_keyboard())
                    
                elif submenu == 'SHOP':
                    msg = utils.escape_markdown_v2("🛍️ فروشگاه در دست توسعه است.")
                    await utils.send_message(BOT_TOKEN, chat_id, msg, keyboards.back_to_main_menu_keyboard())
                elif submenu == 'SOCIALS':
                    msg = utils.escape_markdown_v2("🌐 شبکه‌های اجتماعی در دست توسعه است.")
                    await utils.send_message(BOT_TOKEN, chat_id, msg, keyboards.back_to_main_menu_keyboard())
                elif submenu == 'ABOUT':
                    msg = utils.escape_markdown_v2("🧑‍💻 درباره ما و راهنما در دست توسعه است.")
                    await utils.send_message(BOT_TOKEN, chat_id, msg, keyboards.back_to_main_menu_keyboard())
                elif submenu == 'WELCOME':
                    # بازگشت به منوی اصلی
                    await handle_start_command(chat_id)
                    # در این حالت answer_callback_query ضروری است
            
            # 2. هندلینگ منوی خدمات (SERVICES)
            elif menu == 'SERVICES':
                if submenu == 'ASTRO' and param == '0': 
                    state['step'] = 'ASTRO_MENU'
                    await utils.send_message(BOT_TOKEN, chat_id, utils.escape_markdown_v2("خدمات آسترولوژی را انتخاب کنید:"), keyboards.astrology_menu_keyboard())
                
                elif submenu == 'ASTRO' and param == 'CHART_INPUT':
                    # 💡 شروع فرایند ورود داده چارت
                    state['step'] = 'AWAITING_DATE'
                    await utils.send_message(BOT_TOKEN, chat_id, utils.escape_markdown_v2("لطفاً تاریخ تولد خود را به صورت شمسی (مثلاً 1370/01/01) وارد کنید."))
                    
                elif submenu == 'ASTRO' and param == 'CHART_CALC':
                    # 💡 فراخوانی هندلر محاسبه چارت
                    await utils.answer_callback_query(BOT_TOKEN, callback_id, text="محاسبه چارت در حال انجام است...") 
                    # این تابع باید در ماژول handlers/astro_handlers.py تعریف شده باشد.
                    await astro_handlers.handle_chart_calculation(chat_id, state, save_user_state)
                    return # خروج، چون answer_callback_query در داخل هندلر انجام شد

                elif submenu == 'SIGIL' and param == '0': 
                    state['step'] = 'SAJIL_INPUT'
                    await utils.send_message(BOT_TOKEN, chat_id, utils.escape_markdown_v2("لطفاً کلمه یا اعداد مورد نظر برای تولید سجیل را وارد کنید."))
                    
                elif submenu == 'GEM' and param == '0':
                    state['step'] = 'GEM_MENU'
                    await utils.send_message(BOT_TOKEN, chat_id, utils.escape_markdown_v2("خدمات سنگ‌شناسی را انتخاب کنید:"), keyboards.gem_menu_keyboard())

                elif submenu == 'HERB' and param == '0': 
                    state['step'] = 'HERB_MENU'
                    msg = utils.escape_markdown_v2("🌿 خدمات گیاه‌شناسی در دست ساخت است.")
                    await utils.send_message(BOT_TOKEN, chat_id, msg, keyboards.back_to_main_menu_keyboard())

            # 2.5. هندلینگ زیرمنوی زمان (TIME) 
            elif menu == 'TIME':
                if submenu == 'DEFAULT':
                    default_time = param 
                    state['data']['birth_time'] = default_time
                    state['step'] = 'AWAITING_CITY'
                    await save_user_state(chat_id, state)

                    msg = utils.escape_markdown_v2(
                        f"✅ ساعت تولد شما به صورت پیش‌فرض ({default_time}) ثبت شد.\n"
                        "حالا نام *شهر تولد* خود را به فارسی وارد کنید."
                    )
                    await utils.send_message(BOT_TOKEN, chat_id, msg)
                    
                elif submenu == 'BACK':
                    # بازگشت به دریافت تاریخ
                    state['step'] = 'AWAITING_DATE'
                    await save_user_state(chat_id, state)
                    await utils.send_message(BOT_TOKEN, chat_id, utils.escape_markdown_v2("لطفاً تاریخ تولد خود را به صورت شمسی (مثلاً 1370/01/01) وارد کنید."))


            # 3. بستن اخطار Callback و ذخیره وضعیت (بخش موفقیت)
            await utils.answer_callback_query(BOT_TOKEN, callback_id) 
            await save_user_state(chat_id, state)
            
        # 💥💥💥 مدیریت خطای پردازش منطق (خطای داخلی)
        except Exception as e:
            logging.error(f"RUNTIME ERROR: Logic Exception in handle_callback_query for data {data}: {e}", exc_info=True)
            error_msg = utils.escape_markdown_v2(f"❌ *خطای منطقی*: `{e.__class__.__name__}`\n\nلطفاً /start را بزنید.")
            await utils.send_message(BOT_TOKEN, chat_id, error_msg, keyboards.main_menu_keyboard())
            await utils.answer_callback_query(BOT_TOKEN, callback_id, text="❌ خطای پردازش رخ داد. لاگ‌ها ثبت شد.") 
            await save_user_state(chat_id, state)
            
    # 💥💥💥 مدیریت خطای بازیابی وضعیت (خطای دیتابیس/ State Manager)
    except Exception as e:
        logging.error(f"FATAL ERROR: State Access Exception in handle_callback_query: {e}", exc_info=True)
        error_msg = utils.escape_markdown_v2(f"❌ *خطای سیستم*: `{e.__class__.__name__}`\n\nامکان دسترسی به دیتابیس یا وضعیت کاربر وجود نداشت. لطفاً /start را بزنید.")
        await utils.send_message(BOT_TOKEN, chat_id, error_msg, keyboards.main_menu_keyboard())
        await utils.answer_callback_query(BOT_TOKEN, callback_id, text="❌ خطای حیاتی رخ داد.") 


# --- پیکربندی FastAPI ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 💡 فراخوانی ایجاد دیتابیس در هنگام شروع برنامه
    await state_manager.init_db() 
    print("INFO: FastAPI Bot Application Starting... Database initialized.")
    
    # 🛠️ FIX 2: تنظیم صریح مسیر فایل‌های اپمریس برای swisseph
    # بر اساس Dockerfile شما، مسیر فایل‌های ephe_data در کانتینر /usr/src/app/ephe_data/ است.
    try:
        EPHEMERIS_PATH = '/usr/src/app/ephe_data/'
        swisseph.set_ephe_path(EPHEMERIS_PATH)
        logging.info(f"✅ مسیر Swiss Ephemeris به طور صریح تنظیم شد: {EPHEMERIS_PATH}")
    except Exception as e:
        # اگر swisseph نصب نشده یا در این مرحله قابل دسترسی نباشد، هشدار می‌دهد.
        logging.error(f"FATAL: Failed to set swisseph path: {e}")
    # ----------------------------------------------------

    # تنظیمات کتابخانه محاسباتی (اختیاری، اگر در astrology_core است)
    try:
        # فرض می‌کنیم این خط تنظیمات سوپرامریس را انجام می‌دهد
        await astrology_core.setup_ephemeris()
        logging.info("✅ سوپرامریس (Swiss Ephemeris) با موفقیت تنظیم شد.")
    except AttributeError:
        # این هشدار اصلی در لاگ‌های شما بود، که اکنون با تنظیم مسیر صریح باید کمتر دیده شود.
        logging.warning("Setup Ephemeris not found or failed, continuing without it.")
    except Exception as e:
        logging.error(f"Ephemeris setup failed: {e}")

    yield
    print("INFO: FastAPI Bot Application Shutting Down...")

app = FastAPI(lifespan=lifespan)

@app.post(f"/{BOT_TOKEN}")
async def webhook_handler(request: Request):
    """هندلر اصلی وب‌هوک تلگرام."""
    
    body = await request.json()
    
    if 'message' in body:
        message = body['message']
        chat_id = message['chat']['id']
        text = message.get('text', '')
        
        if text.startswith('/start'):
            await handle_start_command(chat_id)
        
        else:
             state = await get_user_state(chat_id)
             # اطمینان از اینکه پیام متنی در یک وضعیت معتبر دریافت شده است
             if text and state['step'] not in ['START', 'WELCOME']:
                await handle_text_message(chat_id, text)
             else:
                # اگر کاربر در حالتی بود که نباید پیام متنی بفرستد
                await handle_start_command(chat_id)


    elif 'callback_query' in body:
        query = body['callback_query']
        chat_id = query['message']['chat']['id']
        callback_id = query['id']
        data = query['data']
        
        await handle_callback_query(chat_id, callback_id, data)
        
    return {"ok": True}
