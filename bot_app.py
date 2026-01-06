# bot_app.py
# =============================================================================
# نسخهٔ نهایی، ماژولار و سازگار با aiogram 3.x
# =============================================================================

import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

# -----------------------------
# تنظیمات لاگ
# -----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)


# -----------------------------
# توکن ربات
# -----------------------------
print("BOT_TOKEN:", repr(os.getenv("BOT_TOKEN")))
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set in environment variables")

bot = Bot(token=BOT_TOKEN)

# 🔹 فعال‌سازی FSM با MemoryStorage
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


# -----------------------------
# اضافه کردن Routerهای ماژولار
# -----------------------------
# /start + منوی اصلی + شروع ناتال/ترانزیت/سمبل + Back
from bot.handlers.start import router as start_router

# Symbol Menu (هدف → فرهنگ → انرژی + Back)
from bot.handlers.symbol_inline import router as symbol_router

# ترانزیت‌ها (تمام دستورات transits_*)
from bot.handlers.transits import router as transits_router

# FSM ناتال (نام، تاریخ، ساعت، شهر، محاسبه و PDF)
from bot.handlers.natal_fsm import router as natal_router

dp.include_router(start_router)
dp.include_router(symbol_router)
dp.include_router(transits_router)
dp.include_router(natal_router)


# -----------------------------
# اجرای ربات
# -----------------------------
async def main():
    logger.info("Starting bot polling...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
