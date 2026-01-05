#============================
#symbol_handlers.py
#============≈===============
from aiogram import Router, types
from generator.symbol_engine import select_symbols
from generator.output_builder import format_symbol_list

router = Router()


def parse_symbol_command(text: str) -> dict:
    """
    پارس کردن ورودی کاربر برای دستور /symbol
    مثال ورودی:
    /symbol goal=wealth culture=iran energy=قدرت,فراوانی count=5 randomness=0.2
    """

    parts = text.split()
    params = {}

    # اگر فقط /symbol نوشته شده باشد
    if len(parts) == 1:
        return params

    # پردازش پارامترها
    for p in parts[1:]:
        if "=" in p:
            key, value = p.split("=", 1)
            key = key.strip().lower()
            value = value.strip()

            # انرژی‌ها می‌توانند لیستی باشند
            if key == "energy":
                params["energies"] = [e.strip() for e in value.split(",") if e.strip()]
            # count باید عدد باشد
            elif key == "count":
                params["count"] = int(value)
            # randomness باید float باشد
            elif key == "randomness":
                params["randomness"] = float(value)
            else:
                params[key] = value

    return params


@router.message(commands=["symbol"])
async def symbol_handler(message: types.Message):
    params = parse_symbol_command(message.text)

    # goal ضروری است
    goal = params.get("goal")
    if not goal:
        await message.answer(
            "لطفاً هدف را مشخص کن. مثال:\n"
            "/symbol goal=wealth\n\n"
            "پارامترهای قابل استفاده:\n"
            "goal=wealth/love/calm/... \n"
            "culture=iran/chinese/egyptian/... \n"
            "energy=قدرت,آرامش \n"
            "count=3 \n"
            "randomness=0.3"
        )
        return

    symbols = select_symbols(
        goal=goal,
        count=params.get("count", 3),
        primary_culture=params.get("culture"),
        preferred_cultures=None,
        energies=params.get("energies"),
        randomness=params.get("randomness", 0.25),
        exclude_ids=None,
    )

    if not symbols:
        await message.answer("هیچ نمادی پیدا نشد.")
        return

    output = format_symbol_list(symbols)
    await message.answer(output, parse_mode="Markdown")
