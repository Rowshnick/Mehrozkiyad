# ----------------------------------------------------------------------
# utils.py - ابزارهای کمکی عمومی برای ربات آسترولوژی
# ----------------------------------------------------------------------

import asyncio
from typing import Dict, Any, Optional
from geopy.geocoders import Nominatim
from persiantools.jdatetime import JalaliDateTime
import pytz
import logging

# ----------------------------------------------------------------------
# تنظیمات لاگ
# ----------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("astro_bot_utils")

# ----------------------------------------------------------------------
# ابزار مکان‌یابی شهرها
# ----------------------------------------------------------------------

geolocator = Nominatim(user_agent="astro_bot")

async def get_coordinates_from_city(city_name: str, language: str = "fa") -> Dict[str, Any]:
    """
    گرفتن مختصات جغرافیایی (lat, lng) از نام شهر.
    ورودی:
        city_name: نام شهر (مثال: "Tehran, IR")
        language: زبان نتایج (پیش‌فرض: فارسی)
    خروجی:
        دیکشنری شامل lat و lng یا پیام خطا
    """
    loop = asyncio.get_event_loop()
    try:
        location = await loop.run_in_executor(
            None,
            lambda: geolocator.geocode(city_name, language=language)
        )

        if location:
            return {
                "lat": location.latitude,
                "lng": location.longitude,
                "display_name": location.address
            }
        else:
            return {"error": "❌ شهر مورد نظر پیدا نشد."}

    except Exception as e:
        logger.error(f"خطا در گرفتن مختصات: {e}")
        return {"error": f"خطا در گرفتن مختصات: {e}"}

# ----------------------------------------------------------------------
# ابزارهای زمان و تاریخ
# ----------------------------------------------------------------------

def jalali_to_utc(jalali_date_str: str, time_str: str, timezone_str: str) -> Optional[str]:
    """
    تبدیل تاریخ جلالی + زمان محلی به زمان UTC.
    ورودی:
        jalali_date_str: "YYYY/MM/DD"
        time_str: "HH:MM"
        timezone_str: مثل "Asia/Tehran"
    خروجی:
        رشته datetime به فرمت ISO یا None در صورت خطا
    """
    try:
        j_dt = JalaliDateTime.strptime(f"{jalali_date_str} {time_str}", "%Y/%m/%d %H:%M")
        g_dt_naive = j_dt.to_gregorian()
        tz = pytz.timezone(timezone_str)
        g_dt_local = tz.localize(g_dt_naive, is_dst=None)
        g_dt_utc = g_dt_local.astimezone(pytz.utc)
        return g_dt_utc.isoformat()
    except Exception as e:
        logger.error(f"خطا در تبدیل زمان: {e}")
        return None

# ----------------------------------------------------------------------
# ابزارهای عمومی
# ----------------------------------------------------------------------

def safe_dict_get(d: Dict[str, Any], key: str, default: Any = None) -> Any:
    """
    گرفتن مقدار از دیکشنری به شکل امن.
    """
    return d[key] if key in d else default

def format_error(message: str) -> Dict[str, str]:
    """
    ساخت خروجی استاندارد خطا.
    """
    return {"error": f"❌ {message}"}

# ----------------------------------------------------------------------
# تست محلی
# ----------------------------------------------------------------------

if __name__ == "__main__":
    async def test_geo():
        result = await get_coordinates_from_city("Tehran, IR")
        print("نتیجه مکان‌یابی:", result)

    print("تست تبدیل تاریخ:", jalali_to_utc("1365/05/23", "14:30", "Asia/Tehran"))
    asyncio.run(test_geo())
