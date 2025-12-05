import os
import logging
from fastapi import FastAPI, Request
import telegram
from telegram import Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters, CallbackContext

# پیکربندی اولیه
# توکن ربات از متغیر محیطی خوانده می شود
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
if TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN":
    logging.warning("TELEGRAM_BOT_TOKEN is not set. Bot will not function correctly without it.")

# تنظیم لاگ‌گیری
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# دیکشنری برای ذخیره وضعیت کاربران
# کلید: user_id (شناسه کاربر)، مقدار: state (وضعیت فعلی)
user_states = {}
# دیکشنری برای ذخیره داده‌های موقت کاربر
user_data = {}

# تعریف وضعیت‌ها (States)
# این اعداد مشخص کننده مراحل مختلف مکالمه هستند.
STATE_START = 0
STATE_ASKING_NAME = 1
STATE_ASKING_CONFIRMATION = 2
STATE_DONE = 3


# --- توابع هندلر ---

def start(update: Update, context: CallbackContext) -> None:
    """پاسخ به فرمان /start و شروع مکالمه."""
    user_id = update.effective_user.id
    user_states[user_id] = STATE_ASKING_NAME
    # حذف داده‌های قبلی برای شروع مجدد
    if user_id in user_data:
        del user_data[user_id]
        
    update.message.reply_text(
        'سلام! من ربات Mehrozkiyad هستم. برای شروع، لطفاً نام کامل خود را وارد کنید.'
    )


def handle_message(update: Update, context: CallbackContext) -> None:
    """پردازش پیام‌های متنی بر اساس وضعیت کاربر."""
    user_id = update.effective_user.id
    text = update.message.text.strip()
    # اگر کاربر در user_states نباشد، وضعیت پیش‌فرض (STATE_START) را در نظر می‌گیریم.
    current_state = user_states.get(user_id, STATE_START)

    logger.info(f"User {user_id} is in state {current_state} with message: {text}")

    if current_state == STATE_ASKING_NAME:
        # وضعیت ۱: نام کاربر را دریافت و درخواست تأیید می‌کنیم
        if len(text) > 0:
            user_data[user_id] = {'name': text}
            # **تغییر وضعیت به مرحله تأیید**
            user_states[user_id] = STATE_ASKING_CONFIRMATION 
            update.message.reply_text(
                f'بسیار خب، نام شما «{text}» ثبت شد.\n'
                f'لطفاً برای تأیید نهایی، کلمه "بله" یا "تایید" را بفرستید.'
            )
        else:
            update.message.reply_text('لطفاً نامی معتبر وارد کنید.')

    elif current_state == STATE_ASKING_CONFIRMATION:
        # وضعیت ۲: منتظر تأیید نهایی از کاربر هستیم
        
        # ** بخش حیاتی برای رفع مشکل تکرار **
        clean_text = text.lower().replace(' ', '')
        
        # بررسی شرط تأیید (با کلمات رایج فارسی)
        if 'بله' in clean_text or 'تایید' in clean_text or 'تأیید' in clean_text:
            
            # --- تغییر وضعیت موفقیت‌آمیز و قطعی ---
            # 1. وضعیت را به پایان (STATE_DONE) تغییر می‌دهیم.
            user_states[user_id] = STATE_DONE 
            
            name = user_data.get(user_id, {}).get('name', 'دوست عزیز')
            
            update.message.reply_text(
                f'تأیید شد! متشکرم، {name}.\n'
                f'اکنون مکالمه‌ی ما وارد مرحله جدید و کاربردی شده است. برای دیدن دستورات اصلی /help را بزنید.'
            )
            
            # اگر داده‌های موقت زیادی دارید، می‌توانید با: del user_data[user_id] آنها را پاک کنید.
            
        elif current_state != STATE_DONE and 'بله' not in clean_text and 'تایید' not in clean_text:
            # اگر کاربر چیزی غیر از تأیید بفرستد، حرفش را به عنوان نام جدید در نظر می‌گیریم
            # و به حالت پرسش نام برمی‌گردیم تا بتواند تصحیح کند.
            # در این مثال، صرفاً یک پیام راهنما می‌دهیم.
            name = user_data.get(user_id, {}).get('name', '...')
            update.message.reply_text(
                f'متوجه نشدم. اگر نام «{name}» صحیح است، لطفاً فقط کلمه "بله" را ارسال کنید.\n'
                f'اگر نام اشتباه است، نام صحیح را دوباره وارد کنید.'
            )
            # اگر دوباره نام فرستاد، در مرحله بعدی این بلاک اجرا می‌شود:
            # user_states[user_id] = STATE_ASKING_NAME # اگر بخواهید امکان تغییر نام را بدهید

    elif current_state == STATE_DONE:
        # وضعیت ۳: مکالمه تمام شده و ربات آماده وظایف اصلی است.
        name = user_data.get(user_id, {}).get('name', 'دوست')
        update.message.reply_text(
            f'سلام {name}. من آماده انجام وظیفه اصلی خود هستم. چه کاری می‌توانم برایتان انجام دهم؟'
        )

    else:
        # اگر وضعیت نامشخص بود، به شروع برمی‌گردد.
        update.message.reply_text('لطفاً با فرمان /start دوباره شروع کنید.')
        user_states[user_id] = STATE_START


# --- تنظیمات FastAPI و Dispatcher ---

app = FastAPI(title="Mehrozkiyad Telegram Bot Webhook")
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
dispatcher = Dispatcher(bot, None, use_context=True)

# اضافه کردن هندلرها به Dispatcher
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

@app.on_event("startup")
async def startup_event():
    """تنظیم وب‌هوک در زمان راه‌اندازی."""
    webhook_url = os.getenv("WEBHOOK_URL")
    if webhook_url:
        # نکته: ما از توکن به عنوان بخشی از مسیر وب‌هوک برای امنیت استفاده می‌کنیم
        full_webhook_url = f"{webhook_url}/{TELEGRAM_BOT_TOKEN}" 
        await bot.set_webhook(url=full_webhook_url)
        logger.info(f"Webhook set to: {full_webhook_url}")
    else:
        logger.warning("WEBHOOK_URL environment variable is not set.")

# مسیر وب‌هوک که تلگرام به آن پیام می‌فرستد
@app.post(f"/{TELEGRAM_BOT_TOKEN}")
async def webhook(request: Request):
    """دریافت به‌روزرسانی‌ها از تلگرام و ارسال به Dispatcher."""
    try:
        data = await request.json()
        update = Update.de_json(data, bot)
        dispatcher.process_update(update)
    except Exception as e:
        logger.error(f"Error processing update: {e}")
    return {"ok": True}

@app.get("/")
def read_root():
    return {"status": "Mehrozkiyad Bot is running and waiting for webhook calls."}

