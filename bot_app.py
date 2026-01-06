# # bot_app.py
# =============================================================================
# نسخهٔ اصلاح‌شده و ماژولار ربات
# =============================================================================

import asyncio
import logging
import os
from datetime import date, timedelta

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode

# -----------------------------
# فایل‌های داخلی پروژه
# -----------------------------
from astrology_core import calculate_natal_chart
from interpretations_natal_pro import generate_natal_pro_full
from report_builder import build_natal_pdf_report
from transits_engine import analyze_transits_for_range

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
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# -----------------------------
# حافظهٔ ساده برای state ناتال
# -----------------------------
user_state = {}
user_birth_data = {}

# =============================================================================
#   هندلرهای ناتال (فقط زمانی فعال می‌شوند که کاربر از منوی اصلی انتخاب کند)
# =============================================================================

@dp.message(lambda m: user_state.get(m.chat.id) == "ASK_NAME")
async def natal_ask_name(msg: types.Message):
    chat_id = msg.chat.id
    user_birth_data[chat_id] = {"name": msg.text.strip()}
    user_state[chat_id] = "ASK_DATE"

    await msg.answer("تاریخ تولد را وارد کن (مثال: 1375/05/21):")


@dp.message(lambda m: user_state.get(m.chat.id) == "ASK_DATE")
async def natal_ask_date(msg: types.Message):
    chat_id = msg.chat.id
    user_birth_data[chat_id]["jalali_date"] = msg.text.strip()
    user_state[chat_id] = "ASK_TIME"

    await msg.answer("ساعت تولد را وارد کن (مثال: 14:35):")


@dp.message(lambda m: user_state.get(m.chat.id) == "ASK_TIME")
async def natal_ask_time(msg: types.Message):
    chat_id = msg.chat.id
    user_birth_data[chat_id]["time"] = msg.text.strip()
    user_state[chat_id] = "ASK_CITY"

    await msg.answer("شهر تولد را وارد کن (مثال: تهران):")


@dp.message(lambda m: user_state.get(m.chat.id) == "ASK_CITY")
async def natal_ask_city(msg: types.Message):
    chat_id = msg.chat.id
    user_birth_data[chat_id]["city"] = msg.text.strip()

    await msg.answer("⏳ در حال محاسبهٔ چارت تولد... لطفاً صبر کن.")

    try:
        # محاسبه چارت
        chart_data = calculate_natal_chart(
            name=user_birth_data[chat_id]["name"],
            jalali_date=user_birth_data[chat_id]["jalali_date"],
            time=user_birth_data[chat_id]["time"],
            city=user_birth_data[chat_id]["city"]
        )

        logger.info("چارت تولد محاسبه شد.")

        # تفسیر حرفه‌ای
        final_text = generate_natal_pro_full(chart_data)

        await msg.answer(
            "🌟 **گزارش ناتال حرفه‌ای شما آماده شد!**",
            parse_mode=ParseMode.MARKDOWN
        )
        await msg.answer(final_text, parse_mode=ParseMode.MARKDOWN)

        # ساخت PDF
        pdf_bytes = build_natal_pdf_report(chart_data, final_text)

        await bot.send_document(
            chat_id,
            document=types.BufferedInputFile(pdf_bytes, filename="natal_report_pro.pdf"),
            caption="📄 گزارش کامل ناتال PRO + Composite"
        )

        # پاک‌سازی state
        user_state.pop(chat_id, None)
        user_birth_data.pop(chat_id, None)

    except Exception as e:
        logger.error(f"خطا در پردازش ناتال: {e}")
        await msg.answer("❌ خطایی رخ داد. لطفاً دوباره تلاش کن.")


# =============================================================================
#   هندلرهای ترانزیت‌ها
# =============================================================================

def load_user_chart(user_id):
    return None  # نسخه واقعی را خودت داری


@dp.message(commands=["transits"])
async def cmd_transits(message: types.Message):
    user_id = message.from_user.id
    natal_chart = load_user_chart(user_id)
    if not natal_chart:
        return await message.reply("❗ ابتدا باید چارت ناتال خود را ثبت کنید.")

    start = date.today()
    end = start + timedelta(days=30)
    result = analyze_transits_for_range(natal_chart, start, end)

    await message.reply(result or "✨ ترانزیت مهمی یافت نشد.")


# =============================================================================
#   اضافه کردن Routerهای منوی اصلی و Symbol Menu
# =============================================================================

from bot.handlers.start import router as start_router
from bot.handlers.symbol_inline import router as symbol_router

dp.include_router(start_router)
dp.include_router(symbol_router)

# =============================================================================
#   اجرای ربات
# =============================================================================

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
