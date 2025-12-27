# ----------------------------------------------------------------------
# handlers/astro_handlers.py
# نسخه نهایی، پایدار و سازگار با Ascendant + Houses واقعی
# ----------------------------------------------------------------------

import os
import io
import logging
from typing import Dict, Any, Optional

import astrology_core
import utils
import keyboards
from chart_drawer_fa import draw_chart_wheel_fa

# ----------------------------------------------------------------------
# تنظیمات اولیه
# ----------------------------------------------------------------------

BOT_TOKEN = os.environ.get("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable is not set")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ----------------------------------------------------------------------
# هندلر اصلی محاسبه چارت تولد
# ----------------------------------------------------------------------

async def handle_chart_calculation(
    chat_id: int,
    state: Dict[str, Any],
    save_user_state_func
):
    """
    اجرای کامل فرآیند محاسبه چارت تولد:
    - اعتبارسنجی داده‌ها
    - محاسبه نجومی (Asc + Houses + Planets)
    - تولید متن گزارش
    - تولید تصویر چارت (در صورت امکان)
    - ارسال خروجی و بازگشت به منوی اصلی
    """

    # ----------------------------
    # ایمن‌سازی وضعیت
    # ----------------------------

    state.setdefault("data", {})
    data: Dict[str, Any] = state["data"]

    birth_date: Optional[str] = data.get("birth_date")
    birth_time: Optional[str] = data.get("birth_time")
    city_name: Optional[str] = data.get("city_name")

    try:
        latitude = float(data.get("latitude", 0.0))
        longitude = float(data.get("longitude", 0.0))
    except (TypeError, ValueError):
        logger.error("Invalid latitude/longitude values")
        latitude, longitude = 0.0, 0.0

    timezone = data.get("timezone", "Asia/Tehran")

    # ----------------------------
    # بررسی کامل بودن اطلاعات
    # ----------------------------

    if not all([birth_date, birth_time, city_name]):
        await utils.send_message(
            BOT_TOKEN,
            chat_id,
            utils.escape_markdown_v2(
                "❌ اطلاعات تولد کامل نیست.\n"
                "لطفاً تاریخ، ساعت و شهر تولد را دوباره وارد کنید."
            ),
            keyboards.main_menu_keyboard()
        )
        return

    logger.info(
        f"Start natal chart calculation | user={chat_id} | "
        f"{birth_date=} {birth_time=} {city_name=}"
    )

    # ----------------------------
    # محاسبه چارت نجومی (Core)
    # ----------------------------

    chart_result = astrology_core.calculate_natal_chart(
        birth_date_jalali=birth_date,
        birth_time=birth_time,
        city_name=city_name,
        lat=latitude,
        lon=longitude,
        tz_name=timezone
    )

    if not chart_result or "error" in chart_result:
        error_text = chart_result.get("error", "خطای نامشخص در محاسبه چارت")
        logger.error(f"Astrology core error: {error_text}")

        await utils.send_message(
            BOT_TOKEN,
            chat_id,
            utils.escape_markdown_v2(f"❌ خطا در محاسبه چارت:\n{error_text}"),
            keyboards.main_menu_keyboard()
        )
        return

    # ----------------------------
    # تولید متن گزارش
    # ----------------------------

    ascendant = chart_result.get("ascendant")
    planets = chart_result.get("planets", {})

    report_text = (
        f"✨ *چارت تولد شما آماده شد* ✨\n\n"
        f"📍 شهر: {city_name}\n"
        f"📅 تاریخ: {birth_date}\n"
        f"⏰ ساعت: {birth_time}\n"
    )

    if ascendant is not None:
        report_text += f"🌅 *Ascendant (طالع)*: `{ascendant:.2f}°`\n"

    report_text += "──────────────────\n"

    for planet_name, pdata in planets.items():
        if "degree" not in pdata:
            report_text += (
                f"🔹 *{planet_name.title()}*: ❌ خطا در محاسبه\n"
            )
            continue

        degree = pdata["degree"]
        sign = pdata.get("sign", "؟")
        house = pdata.get("house", "؟")

        report_text += (
            f"🔹 *{planet_name.title()}*\n"
            f"   ▫️ موقعیت: `{degree:.2f}° {sign}`\n"
            f"   ▫️ خانه: `{house}`\n\n"
        )

    escaped_report = utils.escape_markdown_v2(report_text)

    # ----------------------------
    # تولید تصویر چارت (اختیاری، حساس به حافظه)
    # ----------------------------

    image_buffer: Optional[io.BytesIO] = None

    try:
        logger.info("Attempting to draw chart wheel image")
        image_buffer = draw_chart_wheel_fa(chart_result)

        if image_buffer:
            await utils.send_photo_with_caption(
                BOT_TOKEN,
                chat_id,
                photo=image_buffer,
                caption=utils.escape_markdown_v2(
                    f"📊 نمودار چارت تولد\n{birth_date} — {city_name}"
                )
            )
            logger.info("Chart image sent successfully")

    except Exception as draw_err:
        logger.warning(f"Chart image generation skipped: {draw_err}")

    finally:
        # آزادسازی حافظه (بسیار مهم برای Railway)
        if image_buffer:
            try:
                image_buffer.close()
            except Exception:
                pass

    # ----------------------------
    # ارسال متن نهایی
    # ----------------------------

    await utils.send_message(
        BOT_TOKEN,
        chat_id,
        escaped_report,
        keyboards.main_menu_keyboard()
    )

    # ----------------------------
    # بازگشت به منوی اصلی
    # ----------------------------

    state["step"] = "WELCOME"
    await save_user_state_func(chat_id, state)

    logger.info(f"Natal chart workflow finished | user={chat_id}")
