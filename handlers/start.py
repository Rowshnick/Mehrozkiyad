from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from keyboards.start_menu.main_menu import start_main_menu, back_to_main_menu
from keyboards.start_menu.astrology_menu import astrology_menu
from keyboards.start_menu.symbol_menu import symbol_main_menu
from keyboards.start_menu.sajil_menu import sajil_menu
from keyboards.start_menu.tools_menu import tools_menu

from keyboards.transits_main_menu import transits_main_menu
from keyboards.symbol_keyboards import goal_keyboard

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
# شروع گزارش ناتال از منو (FSM)
# ----------------------------------------------------
@router.callback_query(F.data == "start_natal")
async def start_natal(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(NatalStates.ASK_NAME)
    await callback.message.edit_text(
        "🔮 **گزارش ناتال حرفه‌ای**\n"
        "برای شروع لطفاً نام خود را وارد کن:",
        reply_markup=back_to_main_menu()
    )


# ----------------------------------------------------
# شروع ترانزیت‌ها از منو
# ----------------------------------------------------
@router.callback_query(F.data == "start_transits")
async def start_transits(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "📜 **منوی ترانزیت‌ها**\n"
        "ترانزیت‌های ۳۰ روز آینده را انتخاب کن:",
        reply_markup=transits_main_menu()
    )


# ----------------------------------------------------
# منوی نمادشناسی
# ----------------------------------------------------
@router.callback_query(F.data == "menu_symbols")
async def menu_symbols(callback: types.CallbackQuery):
    # می‌توانی از symbol_main_menu هم استفاده کنی؛ اینجا مستقیم وارد انتخاب هدف می‌شویم
    await callback.message.edit_text(
        "✨ *نمادشناسی*\n"
        "هدف خود را انتخاب کن:",
        reply_markup=goal_keyboard()
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
# شروع سجیل از منو
# ----------------------------------------------------
@router.callback_query(F.data == "start_sajil")
async def start_sajil_from_menu(callback: types.CallbackQuery):
    await callback.message.answer(
        "برای محاسبهٔ سجیل، اطلاعات را به این فرم بفرست:\n"
        "`نام، تاریخ تولد (YYYY-MM-DD)، شهر تولد`\n"
        "مثال:\n"
        "`رُوشینا، 1995-04-12، مادرید`",
        parse_mode="Markdown"
    )


# ----------------------------------------------------
# مشاهدهٔ گزارش قبلی سجیل (فعلاً پیام ساده)
# ----------------------------------------------------
@router.callback_query(F.data == "sajil_last_report")
async def sajil_last_report(callback: types.CallbackQuery):
    await callback.message.answer(
        "📘 هنوز سیستم ذخیره و نمایش گزارش قبلی سجیل پیاده‌سازی نشده.\n"
        "می‌توانیم بعداً آن را به دیتابیس وصل کنیم."
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
# ابزارها – پاسخ‌های ساده فعلی
# ----------------------------------------------------
@router.callback_query(F.data == "tool_date_convert")
async def tool_date_convert(callback: types.CallbackQuery):
    await callback.message.answer("🕒 تبدیل تاریخ: این ابزار را بعداً می‌توانیم کامل پیاده‌سازی کنیم.")


@router.callback_query(F.data == "tool_timezone")
async def tool_timezone(callback: types.CallbackQuery):
    await callback.message.answer("🌍 تبدیل منطقه زمانی: بعداً می‌توانیم آن را به هستهٔ نجومی وصل کنیم.")


@router.callback_query(F.data == "tool_life_path")
async def tool_life_path(callback: types.CallbackQuery):
    await callback.message.answer("🔢 محاسبه عدد مسیر زندگی: می‌توانیم آن را به ماژول numerology سجیل وصل کنیم.")


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
