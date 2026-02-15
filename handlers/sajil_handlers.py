# handlers/sajil_handlers.py

from aiogram import Router, types
from aiogram.filters import Command

from sajil import SajilInput, compute_sajil, format_sajil_text

router = Router()


@router.message(Command("sajil"))
async def sajil_start(message: types.Message):
    await message.answer(
        "برای محاسبهٔ سجیل، اطلاعات را به این فرم بفرست:\n"
        "`نام، تاریخ تولد (YYYY-MM-DD)، شهر تولد`\n"
        "مثال:\n"
        "`رُوشینا، 1995-04-12، مادرید`",
        parse_mode="Markdown"
    )


@router.message()
async def sajil_process(message: types.Message):
    try:
        parts = [p.strip() for p in message.text.split("،")]
        if len(parts) < 2:
            await message.answer("لطفاً حداقل نام و تاریخ تولد را به فرم گفته‌شده وارد کن.")
            return

        first_name = parts[0]
        birth_date = parts[1]
        birth_city = parts[2] if len(parts) > 2 else None

        data = SajilInput(
            first_name=first_name,
            birth_date=birth_date,
            birth_city=birth_city,
        )

        result = compute_sajil(data)
        text = format_sajil_text(result)
        await message.answer(text, parse_mode="Markdown")

    except Exception as e:
        await message.answer(f"⚠️ خطا در پردازش سجیل:\n{e}")
