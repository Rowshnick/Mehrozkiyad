# bot_app.py — نسخهٔ کامل، حرفه‌ای و سازگار با Aiogram 3.4.1

import asyncio
import logging
import os
import signal

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramRetryAfter, TelegramNetworkError

from handlers import all_routers


# ---------------------------------------------------------
#  تنظیمات لاگ حرفه‌ای
# ---------------------------------------------------------
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    logging.getLogger("aiogram.event").setLevel(logging.WARNING)
    logging.info("📘 Logging initialized.")


# ---------------------------------------------------------
#  ساخت Bot و Dispatcher
# ---------------------------------------------------------
def create_bot_and_dispatcher():
    bot = Bot(
        token=os.environ.get("BOT_TOKEN"),
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
    )

    dp = Dispatcher()

    # اضافه کردن همهٔ روتِرها
    for router in all_routers:
        dp.include_router(router)

    return bot, dp


# ---------------------------------------------------------
#  مدیریت graceful shutdown
# ---------------------------------------------------------
async def shutdown(bot: Bot):
    logging.info("🛑 Shutting down bot gracefully...")
    await bot.session.close()
    logging.info("🔚 Bot shutdown complete.")


# ---------------------------------------------------------
#  اجرای Polling با مدیریت خطا
# ---------------------------------------------------------
async def run_polling(bot: Bot, dp: Dispatcher):
    while True:
        try:
            logging.info("🤖 Bot polling started...")
            await dp.start_polling(bot)

        except TelegramRetryAfter as e:
            logging.warning(f"⏳ Flood control: sleeping for {e.retry_after} seconds...")
            await asyncio.sleep(e.retry_after)

        except TelegramNetworkError:
            logging.warning("🌐 Network error. Retrying in 5 seconds...")
            await asyncio.sleep(5)

        except Exception as e:
            logging.error(f"❌ Unexpected error in polling: {e}", exc_info=True)
            await asyncio.sleep(3)


# ---------------------------------------------------------
#  تابع اصلی
# ---------------------------------------------------------
async def main():
    setup_logging()

    bot, dp = create_bot_and_dispatcher()

    # مدیریت سیگنال‌های سیستم (برای سرورهای واقعی)
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(shutdown(bot)))

    await run_polling(bot, dp)


# ---------------------------------------------------------
#  اجرای برنامه
# ---------------------------------------------------------
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped manually.")
