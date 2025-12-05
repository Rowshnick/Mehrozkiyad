import os
import httpx
import asyncio
import pytz 
import json
from typing import Optional, Tuple, Dict, Any
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel, Field
from geopy.geocoders import Nominatim
from persiantools.jdatetime import JalaliDateTime
from dotenv import load_dotenv

# Load environment variables (like BOT_TOKEN) from .env if running locally
load_dotenv() 

# ----------------------------------------------------------------------
# GLOBAL CONFIGURATION AND STATE MANAGEMENT
# ----------------------------------------------------------------------

# The bot token must be fetched once from the environment
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    print("FATAL ERROR: BOT_TOKEN environment variable not set.")

# --- State Constants ---
STATE_CITY = 1
STATE_DATE = 2
STATE_DONE = 3

# --- In-Memory State Storage ---
# NOTE: This uses an in-memory dictionary for state. State will be lost if the server restarts.
# For production, replace this with Firestore or Redis persistence.
USER_DATA: Dict[int, Dict[str, Any]] = {}

# ----------------------------------------------------------------------
# TELEGRAM PAYLOAD MODELS (for FastAPI validation)
# ----------------------------------------------------------------------

class Message(BaseModel):
    message_id: int
    text: Optional[str] = None
    chat: Dict[str, Any]
    date: int

class CallbackQuery(BaseModel):
    id: str
    data: Optional[str] = None
    message: Optional[Message] = None
    from_user: Dict[str, Any] = Field(alias='from')

class UpdatePayload(BaseModel):
    update_id: int
    message: Optional[Message] = None
    callback_query: Optional[CallbackQuery] = None

# ----------------------------------------------------------------------
# HELPER FUNCTIONS 
# ----------------------------------------------------------------------

# --- Functions for Sending Messages ---

async def send_message(chat_id: int, text: str, reply_markup: Optional[Dict[str, Any]] = None):
    """ارسال یک پیام متنی به کاربر."""
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN is not set, cannot send message.")
        return
        
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        # Use MarkdownV2 for rich formatting
        'parse_mode': 'MarkdownV2', 
        'disable_web_page_preview': True
    }
    if reply_markup:
        payload['reply_markup'] = reply_markup
        
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(url, json=payload)
            response.raise_for_status() 
            # print(f"Message sent successfully to chat ID {chat_id}. Status: {response.status_code}")
        except httpx.HTTPStatusError as e:
            # Often caused by unescaped MarkdownV2 characters
            print(f"HTTP error sending message (check MarkdownV2 escaping): {e}. Response text: {e.response.text}")
        except httpx.RequestError as e:
            print(f"Request error sending message: {e}")

async def answer_callback_query(callback_query_id: str, text: Optional[str] = None):
    """پاسخ به یک callback_query برای حذف حالت بارگذاری."""
    if not BOT_TOKEN:
        return
        
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery"
    payload = {
        'callback_query_id': callback_query_id,
        'text': text or '',
        'show_alert': False
    }
    async with httpx.AsyncClient() as client:
        try:
            await client.post(url, json=payload)
        except Exception as e:
            print(f"Error in answer_callback_query: {e}")

# --- Utility Functions ---

def parse_persian_date(date_str: str) -> Optional[JalaliDateTime]:
    """تبدیل رشته تاریخ شمسی (مثلاً 1370/01/01) به شیء JalaliDateTime."""
    try:
        parts = date_str.split('/')
        if len(parts) == 3:
            year = int(parts[0])
            month = int(parts[1])
            day = int(parts[2])
            # Basic validation
            if 1300 < year < 1500 and 1 <= month <= 12 and 1 <= day <= 31:
                return JalaliDateTime(year, month, day)
        return None
    except Exception:
        return None

async def get_coordinates_from_city(city_name: str) -> Tuple[Optional[float], Optional[float], Optional[pytz.BaseTzInfo]]:
    """جستجو برای مختصات جغرافیایی و منطقه زمانی شهر."""
    try:
        geolocator = Nominatim(user_agent="astro_telegram_bot")
        
        loop = asyncio.get_event_loop()
        # Use run_in_executor to make the blocking geopy call asynchronous
        location = await loop.run_in_executor(
            None, 
            lambda: geolocator.geocode(city_name, addressdetails=True, timeout=10)
        )
        
        if location:
            # Simplified timezone logic
            # For better results, use a library like timezonefinder-python
            if 'iran' in location.raw.get('display_name', '').lower():
                 tz = pytz.timezone('Asia/Tehran')
            else:
                 tz = pytz.utc
                 
            return location.latitude, location.longitude, tz
        
        return None, None, None
    except Exception as e:
        print(f"Error in get_coordinates_from_city: {e}")
        return None, None, None

# --- Escape Functions ---

def escape_markdown_v2(text: str) -> str:
    """
    کاراکترهای رزرو شده MarkdownV2 را برای استفاده در متن عادی Escape می‌کند.
    """
    text = str(text) 
    # Reserved characters in MarkdownV2 that must be escaped
    reserved_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    
    for char in reserved_chars:
        text = text.replace(char, f'\\{char}') 
        
    return text

def escape_code_block(text: str) -> str:
    """
    فقط کاراکترهای بک‌تیک و بک‌اسلش را برای استفاده در داخل کد بلاک Escape می‌کند.
    """
    text = str(text) 
    text = text.replace('\\', '\\\\') 
    text = text.replace('`', '\\`')
    return text

# ----------------------------------------------------------------------
# CORE LOGIC: State Machine and Update Processing
# ----------------------------------------------------------------------

async def handle_start_command(chat_id: int):
    """شروع مجدد یا آغاز مکالمه."""
    # Reset or initialize user state
    USER_DATA[chat_id] = {'state': STATE_CITY}
    
    # Define a simple inline keyboard for the main menu if needed, or just ask for city
    # reply_markup = {
    #     "inline_keyboard": [[{"text": "شروع مجدد", "callback_data": "/start"}]]
    # }

    response_text = escape_markdown_v2("به ربات اخترشناسی خوش آمدید\\! برای شروع، لطفا *نام کامل شهر محل تولد* خود را به فارسی وارد کنید\\.")
    await send_message(chat_id, response_text)

async def process_message_by_state(chat_id: int, text: str, current_state: int):
    """پردازش پیام متنی بر اساس مرحله فعلی کاربر."""
    
    if current_state == STATE_CITY:
        city_name = text.strip()
        
        # 1. Look up coordinates and timezone
        lat, lon, tz = await get_coordinates_from_city(city_name)
        
        if lat and lon and tz:
            # Success: Store data and move to the next state
            USER_DATA[chat_id]['city'] = city_name
            USER_DATA[chat_id]['lat'] = lat
            USER_DATA[chat_id]['lon'] = lon
            USER_DATA[chat_id]['timezone'] = tz.zone
            USER_DATA[chat_id]['state'] = STATE_DATE
            
            response_text = escape_markdown_v2(
                f"شهر شما \\(*{city_name}*\\) با موفقیت ثبت شد\\.\n"
                f"مرحله بعد: لطفا *تاریخ تولد شمسی* خود را با فرمت صحیح \\(مثلا: 1370/01/01\\) ارسال کنید\\."
            )
        else:
            # Failure: Ask again
            response_text = escape_markdown_v2(
                f"متاسفانه نتوانستم مختصات دقیقی برای شهر \\(*{city_name}*\\) پیدا کنم\\.\n"
                f"لطفا نام شهر را با حروف فارسی و کامل بنویسید و دوباره تلاش کنید\\."
            )
            # Stay in STATE_CITY
            
        await send_message(chat_id, response_text)
        
    elif current_state == STATE_DATE:
        date_str = text.strip()
        jdate = parse_persian_date(date_str)
        
        if jdate:
            # Success: Store data and finish the conversation flow (STATE_DONE)
            USER_DATA[chat_id]['date_of_birth'] = date_str
            USER_DATA[chat_id]['jdate'] = jdate.isoformat()
            USER_DATA[chat_id]['state'] = STATE_DONE
            
            # --- FINAL CALCULATION / SUMMARY ---
            city = USER_DATA[chat_id]['city']
            tz = USER_DATA[chat_id]['timezone']
            
            final_summary = (
                f"\\*اطلاعات ثبت شده\\*\n"
                f"شهر: {escape_markdown_v2(city)}\n"
                f"تاریخ تولد: {escape_markdown_v2(date_str)}\n"
                f"منطقه زمانی: {escape_markdown_v2(tz)}"
            )
            
            response_text = escape_markdown_v2(
                f"تبریک می‌گویم\\! اطلاعات شما کامل شد\\.\n\n"
                f"{final_summary}\n\n"
                f"اکنون می‌توانید محاسبه اصلی اخترشناسی را انجام دهید یا با دستور /start دوباره شروع کنید\\."
            )
            
            await send_message(chat_id, response_text)
            
            # Optionally: Clear data completely after done (if not needed for main menu)
            # USER_DATA.pop(chat_id, None)

        else:
            # Failure: Ask again
            response_text = escape_markdown_v2(
                f"فرمت تاریخ \\(*{date_str}*\\) معتبر نیست\\.\n"
                f"لطفا تاریخ تولد شمسی را دقیقا به صورت \\(مثلا: 1370/01/01\\) ارسال کنید\\."
            )
            # Stay in STATE_DATE
            await send_message(chat_id, response_text)

    elif current_state == STATE_DONE:
        # User is already done, send the main menu prompt or echo
        response_text = escape_markdown_v2("شما قبلا اطلاعات خود را تکمیل کرده‌اید\\.\nبرای شروع یک مکالمه جدید یا ویرایش اطلاعات، دستور \\/start را ارسال کنید\\.")
        await send_message(chat_id, response_text)


async def process_update(update: UpdatePayload):
    """منطق اصلی پردازش به‌روزرسانی‌های دریافتی از تلگرام."""
    
    # 1. Handle regular messages
    if update.message:
        msg = update.message
        chat_id = msg.chat.get('id')
        text = msg.text
        
        if not chat_id:
            print("Warning: Received message without chat_id.")
            return

        # Get current state, or default to STATE_DONE if no data exists
        user_state = USER_DATA.get(chat_id, {}).get('state', STATE_DONE)

        # Handle Commands (always check first)
        if text and text.startswith('/start'):
            print(f"Processing /start from chat {chat_id}")
            await handle_start_command(chat_id)
            return
        
        # Handle regular text messages based on state
        if text:
            await process_message_by_state(chat_id, text, user_state)
            return

    # 2. Handle callback queries (if using inline buttons)
    if update.callback_query:
        cbq = update.callback_query
        chat_id = cbq.message.chat.get('id') if cbq.message else None
        data = cbq.data
        
        print(f"Processing callback query from chat {chat_id}: {data}")

        if cbq.id:
            await answer_callback_query(cbq.id, text="درخواست شما دریافت شد.")

        if chat_id and data == '/start':
            # Handle /start from inline button if needed
            await handle_start_command(chat_id)
            return

        if chat_id:
            # Default response for other callbacks
            response_text = escape_markdown_v2(f"شما دکمه‌ای با داده: `{data}` را فشار دادید\\.")
            await send_message(chat_id, response_text)
            return


# ----------------------------------------------------------------------
# FASTAPI SETUP AND ROUTES
# ----------------------------------------------------------------------

app = FastAPI()

# 1. Health Check Route
@app.get("/")
async def root():
    """A simple endpoint to check if the service is running."""
    return {"status": "ok", "message": "Astro Telegram Bot is running. Send Webhooks to the /<BOT_TOKEN> path."}

# 2. The CRUCIAL Webhook Route
# The path MUST be exactly the BOT_TOKEN string (or a secret hash)
@app.post(f"/{BOT_TOKEN}")
async def telegram_webhook(update: UpdatePayload):
    """Handles incoming Telegram updates."""
    try:
        await process_update(update)
    except Exception as e:
        # Log the error but still return 200 OK to Telegram to prevent retry floods
        print(f"ERROR during update processing: {e}")
        pass 
        
    # Always return 200 OK fast
    return {"status": "success"}

# 3. Startup Event
@app.on_event("startup")
async def startup_event():
    """Ensure the BOT_TOKEN is set before starting."""
    if not BOT_TOKEN:
        print("FATAL: Cannot start. BOT_TOKEN is missing.")
        raise RuntimeError("BOT_TOKEN is not configured.")
    print("FastAPI Bot Application Started.")

