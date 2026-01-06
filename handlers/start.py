from aiogram import Router, types
from bot.keyboards.start_menu import start_main_menu

router = Router()

@router.message(commands=["start"])
async def start_cmd(message: types.Message):
    await message.answer(
        "سلام! 🌟\n"
        "به مرکز تحلیل‌های نجومی خوش آمدی.\n\n"
        "لطفاً یکی از گزینه‌های زیر را انتخاب کن:",
        reply_markup=start_main_menu()
    )
    @router.callback_query(lambda c: c.data == "start_natal")
async def start_natal(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id

    # شروع state
    from bot_app import user_state, user_birth_data
    user_state[chat_id] = "ASK_NAME"
    user_birth_data[chat_id] = {}

    await callback.message.edit_text(
        "برای ساخت گزارش ناتال حرفه‌ای، لطفاً نام خود را وارد کن:"
    )
    @router.callback_query(lambda c: c.data == "start_transits")
async def start_transits(callback: types.CallbackQuery):
    from keyboards import transits_main_menu
    await callback.message.edit_text(
        "📜 **منوی ترانزیت‌ها:**",
        reply_markup=transits_main_menu()
    )
    @router.callback_query(lambda c: c.data == "start_symbol")
async def start_symbol(callback: types.CallbackQuery):
    from bot.keyboards.symbol_keyboards import goal_keyboard
    await callback.message.edit_text(
        "🎯 لطفاً هدف خود را انتخاب کن:",
        reply_markup=goal_keyboard()
    )
    
