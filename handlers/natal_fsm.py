from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from astrology_core import calculate_natal_chart
from interpretations_natal_pro import generate_natal_pro_full
from report_builder import build_natal_pdf_report

from states.natal_states import NatalStates

router = Router()


# -----------------------------
# مرحله ۱: دریافت نام
# -----------------------------
@router.message(NatalStates.ASK_NAME)
async def natal_ask_name(message: types.Message, state: FSMContext):
    name = message.text.strip()
    await state.update_data(name=name)

    await state.set_state(NatalStates.ASK_DATE)
    await message.answer("تاریخ تولد را وارد کن (مثال: 1375/05/21):")


# -----------------------------
# مرحله ۲: دریافت تاریخ
# -----------------------------
@router.message(NatalStates.ASK_DATE)
async def natal_ask_date(message: types.Message, state: FSMContext):
    jalali_date = message.text.strip()
    await state.update_data(jalali_date=jalali_date)

    await state.set_state(NatalStates.ASK_TIME)
    await message.answer("ساعت تولد را وارد کن (مثال: 14:35):")


# -----------------------------
# مرحله ۳: دریافت ساعت
# -----------------------------
@router.message(NatalStates.ASK_TIME)
async def natal_ask_time(message: types.Message, state: FSMContext):
    time_str = message.text.strip()
    await state.update_data(time=time_str)

    await state.set_state(NatalStates.ASK_CITY)
    await message.answer("شهر تولد را وارد کن (مثال: تهران):")


# -----------------------------
# مرحله ۴: دریافت شهر و محاسبه نهایی
# -----------------------------
@router.message(NatalStates.ASK_CITY)
async def natal_ask_city(message: types.Message, state: FSMContext):
    city = message.text.strip()
    await state.update_data(city=city)

    await message.answer("⏳ در حال محاسبهٔ چارت تولد... لطفاً صبر کن.")

    data = await state.get_data()

    try:
        chart_data = calculate_natal_chart(
            name=data["name"],
            jalali_date=data["jalali_date"],
            time=data["time"],
            city=data["city"],
        )

        final_text = generate_natal_pro_full(chart_data)

        await message.answer(
            "🌟 **گزارش ناتال حرفه‌ای شما آماده شد!**",
            parse_mode=ParseMode.MARKDOWN,
        )
        await message.answer(final_text, parse_mode=ParseMode.MARKDOWN)

        pdf_bytes = build_natal_pdf_report(chart_data, final_text)

        await message.bot.send_document(
            message.chat.id,
            document=types.BufferedInputFile(
                pdf_bytes, filename="natal_report_pro.pdf"
            ),
            caption="📄 گزارش کامل ناتال PRO + Composite",
        )

    except Exception:
        await message.answer("❌ خطایی رخ داد. لطفاً دوباره تلاش کن.")
    finally:
        await state.clear()
