from aiogram import Router, types
from aiogram.fsm.context import FSMContext

from keyboards.start_menu import start_main_menu, back_to_main_menu
from states.natal_states import NatalStates
router = Router()


# -----------------------------
# /start → منوی اصلی
# -----------------------------
@router.message(commands=["start"])
async def start_cmd(message: types.Message):
    await message.answer(
        "سلام! 🌟\n"
        "به مرکز تحلیل‌های نجومی خوش آمدی.\n\n"
        "از منوی زیر یکی از سرویس‌ها را انتخاب کن:",
        reply_markup=start_main_menu()
    )


# -----------------------------
# شروع گزارش ناتال → ورود به FSM
# -----------------------------
@router.callback_query(lambda c: c.data == "start_natal")
async def start_natal(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(NatalStates.ASK_NAME)

    await callback.message.edit_text(
        "🔮 **گزارش ناتال حرفه‌ای**\n"
        "برای شروع لطفاً نام خود را وارد کن:",
        reply_markup=back_to_main_menu()
    )


# -----------------------------
# شروع ترانزیت‌ها
# -----------------------------
@router.callback_query(lambda c: c.data == "start_transits")
async def start_transits(callback: types.CallbackQuery):
    from keyboards import transits_main_menu

    await callback.message.edit_text(
        "📜 **منوی ترانزیت‌ها**\n"
        "ترانزیت‌های ۳۰ روز آینده را انتخاب کن:",
        reply_markup=transits_main_menu()
    )


# -----------------------------
# شروع Symbol Menu
# -----------------------------
@router.callback_query(lambda c: c.data == "start_symbol")
async def start_symbol(callback: types.CallbackQuery):
    from bot.keyboards.symbol_keyboards import goal_keyboard

    await callback.message.edit_text(
        "✨ **Symbol Menu**\n"
        "لطفاً هدف خود را انتخاب کن:",
        reply_markup=goal_keyboard()
    )


# -----------------------------
# دکمهٔ Back → بازگشت به منوی اصلی
# -----------------------------
@router.callback_query(lambda c: c.data == "back_main")
async def back_main(callback: types.CallbackQuery, state: FSMContext):
    # اگر کاربر وسط ناتال Back بزند، state ناتال را پاک می‌کنیم
    await state.clear()

    await callback.message.edit_text(
        "سلام دوباره! 🌟\n"
        "از منوی زیر یکی از سرویس‌ها را انتخاب کن:",
        reply_markup=start_main_menu()
    )
