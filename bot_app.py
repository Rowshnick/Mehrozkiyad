import os
import httpx 
from fastapi import FastAPI
from pydantic import BaseModel

# --- تنظیمات ---
# توکن ربات تلگرام را از متغیر محیطی (environment variable) یا جای دیگر دریافت کنید.
# هشدار: اگر این مقدار به درستی تنظیم نشود، ربات و وب‌هوک کار نخواهد کرد.
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN_HERE")

# توجه: در محیط Immersive، آدرس پایه وب‌هوک شما توسط پلتفرم فراهم می‌شود.
# اما اگر نیاز به دسترسی مستقیم به API تلگرام باشد:
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
    """
    reserved_chars = r'_*[]()~`>#+-=|{}.!'
    
    # ساختن یک جدول ترجمه: هر کاراکتر رزرو شده به '\' + 'کاراکتر' تبدیل می‌شود.
    # باید در متن جایگزین هم بک‌اسلش را فرار دهیم، به همین دلیل از r'\<char>' استفاده می‌شود.
    escape_table = str.maketrans({char: rf'\{char}' for char in reserved_chars})
    
    return text.translate(escape_table)

# --- مسیر اصلی (روت) ---

@app.get("/")
async def root():
    """روت اصلی برای بررسی سلامت اپلیکیشن"""
    return {"status": "running", "message": "Bot is operational. Visit /set-webhook to configure Telegram."}

# --- مسیر تنظیم وب‌هوک (تنظیم یک مسیر ثابت برای سادگی) ---
@app.get("/set-webhook")
async def set_telegram_webhook():
    """
    برای تنظیم URL وب‌هوک در سمت تلگرام، این مسیر را در مرورگر باز کنید.
    توجه: آدرس شما باید https باشد.
    URL نهایی شما شبیه به این خواهد بود: https://<YOUR_APP_URL>/webhook
    """
    # URL اپلیکیشن شما باید توسط پلتفرم فراهم شود. 
    # به جای URL زیر، آدرس عمومی (Public URL) اپلیکیشن خود را قرار دهید:
    # مثال: https://<your_subdomain>.canvas.app/webhook
    
    # فرض می‌کنیم آدرس عمومی شما همان URLی است که این مسیر را از آن باز کرده‌اید، 
    # و وب‌هوک را به مسیر ثابت "/webhook" تنظیم می‌کنیم.

    # این یک عملیات خارجی است و باید URL درست را از محیط بدست آورید.
    # چون نمی‌توانم URL دیپلوی شما را بدانم، فرض می‌کنم کاربر آن را دستی جایگزین می‌کند.
    # اگر در محیطی هستید که متغیر محیطی WEBHOOK_HOST دارد، آن را استفاده کنید.
    # در غیر این صورت، از کاربر بخواهید آدرس عمومی خود را جایگزین کند.
    
    # ***مهم***: YOUR_PUBLIC_APP_URL را با آدرس عمومی اپلیکیشن خود جایگزین کنید!
    webhook_url = os.environ.get("WEBHOOK_HOST", "https://<YOUR_PUBLIC_APP_URL_HERE>/webhook")
    
    # اگر توکن نامعتبر باشد، این درخواست شکست می‌خورد
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


# --- مسیر وب‌هوک برای دریافت پیام‌ها (مسیر ثابت) ---
@app.post("/webhook")
async def telegram_webhook(update: WebhookUpdate):
    """
    رسیدگی به به‌روزرسانی‌های دریافتی از تلگرام (پیام‌ها).
    """
    if update.message:
        message = update.message
        chat_id = message['chat']['id']
        text = message.get('text', '')
        
        # لاگ ورودی
        print(f"INFO: Processing message: '{text}' from chat {chat_id}")
        
        if text.startswith('/start'):
            
            # 1. متن اصلی حاوی کاراکتر '!'
            raw_response = "سلام! به ربات خوش آمدید. این یک پیام آزمایشی است، آیا می‌توانید این علامت تعجب (!) را ببینید؟"
            
            # 2. اعمال اصلاحیه: فرار کردن متن
            safe_text = escape_markdown_v2(raw_response)
            
            # 3. لاگ برای بررسی (اشکال‌زدایی)
            print(f"DEBUG: Original Text: {raw_response}")
            print(f"DEBUG: Escaped Text: {safe_text}")
            
            payload = {
                'chat_id': chat_id,
                'text': safe_text,
                'parse_mode': 'MarkdownV2'
            }
            
            # ارسال پیام پاسخ به تلگرام
            async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=10.0) as client:
                try:
                    response = await client.post("sendMessage", json=payload)
                    response.raise_for_status() # بررسی خطاهای HTTP 4xx/5xx
                    print(f"INFO: Message sent successfully. Status: {response.status_code}")
                except httpx.HTTPStatusError as e:
                    # این بخش دقیقاً خطای تلگرام را به شما نشان خواهد داد.
                    error_message = f"Client error '{e.response.status_code} {e.response.reason}'"
                    response_text = e.response.text
                    print(f"ERROR: Failed to send message ({error_message}). Response: {response_text}")
                except Exception as e:
                    print(f"ERROR: An unexpected error occurred while sending message: {e}")
            
        else:
            # پاسخ به پیام‌های دیگر یا نادیده گرفتن
            pass
            
    return {"message": "Update processed"}

@app.on_event("startup")
async def startup_event():
    """
    رویداد راه‌اندازی برنامه
    """
    print("INFO: FastAPI Bot Application Started and ready for webhooks.")

