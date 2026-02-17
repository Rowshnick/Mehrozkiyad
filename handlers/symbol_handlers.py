# ================================
#   symbol_handlers.py
#   نسخهٔ اصلاح‌شده برای Aiogram 3.x
# ================================

from aiogram import Router, types
from aiogram.filters import Command

from symbol_lib.generator.symbol_engine import select_symbols
from symbol_lib.generator.output_builder import format_symbol_list

router = Router()


def parse_symbol_command(text: str) -> dict:
    """
    پارس‌کردن دستور /symbol
    مثال:
        /symbol goal=love count=3 culture=iran
    """
    params = {
        "goal": None,
        "count": 1,
        "primary_culture": None,
        "preferred_cultures": None,
        "energies": None,
    }

    parts = text.split()
    for p in parts[1:]:
        if "=" in p:
            key, value = p.split("=", 1)
            key = key.strip().lower()
            value = value.strip()

            if key == "goal":
                params["goal"] = value

            elif key == "count":
                try:
                    params["count"] = int(value)
                except:
                    pass

            elif key == "culture":
                params["primary_culture"] = value

            elif key == "cultures":
                params["preferred_cultures"] = value.split(",")

            elif key == "energies":
                params["energies"] = value.split(",")

    return params


@router.message(Command("symbol"))
async def symbol_handler(message: types.Message):
    params = parse_symbol_command(message.text)

    goal = params.get("goal")
    count = params.get("count", 1)
    primary_culture = params.get("primary_culture")
    preferred_cultures = params.get("preferred_cultures")
    energies = params.get("energies")

    if not goal:
        await message.answer(
            "❗ لطفاً هدف را مشخص کنید.\n"
            "مثال:\n"
            "`/symbol goal=love count=3`",
            parse_mode="Markdown"
        )
        return

    symbols = select_symbols(
        goal=goal,
        count=count,
        primary_culture=primary_culture,
        preferred_cultures=preferred_cultures,
        energies=energies,
    )

    output = format_symbol_list(symbols)
    await message.answer(output, parse_mode="Markdown")


@router.message(Command("symbol_simple"))
async def symbol_simple_handler(message: types.Message):
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("❗ مثال:\n`/symbol_simple love`", parse_mode="Markdown")
        return

    goal = parts[1]
    symbols = select_symbols(goal=goal, count=1)
    output = format_symbol_list(symbols)

    await message.answer(output, parse_mode="Markdown")
