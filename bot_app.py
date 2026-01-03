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
from datetime import date, timedelta
from aiogram import types

# ایمپورت منوها از فایل keyboards.py
from keyboards import (
    transits_main_menu,
    submenu_general,
    submenu_love,
    submenu_karmic,
    submenu_job,
    submenu_challenge,
)
# -----------------------------
# فایل‌های داخلی پروژه
# -----------------------------
from astro_engine import calculate_natal_chart
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


# =========================
#   تابع لود چارت کاربر
# =========================

def load_user_chart(user_id):
    # نسخه واقعی را خودت داری
    return None



# =========================
#   دستورات اصلی ترانزیت‌ها
# =========================

@dp.message_handler(commands=["transits"])
async def cmd_transits(message: types.Message):
    user_id = message.from_user.id
    natal_chart = load_user_chart(user_id)
    if not natal_chart:
        await message.reply("❗ ابتدا باید چارت ناتال خود را ثبت کنید.")
        return

    start = date.today()
    end = start + timedelta(days=30)
    result = analyze_transits_for_range(natal_chart, start, end)

    await message.reply(result or "✨ ترانزیت مهمی یافت نشد.")



@dp.message_handler(commands=["transits_today"])
async def cmd_transits_today(message: types.Message):
    user_id = message.from_user.id
    natal_chart = load_user_chart(user_id)
    if not natal_chart:
        await message.reply("❗ ابتدا باید چارت ناتال خود را ثبت کنید.")
        return

    today = date.today()
    result = analyze_transits_for_range(natal_chart, today, today)

    await message.reply(result or "✨ امروز ترانزیت مهمی یافت نشد.")



# =========================
#   عشق
# =========================

@dp.message_handler(commands=["transits_love"])
async def cmd_transits_love(message: types.Message):
    user_id = message.from_user.id
    natal_chart = load_user_chart(user_id)
    if not natal_chart:
        await message.reply("❗ ابتدا باید چارت ناتال خود را ثبت کنید.")
        return

    start = date.today()
    end = start + timedelta(days=30)
    full = analyze_transits_for_range(natal_chart, start, end)
    love = [l for l in full.split("\n") if "عشق" in l]

    await message.reply("💞 ترانزیت‌های عاشقانه:\n\n" + "\n".join(love) if love else "💞 ترانزیت عاشقانه‌ای یافت نشد.")



@dp.message_handler(commands=["transits_love_today"])
async def cmd_transits_love_today(message: types.Message):
    user_id = message.from_user.id
    natal_chart = load_user_chart(user_id)
    if not natal_chart:
        await message.reply("❗ ابتدا باید چارت ناتال خود را ثبت کنید.")
        return

    today = date.today()
    full = analyze_transits_for_range(natal_chart, today, today)
    love = [l for l in full.split("\n") if "عشق" in l]

    await message.reply("💞 ترانزیت‌های عاشقانه امروز:\n\n" + "\n".join(love) if love else "💞 امروز ترانزیت عاشقانه‌ای نیست.")



# =========================
#   کارما
# =========================

@dp.message_handler(commands=["transits_karmic"])
async def cmd_transits_karmic(message: types.Message):
    user_id = message.from_user.id
    natal_chart = load_user_chart(user_id)
    if not natal_chart:
        await message.reply("❗ ابتدا باید چارت ناتال خود را ثبت کنید.")
        return

    start = date.today()
    end = start + timedelta(days=30)
    full = analyze_transits_for_range(natal_chart, start, end)
    karmic = [l for l in full.split("\n") if "کارما" in l]

    await message.reply("🜂 ترانزیت‌های کارمایی:\n\n" + "\n".join(karmic) if karmic else "🜂 ترانزیت کارمایی یافت نشد.")



@dp.message_handler(commands=["transits_karmic_today"])
async def cmd_transits_karmic_today(message: types.Message):
    user_id = message.from_user.id
    natal_chart = load_user_chart(user_id)
    if not natal_chart:
        await message.reply("❗ ابتدا باید چارت ناتال خود را ثبت کنید.")
        return

    today = date.today()
    full = analyze_transits_for_range(natal_chart, today, today)
    karmic = [l for l in full.split("\n") if "کارما" in l]

    await message.reply("🜂 ترانزیت‌های کارمایی امروز:\n\n" + "\n".join(karmic) if karmic else "🜂 امروز ترانزیت کارمایی نیست.")



# =========================
#   شغل
# =========================

@dp.message_handler(commands=["transits_job"])
async def cmd_transits_job(message: types.Message):
    user_id = message.from_user.id
    natal_chart = load_user_chart(user_id)
    if not natal_chart:
        await message.reply("❗ ابتدا باید چارت ناتال خود را ثبت کنید.")
        return

    start = date.today()
    end = start + timedelta(days=30)
    full = analyze_transits_for_range(natal_chart, start, end)
    job = [l for l in full.split("\n") if "شغل" in l or "MC" in l]

    await message.reply("💼 ترانزیت‌های شغلی:\n\n" + "\n".join(job) if job else "💼 ترانزیت شغلی یافت نشد.")



@dp.message_handler(commands=["transits_job_today"])
async def cmd_transits_job_today(message: types.Message):
    user_id = message.from_user.id
    natal_chart = load_user_chart(user_id)
    if not natal_chart:
        await message.reply("❗ ابتدا باید چارت ناتال خود را ثبت کنید.")
        return

    today = date.today()
    full = analyze_transits_for_range(natal_chart, today, today)
    job = [l for l in full.split("\n") if "شغل" in l or "MC" in l]

    await message.reply("💼 ترانزیت‌های شغلی امروز:\n\n" + "\n".join(job) if job else "💼 امروز ترانزیت شغلی نیست.")



# =========================
#   چالش
# =========================

@dp.message_handler(commands=["transits_challenge"])
async def cmd_transits_challenge(message: types.Message):
    user_id = message.from_user.id
    natal_chart = load_user_chart(user_id)
    if not natal_chart:
        await message.reply("❗ ابتدا باید چارت ناتال خود را ثبت کنید.")
        return

    start = date.today()
    end = start + timedelta(days=30)
    full = analyze_transits_for_range(natal_chart, start, end)
    challenge = [l for l in full.split("\n") if "چالش" in l]

    await message.reply("⚠️ ترانزیت‌های چالشی:\n\n" + "\n".join(challenge) if challenge else "⚠️ ترانزیت چالشی یافت نشد.")



@dp.message_handler(commands=["transits_challenge_today"])
async def cmd_transits_challenge_today(message: types.Message):
    user_id = message.from_user.id
    natal_chart = load_user_chart(user_id)
    if not natal_chart:
        await message.reply("❗ ابتدا باید چارت ناتال خود را ثبت کنید.")
        return

    today = date.today()
    full = analyze_transits_for_range(natal_chart, today, today)
    challenge = [l for l in full.split("\n") if "چالش" in l]

    await message.reply("⚠️ ترانزیت‌های چالشی امروز:\n\n" + "\n".join(challenge) if challenge else "⚠️ امروز ترانزیت چالشی نیست.")



# =========================
#   منوی حرفه‌ای
# =========================

@dp.message_handler(commands=["menu_transits"])
async def cmd_menu_transits(message: types.Message):
    await message.reply("📜 **منوی ترانزیت‌ها:**", reply_markup=transits_main_menu())



# =========================
#   Callback Handlers
# =========================

@dp.callback_query_handler(lambda c: c.data == "menu_general")
async def cb_general(callback: types.CallbackQuery):
    await callback.message.edit_text("🔮 **ترانزیت‌های کلی:**", reply_markup=submenu_general())


@dp.callback_query_handler(lambda c: c.data == "menu_love")
async def cb_love(callback: types.CallbackQuery):
    await callback.message.edit_text("💞 **ترانزیت‌های عاشقانه:**", reply_markup=submenu_love())


@dp.callback_query_handler(lambda c: c.data == "menu_karmic")
async def cb_karmic(callback: types.CallbackQuery):
    await callback.message.edit_text("🜂 **ترانزیت‌های کارمایی:**", reply_markup=submenu_karmic())


@dp.callback_query_handler(lambda c: c.data == "menu_job")
async def cb_job(callback: types.CallbackQuery):
    await callback.message.edit_text("💼 **ترانزیت‌های شغلی:**", reply_markup=submenu_job())


@dp.callback_query_handler(lambda c: c.data == "menu_challenge")
async def cb_challenge(callback: types.CallbackQuery):
    await callback.message.edit_text("⚠️ **ترانزیت‌های چالشی:**", reply_markup=submenu_challenge())


@dp.callback_query_handler(lambda c: c.data == "back_to_main")
async def cb_back(callback: types.CallbackQuery):
    await callback.message.edit_text("📜 **منوی ترانزیت‌ها:**", reply_markup=transits_main_menu())


# -----------------------------
# اجرای ربات
# -----------------------------
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
