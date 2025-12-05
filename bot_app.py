import os
import httpx 
from fastapi import FastAPI
from pydantic import BaseModel

# --- تنظیمات ---
# توکن ربات تلگرام را از متغیر محیطی (environment variable) یا جای دیگر دریافت کنید.
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN_HERE")

API_BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

# --- مدل داده برای درخواست‌های ورودی ---
class WebhookUpdate(BaseModel):
    update_id: int
    message: dict | None = None

app = FastAPI(title="FastAPI Telegram Bot with MarkdownV2 Fix")

# --- تابع کمکی برای فرار (Escaping) کاراکترهای رزرو شده MarkdownV2 ---
def escape_markdown_v2(text: str) -> str:
    """
    کاراکترهای رزرو شده در فرمت MarkdownV2 تلگرام را با یک بک‌اسلش (\) فرار می‌دهد.
    کاراکترها: _, *, [, ], (, ), ~, `, >, #, +, -, =, |, {, }, ., !
    
    این تابع با استفاده از str.replace صریح، تضمین می‌کند که کاراکتر فرار (\) 
    در رشته Python وجود داشته باشد تا توسط JSON به \\ تبدیل شود.
    """
    # لیست کامل کاراکترهایی که باید اسکیپ شوند.
    reserved_chars = r'_*[]()~`>#+-=|{}.!'
    
    new_text = text
    # استفاده از str.replace در یک حلقه برای جایگزینی مطمئن:
    for char in reserved_chars:
        # جایگزینی کاراکتر با یک بک‌اسلش + کاراکتر (به عنوان مثال، '!' با '\!')
        # این رشته پایتون توسط httpx/JSON به صورت درست '\\!' ارسال می‌شود.
        new_text = new_text.replace(char, '\\' + char)
        
    return new_text

# --- مسیر اصلی (روت) ---

@app.get("/")
async def root():
    """روت اصلی برای بررسی سلامت اپلیکیشن"""
    return {"status": "running", "message": "Bot is operational. Visit /set-webhook to configure Telegram."}

# --- مسیر تنظیم وب‌هوک ---
@app.get("/set-webhook")
async def set_telegram_webhook():
    """
    برای تنظیم URL وب‌هوک در سمت تلگرام، این مسیر را در مرورگر باز کنید.
    """
    webhook_url = os.environ.get("WEBHOOK_HOST", "https://<YOUR_PUBLIC_APP_URL_HERE>/webhook")
    
    if BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        return {"error": "BOT_TOKEN not set correctly. Cannot set webhook."}

    set_url = API_BASE_URL + "setWebhook"
    payload = {'url': webhook_url}

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.post(set_url, json=payload)
            response.raise_for_status()
            result = response.json()
            if result.get("ok"):
                return {"status": "Webhook set successfully", "url": webhook_url, "telegram_response": result}
            else:
                return {"status": "Webhook setting failed", "url": webhook_url, "telegram_response": result}
        except Exception as e:
            print(f"ERROR: Failed to set webhook: {e}")
            return {"status": "Failed to set webhook (Connection Error)", "error": str(e)}


# --- مسیر وب‌هوک برای دریافت پیام‌ها ---
@app.post("/webhook")
async def telegram_webhook(update: WebhookUpdate):
    """
    رسیدگی به به‌روزرسانی‌های دریافتی از تلگرام (پیام‌ها).
    """
    if update.message:
        message = update.message
        chat_id = message['chat']['id']
        text = message.get('text', '')
        
        print(f"INFO: Processing message: '{text}' from chat {chat_id}")
        
        if text.startswith('/start'):
            
            # متن اصلی را برای پیدا کردن کاراکترهای رزرو شده تست می‌کنیم.
            raw_response = "سلام! به ربات خوش آمدید. این یک پیام آزمایشی است، آیا می‌توانید علامت تعجب، نقطه و اندرلاین را ببینید؟ (!._)"
            
            safe_text = escape_markdown_v2(raw_response)
            
            # لاگ برای بررسی: خروجی safe_text باید حاوی یک بک‌اسلش قبل از کاراکترهای رزرو شده باشد.
            print(f"DEBUG: Original Text: {raw_response}")
            print(f"DEBUG: Escaped Text (Python String): {repr(safe_text)}")
            
            payload = {
                'chat_id': chat_id,
                'text': safe_text,
                'parse_mode': 'MarkdownV2'
            }
            
            async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=10.0) as client:
                try:
                    response = await client.post("sendMessage", json=payload)
                    response.raise_for_status() 
                    print(f"INFO: Message sent successfully. Status: {response.status_code}")
                except httpx.HTTPStatusError as e:
                    # این بخش حیاتی است و متن کامل خطا را از تلگرام استخراج می‌کند.
                    response_text = e.response.text
                    error_message = f"Client error '{e.response.status_code} {e.response.reason}'"
                    print(f"ERROR: Failed to send message ({error_message}). Response TEXT: {response_text}")
                except Exception as e:
                    print(f"ERROR: An unexpected error occurred while sending message: {e}")
            
        else:
            pass
            
    return {"message": "Update processed"}

@app.on_event("startup")
async def startup_event():
    """
    رویداد راه‌اندازی برنامه
    """
    print("INFO: FastAPI Bot Application Started and ready for webhooks.")
