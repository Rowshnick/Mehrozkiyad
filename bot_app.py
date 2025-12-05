import os
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Request, HTTPException
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# استخراج توکن ربات از متغیر محیطی
# Extract bot token from environment variable
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    # در محیط واقعی، این خطا باعث توقف برنامه می‌شود تا از اجرای بدون توکن جلوگیری شود.
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set.")

# تعریف مسیر وب‌هوک (این مسیر شامل توکن است تا با URL ارسالی توسط تلگرام تطابق یابد)
# Define the webhook path (this path includes the token to match the URL sent by Telegram)
WEBHOOK_PATH = f"/{TOKEN}"
# توجه: آدرس دامنه اپلیکیشن شما باید جایگزین شود تا وب‌هوک به درستی تنظیم شود
# Note: Your application's domain address must be replaced for the webhook to be set correctly
WEBHOOK_URL = f"https://YOUR_APP_DOMAIN{WEBHOOK_PATH}" 

# تابع کمکی برای فرار (Escape) دادن کاراکترهای خاص در MarkdownV2
# Helper function to escape special characters in MarkdownV2
def escape_markdown_v2(text: str) -> str:
    """
    Escapes special characters for Telegram MarkdownV2 parsing mode.
    این تابع کاراکترهای خاص را با پیشوند بک‌اسلش '\\' فرار می‌دهد.
    """
    # کاراکترهای خاص در MarkdownV2
    # Special characters in MarkdownV2
    special_chars = [
        '_', '*', '[', ']', '(', ')', '~', '`', '>', '#',
        '+', '-', '=', '|', '{', '}', '.', '!'
    ]
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text

# توابع هندلر
# Handler functions
async def start(update: Update, context: Any) -> None:
    """Handles the /start command."""
    # پیام خوش‌آمدگویی
    welcome_message = (
        "به ربات آزمایشی خوش آمدید\\!\n"
        "این ربات با استفاده از FastAPI و Python Telegram Bot اجرا شده است\\.\n"
        "شما می‌توانید با فرستادن هر متنی، یک پاسخ ساده دریافت کنید\\.\n\n"
        "دستورات موجود:\n"
        "\\- /start: شروع مجدد و نمایش این پیام\\.\n"
        "\\- /hello: یک پیام سلام ساده\\."
    )
    
    # اطمینان از فرار (Escape) دادن صحیح کاراکترهای خاص
    await update.message.reply_text(
        text=welcome_message,
        parse_mode='MarkdownV2'
    )

async def hello(update: Update, context: Any) -> None:
    """Handles the /hello command."""
    await update.message.reply_text("سلام به شما\\! امیدوارم روز خوبی داشته باشید\\.", parse_mode='MarkdownV2')

async def echo(update: Update, context: Any) -> None:
    """Echos the user message."""
    user_text = update.message.text
    # پیام کاربر را Escape می‌کنیم تا در MarkdownV2 خطایی رخ ندهد و آن را در داخل '`' قرار می‌دهیم.
    response_text = f"شما گفتید: `{escape_markdown_v2(user_text)}`"
    await update.message.reply_text(response_text, parse_mode='MarkdownV2')


# تنظیمات اپلیکیشن تلگرام
# Telegram application setup
application = ApplicationBuilder().token(TOKEN).build()

# افزودن هندلرها
# Add handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("hello", hello))
# یک MessageHandler برای پاسخ دادن به پیام‌های متنی غیردستوری
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))


# تابع مدیریت چرخه حیات FastAPI
# FastAPI lifecycle management function
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Sets up the webhook on startup and cleans up on shutdown.
    """
    print("INFO: FastAPI Bot Application Starting...")
    try:
        # تنظیم وب‌هوک برای شروع
        # Set the webhook on startup
        # توجه: YOUR_APP_DOMAIN باید با دامنه واقعی شما جایگزین شود.
        await application.bot.set_webhook(url=WEBHOOK_URL)
        print(f"INFO: Webhook set to: {WEBHOOK_URL}")
        print("INFO: FastAPI Bot Application Started and ready for webhooks.")
    except Exception as e:
        print(f"ERROR: Could not set webhook: {e}")
        pass # ادامه اجرای برنامه حتی اگر وب‌هوک تنظیم نشود
    
    # اجرای کدهای اپلیکیشن در پس‌زمینه
    # Run application code in the background
    await application.initialize()
    await application.post_init(application.bot, application._bot_data)
    await application.updater.start()
    
    yield
    
    # حذف وب‌هوک هنگام خاموش شدن
    # Delete the webhook on shutdown
    try:
        await application.bot.delete_webhook()
        print("INFO: Webhook deleted successfully.")
    except Exception as e:
        print(f"ERROR: Could not delete webhook: {e}")
    
    # خاموش کردن اپلیکیشن تلگرام
    # Shutdown the telegram application
    await application.updater.stop()
    print("INFO: FastAPI Bot Application Stopped.")


# تعریف اپلیکیشن FastAPI با تابع مدیریت چرخه حیات
# Define the FastAPI application with the lifespan function
app = FastAPI(lifespan=lifespan)

# مسیر اصلی وب‌هوک که توسط تلگرام فراخوانی می‌شود
# The main webhook route called by Telegram
@app.post(WEBHOOK_PATH)
async def webhook(request: Request):
    """
    Handles incoming Telegram updates.
    """
    try:
        # دریافت داده‌های JSON از درخواست
        # Get JSON data from the request
        data = await request.json()
        
        # ساخت یک آبجکت Update از داده‌های دریافتی
        # Create an Update object from the received data
        update = Update.de_json(data, application.bot)
        
        # پردازش آپدیت توسط هندلرهای اپلیکیشن
        # Process the update using application handlers
        await application.process_update(update)
        
        return {"ok": True}
    except Exception as e:
        # چاپ خطا برای اشکال‌زدایی و بازگرداندن پاسخ موفق به تلگرام تا تلاش مجدد نکند
        # Print error for debugging and return success to Telegram to prevent retry
        print(f"An error occurred while processing the update: {e}")
        # بهتر است همیشه 200 OK را برگردانیم تا تلگرام از ارسال مجدد خودداری کند
        return {"ok": True}

# مسیر / برای بررسی سلامت (Health Check)
# The / path for health check
@app.get("/")
async def root():
    return {"message": "FastAPI Telegram Bot is running. Send updates to the webhook path."}
