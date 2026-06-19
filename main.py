from fastapi import FastAPI
import uvicorn
from threading import Thread
from telegram.ext import ApplicationBuilder, CommandHandler
import asyncio

# -------------------------
# 1) FastAPI (برای API)
# -------------------------
app = FastAPI()

@app.get("/")
def home():
    return {"status": "Astrology Core Running", "version": "1.0"}

@app.get("/chart")
def chart_api(date: str, time: str, lat: float, lon: float):
    # اینجا تو می‌توانی از astrology_core استفاده کنی
    # مثلا:
    # chart = astrology_core.render.draw_chart(...)
    return {"message": "Chart API is working"}

# -------------------------
# 2) Telegram Bot
# -------------------------
BOT_TOKEN = "توکن ربات تلگرام"

async def start(update, context):
    await update.message.reply_text("ربات استرولوژی روشن است")

def run_bot():
    asyncio.run(_run_bot())

async def _run_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    await app.run_polling()

# -------------------------
# 3) اجرای همزمان API + Bot
# -------------------------
def start_services():
    bot_thread = Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()

    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    start_services()
