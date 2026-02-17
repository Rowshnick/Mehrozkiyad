#================================
#symbol_inline.py
#================================
from aiogram import Router, types, F

from keyboards.symbol_keyboards import (
    goal_keyboard,
    culture_keyboard,
    energy_keyboard,
    symbol_keyboard,
)

router = Router()


# -----------------------------
# شروع نمادشناسی از دکمهٔ قدیمی start_symbol (اگر جایی استفاده شود)
# -----------------------------
@router.callback_query(F.data == "start_symbol")
async def start_symbol(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "✨ **Symbol Menu**\n"
        "لطفاً هدف خود را انتخاب کن:",
        reply_markup=goal_keyboard()
    )


# -----------------------------
# انتخاب هدف (الگوی قدیمی goal:...)
# -----------------------------
@router.callback_query(F.data.startswith("goal:"))
async def choose_goal(callback: types.CallbackQuery):
    goal_id = callback.data.split(":", 1)[1]

    await callback.message.edit_text(
        "🌍 حالا فرهنگ/فضای نماد را انتخاب کن:",
        reply_markup=culture_keyboard(goal_id)
    )


# -----------------------------
# انتخاب هدف از منوی جدید (symbol_goal_...)
# -----------------------------
@router.callback_query(F.data.startswith("symbol_goal_"))
async def choose_goal_from_new_menu(callback: types.CallbackQuery):
    # مثال: symbol_goal_love → love
    goal_id = callback.data.replace("symbol_goal_", "", 1)

    await callback.message.edit_text(
        "🌍 حالا فرهنگ/فضای نماد را انتخاب کن:",
        reply_markup=culture_keyboard(goal_id)
    )


# -----------------------------
# انتخاب فرهنگ
# -----------------------------
@router.callback_query(F.data.startswith("culture:"))
async def choose_culture(callback: types.CallbackQuery):
    # مثال: culture:<goal_id>:<culture_id>
    _, goal_id, culture_id = callback.data.split(":", 2)

    await callback.message.edit_text(
        "⚡ حالا نوع انرژی را انتخاب کن:",
        reply_markup=energy_keyboard(goal_id, culture_id)
    )


# -----------------------------
# انتخاب انرژی
# -----------------------------
@router.callback_query(F.data.startswith("energy:"))
async def choose_energy(callback: types.CallbackQuery):
    # مثال: energy:<goal_id>:<culture_id>:<energy_id>
    _, goal_id, culture_id, energy_id = callback.data.split(":", 3)

    await callback.message.edit_text(
        "✨ بر اساس انتخاب تو، این نمادها پیشنهاد می‌شوند:",
        reply_markup=symbol_keyboard(goal_id, culture_id, energy_id)
    )


# -----------------------------
# نمایش نماد نهایی
# -----------------------------
@router.callback_query(F.data.startswith("symbol:"))
async def show_symbol(callback: types.CallbackQuery):
    _, symbol_id = callback.data.split(":", 1)

    await callback.message.edit_text(
        f"🔯 نماد انتخابی تو: {symbol_id}\n\n"
        "اگر خواستی می‌توانی دوباره از منوی اصلی شروع کنی یا نماد دیگری را تست کنی."
    )
