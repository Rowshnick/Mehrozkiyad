# handlers/astro_handlers.py
# =============================================================================
# مدیریت گردش‌کار آسترولوژی (Astrology Workflow)
# -----------------------------------------------------------------------------
# این فایل هیچ محاسبه‌ای انجام نمی‌دهد.
# فقط:
#   1) ورودی‌ها را از state دریافت می‌کند
#   2) چارت را محاسبه می‌کند
#   3) تفسیر را تولید می‌کند
#   4) تصویر چارت را رسم می‌کند
#   5) خروجی را برای کاربر ارسال می‌کند
#   6) state را به منوی اصلی برمی‌گرداند
# =============================================================================

from aiogram import Router

from core import utils
from core.astrology_core import calculate_natal_chart
from core.interpret_natal_chart import interpret_natal_chart
from core.chart_drawer_fa import draw_chart_advanced_fa

router = Router()


# =============================================================================
# تابع اصلی اجرای آسترولوژی
# =============================================================================

async def run_astrology_workflow(chat_id: int, state: dict, save_state_func):
    """
    اجرای کامل گردش‌کار آسترولوژی:
        - محاسبه چارت
        - تولید تفسیر
        - رسم چارت
        - ارسال خروجی
    """

    data = state.get("data", {})

    # بررسی کامل بودن داده‌ها
    required_fields = ["birth_date", "birth_time", "latitude", "longitude", "timezone"]
    missing = [f for f in required_fields if f not in data]

    if missing:
        await utils.send_message(
            utils.BOT_TOKEN,
            chat_id,
            utils.escape_markdown_v2(
                f"❌ اطلاعات ناقص است. فیلدهای زیر یافت نشد:\n{', '.join(missing)}"
            )
        )
        return

    # پیام انتظار
    await utils.send_message(
        utils.BOT_TOKEN,
        chat_id,
        utils.escape_markdown_v2("🔄 در حال محاسبه چارت تولد شما... لطفاً کمی صبر کنید.")
    )

    # -------------------------------------------------------------------------
    # ۱) محاسبه چارت
    # -------------------------------------------------------------------------
    chart = calculate_natal_chart(
        birth_date_jalali=data["birth_date"],
        birth_time_str=data["birth_time"],
        latitude=data["latitude"],
        longitude=data["longitude"],
        timezone_str=data["timezone"],
        house_system="K"
    )

    if "error" in chart:
        await utils.send_message(
            utils.BOT_TOKEN,
            chat_id,
            utils.escape_markdown_v2(f"❌ خطا در محاسبه چارت:\n{chart['error']}")
        )
        return

    # -------------------------------------------------------------------------
    # ۲) تولید تفسیر
    # -------------------------------------------------------------------------
    interpretation = interpret_natal_chart(chart)

    # -------------------------------------------------------------------------
    # ۳) رسم چارت تصویری
    # -------------------------------------------------------------------------
    chart_image = draw_chart_advanced_fa(chart)

    # -------------------------------------------------------------------------
    # ۴) ارسال تصویر + تفسیر
    # -------------------------------------------------------------------------
    await utils.send_photo_with_caption(
        utils.BOT_TOKEN,
        chat_id,
        chart_image,
        interpretation
    )

    # -------------------------------------------------------------------------
    # ۵) بازگشت به منوی اصلی
    # -------------------------------------------------------------------------
    await utils.send_message(
        utils.BOT_TOKEN,
        chat_id,
        utils.escape_markdown_v2("بازگشت به منوی اصلی:"),
        reply_markup=None
    )

    # ریست state
    new_state = {"step": "WELCOME", "data": {}}
    await save_state_func(chat_id, new_state)
