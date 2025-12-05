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
# TELEGRAM PAYLOAD MODELS (for FastAPI validation)
# ----------------------------------------------------------------------

# We define a minimal model for the Telegram Update structure we care about
# This helps FastAPI validate the incoming request body
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
# HELPER FUNCTIONS (Your original functions, integrated into a class/module)
# ----------------------------------------------------------------------

# The bot token must be fetched once from the environment
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    print("FATAL ERROR: BOT_TOKEN environment variable not set.")

# --- Functions for Sending Messages ---

async def send_message(chat_id: int, text: str, reply_markup: Optional[Dict[str, Any]] = None):
    """ارسال یک پیام متنی به کاربر."""
    if not BOT_TOKEN:
        return
        
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'MarkdownV2', 
        'disable_web_page_preview': True
    }
    if reply_markup:
        payload['reply_markup'] = reply_markup
        
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(url, json=payload)
            response.raise_for_status() 
            print(f"Message sent successfully to chat ID {chat_id}. Status: {response.status_code}")
        except httpx.HTTPStatusError as e:
            # IMPORTANT: 400 Bad Request usually means a MarkdownV2 escape error
            print(f"HTTP error sending message (check MarkdownV2 escaping): {e}. Response text: {e.response.text}")
        except httpx.RequestError as e:
            print(f"Request error sending message: {e}")

async def answer_callback_query(callback_query_id: str, text: Optional[str] = None):
    """پاسخ به یک callback_query."""
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
    # Your original implementation
    try:
        parts = date_str.split('/')
        if len(parts) == 3:
            year = int(parts[0])
            month = int(parts[1])
            day = int(parts[2])
            if 1300 < year < 1500 and 1 <= month <= 12 and 1 <= day <= 31:
                return JalaliDateTime(year, month, day)
        return None
    except Exception:
        return None

async def get_coordinates_from_city(city_name: str) -> Tuple[Optional[float], Optional[float], Any]:
    """جستجو برای مختصات جغرافیایی و منطقه زمانی شهر."""
    # Your original implementation
    try:
        geolocator = Nominatim(user_agent="astro_telegram_bot")
        
        loop = asyncio.get_event_loop()
        # Use run_in_executor for geolocator to prevent blocking the FastAPI event loop
        location = await loop.run_in_executor(
            None, 
            lambda: geolocator.geocode(city_name, addressdetails=True, timeout=10)
        )
        
        if location:
            # Simplified timezone logic based on original code, consider using timezonefinder for production
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
# CORE LOGIC: Update Processing
# ----------------------------------------------------------------------

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

        print(f"Processing message from chat {chat_id}: {text}")

        # Example Command Handling
        if text and text.startswith('/start'):
            response_text = escape_markdown_v2("به ربات اخترشناسی خوش آمدید! لطفا نام شهر خود را بفرستید.")
            await send_message(chat_id, response_text)
            return

        # Example City Coordinate Lookup (Demonstration)
        if text and text.lower() in ["tehran", "تهران"]:
            lat, lon, tz = await get_coordinates_from_city(text)
            if lat and lon:
                response_text = f"مختصات شهر {escape_markdown_v2(text)}:\\\nعرض جغرافیایی: `{lat}`\\\nطول جغرافیایی: `{lon}`"
            else:
                response_text = escape_markdown_v2(f"متاسفانه نتوانستم مختصات شهر {text} را پیدا کنم.")
            await send_message(chat_id, response_text)
            return

        # Default Echo Response
        if text:
            # Ensure the response text is escaped to prevent 400 Bad Request
            escaped_text = escape_markdown_v2(text)
            response_text = f"شما گفتید: `{escaped_text}`"
            await send_message(chat_id, response_text)
            return

    # 2. Handle callback queries (if using inline buttons)
    if update.callback_query:
        cbq = update.callback_query
        chat_id = cbq.message.chat.get('id') if cbq.message else None
        data = cbq.data
        
        print(f"Processing callback query from chat {chat_id}: {data}")

        if cbq.id:
            # Answer the query to dismiss the loading indicator on the client side
            await answer_callback_query(cbq.id, text="درخواست شما دریافت شد.")

        if chat_id:
            response_text = escape_markdown_v2(f"شما دکمه‌ای با داده: {data} را فشار دادید.")
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
    # This URL should *not* be used for the Telegram Webhook
    return {"status": "ok", "message": "Astro Telegram Bot is running. Send Webhooks to the /<BOT_TOKEN> path."}

# 2. The CRUCIAL Webhook Route
# The path MUST be exactly the BOT_TOKEN string (or a secret hash)
@app.post(f"/{BOT_TOKEN}")
async def telegram_webhook(update: UpdatePayload):
    """Handles incoming Telegram updates."""
    # Process the update asynchronously
    # We use await here to ensure the update processing happens before sending the 200 OK response
    try:
        await process_update(update)
    except Exception as e:
        # Log the error but still return 200 OK to Telegram to prevent retry floods
        print(f"ERROR during update processing: {e}")
        # Re-raise for FastAPI's internal logger/error handler if needed, but returning 200 is safer
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
