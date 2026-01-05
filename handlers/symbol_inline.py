#================================
#symbol_inline.py
#================================
from aiogram import Router, types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from generator.symbol_engine import select_symbols
from generator.output_builder import format_symbol_list

router = Router()

# -----------------------------
# مرحله ۱: انتخاب هدف (Goal)
# -----------------------------

GOALS = {
    "wealth": "ثروت",
    "love": "عشق",
    "calm": "آرامش",
    "success": "موفقیت",
    "protection": "محافظت",
    "spiritual": "معنویت",
    "general": "عمومی",
}


@router.message(commands=["symbol_menu"])
async def symbol_menu_start(message: types.Message):
    kb = InlineKeyboardBuilder()

    for key, label in GOALS.items():
        kb.button(text=label, callback_data=f"goal:{key}")

    kb.adjust(2)
    await message.answer("🎯 لطفاً هدف خود را انتخاب کن:", reply_markup=kb.as_markup())


# -----------------------------
# مرحله ۲: انتخاب فرهنگ (Culture)
# -----------------------------

CULTURES = {
    "iranian": "ایران",
    "chinese": "چین",
    "egyptian": "مصر",
    "hindu": "هند",
    "celtic": "سلتی",
    "global": "جهانی",
    "none": "فرقی ندارد",
}


@router.callback_query(lambda c: c.data.startswith("goal:"))
async def select_culture(callback: types.CallbackQuery):
    goal = callback.data.split(":")[1]

    kb = InlineKeyboardBuilder()
    for key, label in CULTURES.items():
        kb.button(text=label, callback_data=f"culture:{goal}:{key}")

    kb.adjust(2)
    await callback.message.edit_text(
        f"🎯 هدف انتخاب شد: {GOALS[goal]}\n\n🌍 حالا فرهنگ را انتخاب کن:",
        reply_markup=kb.as_markup()
    )


# -----------------------------
# مرحله ۳: انتخاب انرژی (Energy)
# -----------------------------

ENERGIES = {
    "power": "قدرت",
    "calm": "آرامش",
    "growth": "رشد",
    "balance": "تعادل",
    "light": "نور",
    "none": "فرقی ندارد",
}


@router.callback_query(lambda c: c.data.startswith("culture:"))
async def select_energy(callback: types.CallbackQuery):
    _, goal, culture = callback.data.split(":")

    kb = InlineKeyboardBuilder()
    for key, label in ENERGIES.items():
        kb.button(text=label, callback_data=f"energy:{goal}:{culture}:{key}")

    kb.adjust(2)
    await callback.message.edit_text(
        f"🎯 هدف: {GOALS[goal]}\n"
        f"🌍 فرهنگ: {CULTURES[culture]}\n\n"
        f"✨ حالا انرژی را انتخاب کن:",
        reply_markup=kb.as_markup()
    )


# -----------------------------
# مرحله ۴: انتخاب نهایی نماد
# -----------------------------

@router.callback_query(lambda c: c.data.startswith("energy:"))
async def final_symbol(callback: types.CallbackQuery):
    _, goal, culture, energy = callback.data.split(":")

    # تبدیل none به None
    culture = None if culture == "none" else culture
    energies = None if energy == "none" else [ENERGIES[energy]]

    symbols = select_symbols(
        goal=goal,
        count=3,
        primary_culture=culture,
        energies=energies,
        randomness=0.25,
    )

    output = format_symbol_list(symbols)

    await callback.message.edit_text(
        f"🎯 هدف: {GOALS[goal]}\n"
        f"🌍 فرهنگ: {CULTURES.get(culture, '—')}\n"
        f"✨ انرژی: {ENERGIES.get(energy, '—')}\n\n"
        f"{output}",
        parse_mode="Markdown"
    )
