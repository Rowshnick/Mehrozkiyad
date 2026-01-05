#================================
#symbol_inline.py
#================================
from aiogram import Router, types

from generator.symbol_engine import select_symbols
from generator.output_builder import format_symbol_list

from bot.keyboards.symbol_keyboards import (
    goal_keyboard,
    culture_keyboard,
    energy_keyboard,
    GOALS,
    CULTURES,
    ENERGIES,
)

router = Router()


# -----------------------------
# مرحله ۱: شروع
# -----------------------------
@router.message(commands=["symbol_menu"])
async def symbol_menu_start(message: types.Message):
    await message.answer("🎯 لطفاً هدف خود را انتخاب کن:", reply_markup=goal_keyboard())


# -----------------------------
# مرحله ۲: انتخاب فرهنگ
# -----------------------------
@router.callback_query(lambda c: c.data.startswith("goal:"))
async def select_culture(callback: types.CallbackQuery):
    goal = callback.data.split(":")[1]

    await callback.message.edit_text(
        f"🎯 هدف انتخاب شد: {GOALS[goal]}\n\n🌍 حالا فرهنگ را انتخاب کن:",
        reply_markup=culture_keyboard(goal)
    )


# -----------------------------
# مرحله Back از فرهنگ → هدف
# -----------------------------
@router.callback_query(lambda c: c.data == "back:goal")
async def back_to_goal(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "🎯 لطفاً هدف خود را انتخاب کن:",
        reply_markup=goal_keyboard()
    )


# -----------------------------
# مرحله ۳: انتخاب انرژی
# -----------------------------
@router.callback_query(lambda c: c.data.startswith("culture:"))
async def select_energy(callback: types.CallbackQuery):
    _, goal, culture = callback.data.split(":")

    await callback.message.edit_text(
        f"🎯 هدف: {GOALS[goal]}\n"
        f"🌍 فرهنگ: {CULTURES[culture]}\n\n"
        f"✨ حالا انرژی را انتخاب کن:",
        reply_markup=energy_keyboard(goal, culture)
    )


# -----------------------------
# Back از انرژی → فرهنگ
# -----------------------------
@router.callback_query(lambda c: c.data.startswith("back:culture"))
async def back_to_culture(callback: types.CallbackQuery):
    _, _, goal = callback.data.split(":")
    await callback.message.edit_text(
        f"🎯 هدف انتخاب شد: {GOALS[goal]}\n\n🌍 حالا فرهنگ را انتخاب کن:",
        reply_markup=culture_keyboard(goal)
    )


# -----------------------------
# مرحله ۴: انتخاب نهایی نماد
# -----------------------------
@router.callback_query(lambda c: c.data.startswith("energy:"))
async def final_symbol(callback: types.CallbackQuery):
    _, goal, culture, energy = callback.data.split(":")

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
