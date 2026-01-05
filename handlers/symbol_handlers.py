from aiogram import Router, types
from generator.symbol_engine import select_symbols
from generator.output_builder import format_symbol_list

router = Router()

@router.message(commands=["symbol"])
async def symbol_handler(message: types.Message):
    text = message.text.strip().split()

    # مثال: /symbol wealth iran
    # text[0] = /symbol
    # text[1] = goal
    # text[2] = culture (اختیاری)

    if len(text) < 2:
        await message.answer("لطفاً هدف را مشخص کن. مثال:\n/symbol wealth")
        return

    goal = text[1]
    culture = text[2] if len(text) > 2 else None

    symbols = select_symbols(
        goal=goal,
        count=3,
        primary_culture=culture,
        preferred_cultures=None,
        energies=None,
        randomness=0.25,
    )

    if not symbols:
        await message.answer("هیچ نمادی پیدا نشد.")
        return

    output = format_symbol_list(symbols)
    await message.answer(output, parse_mode="Markdown")
