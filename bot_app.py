# bot_app.py
# =============================================================================
# نسخهٔ پیشرفته و چندحالته ربات:
# ۱) چارت تولد + تفسیر حرفه‌ای با نکات/هشدار/پیشنهاد
# ۲) پیش‌بینی سالانه (Solar Return)
# ۳) سینستری (تطبیق دو نفر)
# ۴) آماده برای تولید گزارش چندصفحه‌ای (PDF) در لایهٔ جداگانه
# =============================================================================
import asyncio
import logging
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode

# -----------------------------
# فایل‌های داخلی پروژه
# -----------------------------
from astro_engine import calculate_natal_chart
from interpretations_natal_pro import generate_natal_pro_full
from report_builder import build_natal_pdf_report


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
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# -----------------------------
# حافظهٔ ساده برای state
# -----------------------------
user_state = {}
user_birth_data = {}


# -----------------------------
# شروع
# -----------------------------
@dp.message(Command("start"))
async def start_cmd(msg: types.Message):
    chat_id = msg.chat.id
    user_state[chat_id] = "ASK_NAME"

    await msg.answer(
        "سلام! 🌟\n"
        "برای ساخت گزارش ناتال حرفه‌ای (PRO + Composite)، لطفاً نام خود را وارد کن:"
    )


# -----------------------------
# دریافت نام
# -----------------------------
@dp.message(lambda m: user_state.get(m.chat.id) == "ASK_NAME")
async def ask_name(msg: types.Message):
    chat_id = msg.chat.id
    user_birth_data[chat_id] = {"name": msg.text.strip()}
    user_state[chat_id] = "ASK_DATE"

    await msg.answer("تاریخ تولد را وارد کن (مثال: 1375/05/21):")


# -----------------------------
# دریافت تاریخ
# -----------------------------
@dp.message(lambda m: user_state.get(m.chat.id) == "ASK_DATE")
async def ask_date(msg: types.Message):
    chat_id = msg.chat.id
    user_birth_data[chat_id]["jalali_date"] = msg.text.strip()
    user_state[chat_id] = "ASK_TIME"

    await msg.answer("ساعت تولد را وارد کن (مثال: 14:35):")


# -----------------------------
# دریافت ساعت
# -----------------------------
@dp.message(lambda m: user_state.get(m.chat.id) == "ASK_TIME")
async def ask_time(msg: types.Message):
    chat_id = msg.chat.id
    user_birth_data[chat_id]["time"] = msg.text.strip()
    user_state[chat_id] = "ASK_CITY"

    await msg.answer("شهر تولد را وارد کن (مثال: تهران):")


# -----------------------------
# دریافت شهر
# -----------------------------
@dp.message(lambda m: user_state.get(m.chat.id) == "ASK_CITY")
async def ask_city(msg: types.Message):
    chat_id = msg.chat.id
    user_birth_data[chat_id]["city"] = msg.text.strip()

    await msg.answer("⏳ در حال محاسبهٔ چارت تولد... لطفاً صبر کن.")

    try:
        # -----------------------------
        # محاسبه چارت تولد
        # -----------------------------
        chart_data = calculate_natal_chart(
            name=user_birth_data[chat_id]["name"],
            jalali_date=user_birth_data[chat_id]["jalali_date"],
            time=user_birth_data[chat_id]["time"],
            city=user_birth_data[chat_id]["city"]
        )

        logger.info("چارت تولد با موفقیت محاسبه شد.")

        # -----------------------------
        # تفسیر PRO + Composite
        # -----------------------------
        logger.info("شروع تفسیر حرفه‌ای (PRO + Composite)...")
        final_text = generate_natal_pro_full(chart_data)

        await msg.answer(
            "🌟 **گزارش ناتال حرفه‌ای شما آماده شد!**\n"
            "در ادامه متن کامل را مشاهده می‌کنید:",
            parse_mode=ParseMode.MARKDOWN
        )

        await msg.answer(final_text, parse_mode=ParseMode.MARKDOWN)

        # -----------------------------
        # ساخت PDF
        # -----------------------------
        logger.info("ساخت PDF نهایی...")
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


# -----------------------------
# اجرای ربات
# -----------------------------
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
