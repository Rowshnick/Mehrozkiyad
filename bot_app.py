import os
import httpx # استفاده از httpx برای درخواست‌های HTTP ناهمزمان
from fastapi import FastAPI
from pydantic import BaseModel

# --- تنظیمات ---
# توکن ربات تلگرام را از متغیر محیطی (environment variable) یا جای دیگر دریافت کنید.
# توجه: بهتر است این توکن را به عنوان یک Secret در محیط دیپلوی تنظیم کنید.
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN_HERE")
API_BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

# --- مدل داده برای درخواست‌های ورودی ---
# این کلاس برای اعتبارسنجی داده‌های دریافتی از وب‌هوک تلگرام استفاده می‌شود.
class WebhookUpdate(BaseModel):
    update_id: int
    message: dict | None = None

app = FastAPI(title="FastAPI Telegram Bot with MarkdownV2 Fix")

# --- تابع کمکی برای فرار (Escaping) کاراکترهای رزرو شده MarkdownV2 ---
def escape_markdown_v2(text: str) -> str:
    """
    کاراکترهای رزرو شده در فرمت MarkdownV2 تلگرام را با یک بک‌اسلش (\) فرار می‌دهد.
    این کاراکترها شامل: _, *, [, ], (, ), ~, `, >, #, +, -, =, |, {, }, ., ! هستند.
    """
    # لیست کاراکترهای رزرو شده
    reserved_chars = r'_*[]()~`>#+-=|{}.!'
    
    # ساختن یک جدول ترجمه برای فرار هر کاراکتر به صورت "\<کاراکتر>"
    escape_table = str.maketrans({char: rf'\{char}' for char in reserved_chars})
    
    return text.translate(escape_table)

# --- مسیر وب‌هوک برای دریافت پیام‌ها ---
# توجه: مسیر وب‌هوک در محیط دیپلوی معمولاً شامل توکن ربات است.
@app.post(f"/{BOT_TOKEN}")
async def telegram_webhook(update: WebhookUpdate):
    """
    رسیدگی به به‌روزرسانی‌های دریافتی از تلگرام (پیام‌ها).
    """
    if update.message:
        message = update.message
        chat_id = message['chat']['id']
        text = message.get('text', '')
        
        # تنها پیام‌های متنی را پردازش کنید
        if text.startswith('/start'):
            # --- این پیام شامل کاراکتر رزرو شده "!" است ---
            # اگر فرار (escaping) انجام نشود، تلگرام خطای 400 Bad Request خواهد داد.
            
            raw_response = "سلام! به ربات خوش آمدید. این یک پیام آزمایشی است، آیا می‌توانید این علامت تعجب (!) را ببینید؟"
            
            # --- اعمال اصلاحیه: فرار کردن متن قبل از ارسال ---
            # اگر از parse_mode='MarkdownV2' استفاده می‌کنید، باید کاراکترهای خاص را فرار دهید.
            safe_text = escape_markdown_v2(raw_response)
            
            payload = {
                'chat_id': chat_id,
                'text': safe_text,
                'parse_mode': 'MarkdownV2' # استفاده از MarkdownV2
            }
            
            # ارسال پیام پاسخ به تلگرام
            async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=10.0) as client:
                try:
                    # استفاده از "sendMessage" به جای آدرس کامل
                    response = await client.post("sendMessage", json=payload)
                    response.raise_for_status() # برای بررسی خطاهای HTTP
                    print(f"INFO: Message sent successfully. Status: {response.status_code}")
                except httpx.HTTPStatusError as e:
                    # چاپ خطای دقیق‌تر برای عیب‌یابی
                    print(f"ERROR: Failed to send message (HTTP Status Error): {e}. Response: {e.response.text}")
                except Exception as e:
                    print(f"ERROR: An unexpected error occurred while sending message: {e}")
            
        else:
            # مثال: پاسخ به پیام‌های دیگر
            print(f"INFO: Received message: {text}")
            pass
            
    return {"message": "Update processed"}

@app.on_event("startup")
async def startup_event():
    """
    رویداد راه‌اندازی برنامه
    """
    print("INFO: FastAPI Bot Application Started.")
# شما می‌توانید منطق تنظیم وب‌هوک را در اینجا اضافه کنید
# اگرچه معمولاً در دیپلوی، وب‌هوک به‌طور خودکار تنظیم می‌شود.

