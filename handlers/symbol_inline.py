#================================
#symbol_inline.py
#================================
from aiogram import Router, types

from keyboards.symbol_keyboards import (
    goal_keyboard,
    culture_keyboard,
    energy_keyboard,
    symbol_keyboard,
)

router = Router()


# -----------------------------
# انتخاب هدف (این در start.py با start_symbol شروع می‌شود)
# -----------------------------
@router.callback_query(lambda c: c.data.startswith("goal:"))
async def choose_goal(callback: types.CallbackQuery):
    goal_id = callback.data.split(":", 1)[1]

    await callback.message.edit_text(
        "🌍 حالا فرهنگ/فضای نماد را انتخاب کن:",
        reply_markup=culture_keyboard(goal_id)
    )


# -----------------------------
# انتخاب فرهنگ
# -----------------------------
@router.callback_query(lambda c: c.data.startswith("culture:"))
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
@router.callback_query(lambda c: c.data.startswith("energy:"))
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
@router.callback_query(lambda c: c.data.startswith("symbol:"))
async def show_symbol(callback: types.CallbackQuery):
    # مثال: symbol:<symbol_id>
    _, symbol_id = callback.data.split(":", 1)

    # این‌جا می‌توانی توضیح نماد را از یک دیکشنری/فایل بخوانی
    await callback.message.edit_text(
        f"🔯 نماد انتخابی تو: {symbol_id}\n\n"
        "اگر خواستی می‌توانی دوباره از منوی اصلی شروع کنی یا نماد دیگری را تست کنی."
    )
