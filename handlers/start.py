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
