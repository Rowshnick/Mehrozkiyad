#--------‐-------------------‐-----------
#start.py
#--------‐-------------------‐-----------

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from keyboards.start_menu.main_menu import start_main_menu, back_to_main_menu
from keyboards.start_menu.astrology_menu import astrology_menu
from keyboards.start_menu.symbol_menu import symbol_main_menu
from keyboards.start_menu.sajil_menu import sajil_menu
from keyboards.start_menu.tools_menu import tools_menu

from states.natal_states import NatalStates

router = Router()


# ----------------------------------------------------
# /start → نمایش منوی اصلی
# ----------------------------------------------------
@router.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "سلام رُوشینا 🌙\n"
        "به مرکز تحلیل‌های نجومی خوش آمدی.\n"
        "از منوی زیر یکی از سرویس‌ها را انتخاب کن:",
        reply_markup=start_main_menu()
    )


# ----------------------------------------------------
# منوی تحلیل‌های نجومی
# ----------------------------------------------------
@router.callback_query(F.data == "menu_astrology")
async def menu_astrology(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "🔮 *تحلیل‌های نجومی*\n"
        "یکی از گزینه‌ها را انتخاب کن:",
        reply_markup=astrology_menu()
    )


# ----------------------------------------------------
# منوی نمادشناسی
# ----------------------------------------------------
@router.callback_query(F.data == "menu_symbols")
async def menu_symbols(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "✨ *نمادشناسی*\n"
        "هدف خود را انتخاب کن:",
        reply_markup=symbol_main_menu()
    )


# ----------------------------------------------------
# منوی سجیل
# ----------------------------------------------------
@router.callback_query(F.data == "menu_sajil")
async def menu_sajil(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "🧿 *سجیل شخصی*\n"
        "چه کاری می‌خواهی انجام دهی؟",
        reply_markup=sajil_menu()
    )


# ----------------------------------------------------
# منوی ابزارها
# ----------------------------------------------------
@router.callback_query(F.data == "menu_tools")
async def menu_tools_handler(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "⚙️ *ابزارهای کمکی*\n"
        "یکی از ابزارهای زیر را انتخاب کن:",
        reply_markup=tools_menu()
    )


# ----------------------------------------------------
# بازگشت به منوی اصلی
# ----------------------------------------------------
@router.callback_query(F.data == "back_main")
async def back_main(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "سلام دوباره رُوشینا 🌟\n"
        "از منوی زیر یکی از سرویس‌ها را انتخاب کن:",
        reply_markup=start_main_menu()
    )
