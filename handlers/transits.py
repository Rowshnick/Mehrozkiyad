#========≈===========================
# transits.py
#========≈===========================

from aiogram import Router, types, F
from aiogram.filters import Command
from datetime import date, timedelta

from core.transits_engine import analyze_transits_for_range

router = Router()


# -----------------------------
# لود چارت کاربر (نسخهٔ ساده)
# -----------------------------
def load_user_chart(user_id):
    # نسخهٔ واقعی را خودت پیاده‌سازی می‌کنی
    return None


# -----------------------------
# ترانزیت کلی ۳۰ روز آینده (دستور متنی)
# -----------------------------
@router.message(Command("transits"))
async def cmd_transits(message: types.Message):
    user_id = message.from_user.id
    natal_chart = load_user_chart(user_id)

    if not natal_chart:
        await message.reply("❗ ابتدا باید چارت ناتال خود را ثبت کنید.")
        return

    start = date.today()
    end = start + timedelta(days=30)

    result = analyze_transits_for_range(natal_chart, start, end)
    await message.reply(result or "✨ ترانزیت مهمی یافت نشد.")


# -----------------------------
# ترانزیت امروز (دستور متنی)
# -----------------------------
@router.message(Command("transits_today"))
async def cmd_transits_today(message: types.Message):
    user_id = message.from_user.id
    natal_chart = load_user_chart(user_id)

    if not natal_chart:
        await message.reply("❗ ابتدا باید چارت ناتال خود را ثبت کنید.")
        return

    today = date.today()
    result = analyze_transits_for_range(natal_chart, today, today)

    await message.reply(result or "✨ امروز ترانزیت مهمی یافت نشد.")


# -----------------------------
# ترانزیت‌های عاشقانه (دستور متنی)
# -----------------------------
@router.message(Command("transits_love"))
async def cmd_transits_love(message: types.Message):
    user_id = message.from_user.id
    natal_chart = load_user_chart(user_id)

    if not natal_chart:
        await message.reply("❗ ابتدا باید چارت ناتال خود را ثبت کنید.")
        return

    start = date.today()
    end = start + timedelta(days=30)

    full = analyze_transits_for_range(natal_chart, start, end)
    love = [l for l in full.split("\n") if "عشق" in l]

    await message.reply(
        "💞 ترانزیت‌های عاشقانه:\n\n" + "\n".join(love)
        if love else "💞 ترانزیت عاشقانه‌ای یافت نشد."
    )


# -----------------------------
# ترانزیت‌های عاشقانه امروز (دستور متنی)
# -----------------------------
@router.message(Command("transits_love_today"))
async def cmd_transits_love_today(message: types.Message):
    user_id = message.from_user.id
    natal_chart = load_user_chart(user_id)

    if not natal_chart:
        await message.reply("❗ ابتدا باید چارت ناتال خود را ثبت کنید.")
        return

    today = date.today()
    full = analyze_transits_for_range(natal_chart, today, today)
    love = [l for l in full.split("\n") if "عشق" in l]

    await message.reply(
        "💞 ترانزیت‌های عاشقانه امروز:\n\n" + "\n".join(love)
        if love else "💞 امروز ترانزیت عاشقانه‌ای نیست."
    )


# -----------------------------
# ترانزیت‌های کارمایی (دستور متنی)
# -----------------------------
@router.message(Command("transits_karmic"))
async def cmd_transits_karmic(message: types.Message):
    user_id = message.from_user.id
    natal_chart = load_user_chart(user_id)

    if not natal_chart:
        await message.reply("❗ ابتدا باید چارت ناتال خود را ثبت کنید.")
        return

    start = date.today()
    end = start + timedelta(days=30)

    full = analyze_transits_for_range(natal_chart, start, end)
    karmic = [l for l in full.split("\n") if "کارما" in l]

    await message.reply(
        "🜂 ترانزیت‌های کارمایی:\n\n" + "\n".join(karmic)
        if karmic else "🜂 ترانزیت کارمایی یافت نشد."
    )


# -----------------------------
# ترانزیت‌های کارمایی امروز (دستور متنی)
# -----------------------------
@router.message(Command("transits_karmic_today"))
async def cmd_transits_karmic_today(message: types.Message):
    user_id = message.from_user.id
    natal_chart = load_user_chart(user_id)

    if not natal_chart:
        await message.reply("❗ ابتدا باید چارت ناتال خود را ثبت کنید.")
        return

    today = date.today()
    full = analyze_transits_for_range(natal_chart, today, today)
    karmic = [l for l in full.split("\n") if "کارما" in l]

    await message.reply(
        "🜂 ترانزیت‌های کارمایی امروز:\n\n" + "\n".join(karmic)
        if karmic else "🜂 امروز ترانزیت کارمایی نیست."
    )


# -----------------------------
# ترانزیت‌های شغلی (دستور متنی)
# -----------------------------
@router.message(Command("transits_job"))
async def cmd_transits_job(message: types.Message):
    user_id = message.from_user.id
    natal_chart = load_user_chart(user_id)

    if not natal_chart:
        await message.reply("❗ ابتدا باید چارت ناتال خود را ثبت کنید.")
        return

    start = date.today()
    end = start + timedelta(days=30)

    full = analyze_transits_for_range(natal_chart, start, end)
    job = [l for l in full.split("\n") if "شغل" in l or "MC" in l]

    await message.reply(
        "💼 ترانزیت‌های شغلی:\n\n" + "\n".join(job)
        if job else "💼 ترانزیت شغلی یافت نشد."
    )


# -----------------------------
# ترانزیت‌های شغلی امروز (دستور متنی)
# -----------------------------
@router.message(Command("transits_job_today"))
async def cmd_transits_job_today(message: types.Message):
    user_id = message.from_user.id
    natal_chart = load_user_chart(user_id)

    if not natal_chart:
        await message.reply("❗ ابتدا باید چارت ناتال خود را ثبت کنید.")
        return

    today = date.today()
    full = analyze_transits_for_range(natal_chart, today, today)
    job = [l for l in full.split("\n") if "شغل" in l or "MC" in l]

    await message.reply(
        "💼 ترانزیت‌های شغلی امروز:\n\n" + "\n".join(job)
        if job else "💼 امروز ترانزیت شغلی نیست."
    )


# -----------------------------
# ترانزیت‌های چالشی (دستور متنی)
# -----------------------------
@router.message(Command("transits_challenge"))
async def cmd_transits_challenge(message: types.Message):
    user_id = message.from_user.id
    natal_chart = load_user_chart(user_id)

    if not natal_chart:
        await message.reply("❗ ابتدا باید چارت ناتال خود را ثبت کنید.")
        return

    start = date.today()
    end = start + timedelta(days=30)

    full = analyze_transits_for_range(natal_chart, start, end)
    challenge = [l for l in full.split("\n") if "چالش" in l]

    await message.reply(
        "⚠️ ترانزیت‌های چالشی:\n\n" + "\n".join(challenge)
        if challenge else "⚠️ ترانزیت چالشی یافت نشد."
    )


# -----------------------------
# ترانزیت‌های چالشی امروز (دستور متنی)
# -----------------------------
@router.message(Command("transits_challenge_today"))
async def cmd_transits_challenge_today(message: types.Message):
    user_id = message.from_user.id
    natal_chart = load_user_chart(user_id)

    if not natal_chart:
        await message.reply("❗ ابتدا باید چارت ناتال خود را ثبت کنید.")
        return

    today = date.today()
    full = analyze_transits_for_range(natal_chart, today, today)
    challenge = [l for l in full.split("\n") if "چالش" in l]

    await message.reply(
        "⚠️ ترانزیت‌های چالشی امروز:\n\n" + "\n".join(challenge)
        if challenge else "⚠️ امروز ترانزیت چالشی نیست."
    )


# -----------------------------
# ترانزیت ۳۰ روز آینده از منو (callback)
# -----------------------------
@router.callback_query(F.data == "transits_30")
async def cb_transits_30(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    natal_chart = load_user_chart(user_id)

    if not natal_chart:
        await callback.message.answer("❗ ابتدا باید چارت ناتال خود را ثبت کنید.")
        return

    start = date.today()
    end = start + timedelta(days=30)

    result = analyze_transits_for_range(natal_chart, start, end)
    await callback.message.answer(result or "✨ ترانزیت مهمی یافت نشد.")


# -----------------------------
# ترانزیت امروز از منو (callback)
# -----------------------------
@router.callback_query(F.data == "transits_today")
async def cb_transits_today(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    natal_chart = load_user_chart(user_id)

    if not natal_chart:
        await callback.message.answer("❗ ابتدا باید چارت ناتال خود را ثبت کنید.")
        return

    today = date.today()
    result = analyze_transits_for_range(natal_chart, today, today)

    await callback.message.answer(result or "✨ امروز ترانزیت مهمی یافت نشد.")


# -----------------------------
# ترانزیت‌های عاشقانه از منو (callback)
# -----------------------------
@router.callback_query(F.data == "transits_love")
async def cb_transits_love(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    natal_chart = load_user_chart(user_id)

    if not natal_chart:
        await callback.message.answer("❗ ابتدا باید چارت ناتال خود را ثبت کنید.")
        return

    start = date.today()
    end = start + timedelta(days=30)

    full = analyze_transits_for_range(natal_chart, start, end)
    love = [l for l in full.split("\n") if "عشق" in l]

    await callback.message.answer(
        "💞 ترانزیت‌های عاشقانه:\n\n" + "\n".join(love)
        if love else "💞 ترانزیت عاشقانه‌ای یافت نشد."
    )


# -----------------------------
# ترانزیت‌های کارمایی از منو (callback)
# -----------------------------
@router.callback_query(F.data == "transits_karmic")
async def cb_transits_karmic(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    natal_chart = load_user_chart(user_id)

    if not natal_chart:
        await callback.message.answer("❗ ابتدا باید چارت ناتال خود را ثبت کنید.")
        return

    start = date.today()
    end = start + timedelta(days=30)

    full = analyze_transits_for_range(natal_chart, start, end)
    karmic = [l for l in full.split("\n") if "کارما" in l]

    await callback.message.answer(
        "🜂 ترانزیت‌های کارمایی:\n\n" + "\n".join(karmic)
        if karmic else "🜂 ترانزیت کارمایی یافت نشد."
    )


# -----------------------------
# ترانزیت‌های شغلی از منو (callback)
# -----------------------------
@router.callback_query(F.data == "transits_job")
async def cb_transits_job(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    natal_chart = load_user_chart(user_id)

    if not natal_chart:
        await callback.message.answer("❗ ابتدا باید چارت ناتال خود را ثبت کنید.")
        return

    start = date.today()
    end = start + timedelta(days=30)

    full = analyze_transits_for_range(natal_chart, start, end)
    job = [l for l in full.split("\n") if "شغل" in l or "MC" in l]

    await callback.message.answer(
        "💼 ترانزیت‌های شغلی:\n\n" + "\n".join(job)
        if job else "💼 ترانزیت شغلی یافت نشد."
    )


# -----------------------------
# ترانزیت‌های چالشی از منو (callback)
# -----------------------------
@router.callback_query(F.data == "transits_challenge")
async def cb_transits_challenge(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    natal_chart = load_user_chart(user_id)

    if not natal_chart:
        await callback.message.answer("❗ ابتدا باید چارت ناتال خود را ثبت کنید.")
        return

    start = date.today()
    end = start + timedelta(days=30)

    full = analyze_transits_for_range(natal_chart, start, end)
    challenge = [l for l in full.split("\n") if "چالش" in l]

    await callback.message.answer(
        "⚠️ ترانزیت‌های چالشی:\n\n" + "\n".join(challenge)
        if challenge else "⚠️ ترانزیت چالشی یافت نشد."
    )
