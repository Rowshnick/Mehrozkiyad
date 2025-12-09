# ----------------------------------------------------------------------
# astrology_core.py - ماژول اصلی محاسبات آسترولوژی با Skyfield (نسخه پایدار)
# ----------------------------------------------------------------------

import os
import math
from typing import Dict, Any, Optional

from persiantools.jdatetime import JalaliDateTime
import pytz
from skyfield.api import load, wgs84
from skyfield.api import Loader
from skyfield.units import Angle

# ----------------------------------------------------------------------
# تنظیمات و ثابت‌ها
# ----------------------------------------------------------------------

PLANETS = [
    'sun', 'moon', 'mercury', 'venus', 'mars',
    'jupiter', 'saturn', 'uranus', 'neptune', 'pluto'
]

# نگاشت به اهداف ephemeris (برای بیرونی‌ها از barycenter استفاده شود)
PLANET_TARGETS = {
    'sun': 'sun',
    'moon': 'moon',
    'mercury': 'mercury',
    'venus': 'venus',
    'mars': 'mars',
    'jupiter': 'jupiter barycenter',
    'saturn': 'saturn barycenter',
    'uranus': 'uranus barycenter',
    'neptune': 'neptune barycenter',
    'pluto': 'pluto barycenter',
}

ZODIAC_SIGNS_EN = [
    "Aries","Taurus","Gemini","Cancer","Leo","Virgo",
    "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"
]

# مسیر پیش‌فرض برای فایل‌های ephemeris
DEFAULT_EPHEMERIS_FILE = os.getenv("EPHEMERIS_FILE", "de421.bsp")
EPHEMERIS_DIR = os.getenv("EPHEMERIS_DIR", "data/ephemeris")

# اطمینان از وجود دایرکتوری داده‌ها
os.makedirs(EPHEMERIS_DIR, exist_ok=True)

# Loader سفارشی برای کنترل مسیر کش
loader = Loader(EPHEMERIS_DIR)
ts = load.timescale()

# ----------------------------------------------------------------------
# بارگذاری اپهمریس
# ----------------------------------------------------------------------

def load_ephemeris() -> Optional[dict]:
    """
    تلاش برای بارگذاری فایل ephemeris با امکان fallback.
    """
    try:
        # ابتدا تلاش با نام سفارشی یا پیش‌فرض
        eph_path = os.path.join(EPHEMERIS_DIR, DEFAULT_EPHEMERIS_FILE)
        eph = loader(DEFAULT_EPHEMERIS_FILE) if os.path.exists(eph_path) else load(DEFAULT_EPHEMERIS_FILE)
    except Exception:
        # fallback به de440s اگر موجود بود، یا دانلود شود
        try:
            eph = loader("de440s.bsp")
        except Exception:
            # آخرین تلاش: de421 از اینترنت
            try:
                eph = load("de421.bsp")
            except Exception:
                return None

    # ساخت نقشه اهداف
    ephem_map = {'earth': eph['earth']}
    for key, target in PLANET_TARGETS.items():
        try:
            ephem_map[key] = eph[target]
        except Exception:
            ephem_map[key] = None  # اگر هدفی موجود نبود، بعداً هندل می‌کنیم
    return ephem_map

EPHEMERIS = load_ephemeris()

# ----------------------------------------------------------------------
# ابزارهای زمان و مکان
# ----------------------------------------------------------------------

def to_utc_from_jalali(jalali_date_str: str, time_str: str, timezone_str: str):
    """
    تبدیل تاریخ جلالی + زمان محلی به datetime UTC امن.
    jalali_date_str نمونه: "1403/09/18"
    time_str نمونه: "14:30"
    timezone_str نمونه: "Asia/Tehran"
    """
    try:
        # ساخت datetime جلالی
        j_dt = JalaliDateTime.strptime(f"{jalali_date_str} {time_str}", "%Y/%m/%d %H:%M")
        g_dt_naive = j_dt.to_gregorian()  # naive datetime (بدون tz)
        tz = pytz.timezone(timezone_str)
        g_dt_local = tz.localize(g_dt_naive, is_dst=None)
        g_dt_utc = g_dt_local.astimezone(pytz.utc)
        return g_dt_utc
    except Exception as e:
        raise ValueError(f"خطا در تبدیل زمان/تایم‌زون: {e}")

def sign_name_from_longitude(lon_deg: float) -> str:
    """
    تبدیل طول ecliptic (درجه) به نام برج.
    """
    idx = int(math.floor(lon_deg % 360.0) // 30)
    return ZODIAC_SIGNS_EN[idx]

# ----------------------------------------------------------------------
# محاسبه موقعیت سیارات
# ----------------------------------------------------------------------

def compute_planet_positions(dt_utc, latitude: float, longitude: float) -> Dict[str, Any]:
    """
    محاسبه موقعیت سیارات (درجه ecliptic و نام برج) برای زمان و مکان مشخص.
    """
    if EPHEMERIS is None:
        return {"error": "Ephemeris بارگذاری نشد."}

    try:
        # زمان Skyfield
        t = ts.utc(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour, dt_utc.minute, dt_utc.second)
        # مکان ناظر روی زمین (WGS84)
        location = wgs84.latlon(latitude, longitude)
        observer = EPHEMERIS['earth'] + location
    except Exception as e:
        return {"error": f"خطا در آماده‌سازی زمان/مکان: {e}"}

    results: Dict[str, Any] = {}

    for planet in PLANETS:
        try:
            target = EPHEMERIS.get(planet)
            if target is None:
                results[planet] = {"error": "هدف ephemeris یافت نشد."}
                continue

            # مشاهده و تبدیل به apparent سپس مختصات ecliptic
            position = observer.at(t).observe(target).apparent()
            lon, lat, distance = position.ecliptic_latlon()
            lon_deg = float(lon.degrees)

            results[planet] = {
                "longitude_deg": lon_deg,
                "sign": sign_name_from_longitude(lon_deg),
            }
        except Exception as e:
            results[planet] = {"error": f"خطا در محاسبه سیاره: {e}"}

    return results

# ----------------------------------------------------------------------
# Ascendant و Houses (اسکلت اولیه)
# ----------------------------------------------------------------------

def compute_ascendant(dt_utc, latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
    """
    TODO: محاسبه دقیق Ascendant نیاز به:
      - زمان نجومی محلی (LST)
      - زاویه مایل دایره‌البروج (obliquity)
      - تبدیل به افق محلی و محاسبه نقطه طلوع دایره‌البروج.
    در این نسخه اسکلت آماده است تا در گام بعدی تکمیل شود.
    """
    try:
        # اسکلت پایه برای توسعه بعدی
        # می‌توان از skyfield برای محاسبه زاویه‌ها و از فرمول‌های نجومی کلاسیک استفاده کرد.
        return None
    except Exception:
        return None

# ----------------------------------------------------------------------
# تابع اصلی محاسبه چارت تولد
# ----------------------------------------------------------------------

def calculate_natal_chart(
    birth_date_jalali: str,
    birth_time_str: str,
    city_name: str,
    latitude: float,
    longitude: float,
    timezone_str: str
) -> Dict[str, Any]:
    """
    محاسبه چارت تولد: موقعیت سیارات + (در آینده) Ascendant و Houses.
    ورودی‌ها:
      - birth_date_jalali: "YYYY/MM/DD" جلالی
      - birth_time_str: "HH:MM"
      - city_name: برای ثبت در خروجی
      - latitude, longitude: مختصات محل تولد
      - timezone_str: مثل "Asia/Tehran"
    خروجی:
      - ساختار داده شامل اطلاعات ورودی، زمان تبدیل‌شده، موقعیت سیارات و وضعیت.
    """
    # بررسی اپهمریس
    if EPHEMERIS is None:
        return {"error": "داده‌های Ephemeris در دسترس نیست. لطفاً فایل‌های ephemeris را بررسی کنید."}

    # تبدیل زمان
    try:
        dt_utc = to_utc_from_jalali(birth_date_jalali, birth_time_str, timezone_str)
    except Exception as e:
        return {"error": str(e)}

    # محاسبات سیارات
    planets = compute_planet_positions(dt_utc, latitude, longitude)
    if "error" in planets:
        return planets

    # محاسبه Ascendant (فعلاً None)
    ascendant = compute_ascendant(dt_utc, latitude, longitude)

    # خروجی ساختاریافته
    return {
        "input": {
            "birth_date_jalali": birth_date_jalali,
            "birth_time": birth_time_str,
            "city": city_name,
            "latitude": latitude,
            "longitude": longitude,
            "timezone": timezone_str,
        },
        "datetime_utc": dt_utc.isoformat(),
        "planets": planets,
        "ascendant": ascendant,
        "status": "ok"
    }

# ----------------------------------------------------------------------
# استفاده نمونه (برای تست محلی)
# ----------------------------------------------------------------------

if __name__ == "__main__":
    # نمونه تست
    sample = calculate_natal_chart(
        birth_date_jalali="1365/05/23",
        birth_time_str="14:30",
        city_name="Tehran, IR",
        latitude=35.6892,
        longitude=51.3890,
        timezone_str="Asia/Tehran"
    )
    print(sample)



# ----------------------------------------------------------------------
# تابع جدید: پیشگویی روزانه
# ----------------------------------------------------------------------

def calculate_daily_prediction(
    birth_date_jalali: str,
    birth_time_str: str,
    city_name: str,
    latitude: float,
    longitude: float,
    timezone_str: str,
    target_date: Optional[datetime.date] = None
) -> Dict[str, Any]:
    """
    محاسبه پیشگویی روزانه بر اساس:
      - وضعیت آسمان امروز (ترنزیت سیارات)
      - مقایسه با چارت تولد کاربر
    ورودی:
      - تاریخ و ساعت تولد کاربر
      - مختصات محل تولد
      - تایم‌زون
      - target_date: تاریخ مورد نظر (پیش‌فرض: امروز)
    خروجی:
      - متن پیشگویی روزانه
    """
    if EPHEMERIS is None:
        return {"error": "Ephemeris بارگذاری نشد."}

    # تاریخ هدف (امروز اگر مشخص نشده)
    if target_date is None:
        target_date = datetime.date.today()

    # زمان تولد کاربر (UTC)
    try:
        dt_birth_utc = to_utc_from_jalali(birth_date_jalali, birth_time_str, timezone_str)
    except Exception as e:
        return {"error": f"خطا در تبدیل زمان تولد: {e}"}

    # محاسبه چارت تولد
    natal_chart = calculate_natal_chart(
        birth_date_jalali, birth_time_str, city_name, latitude, longitude, timezone_str
    )
    if "error" in natal_chart:
        return natal_chart

    # محاسبه وضعیت امروز
    t_today = ts.utc(target_date.year, target_date.month, target_date.day)
    location = wgs84.latlon(latitude, longitude)
    observer = EPHEMERIS['earth'] + location

    today_positions = {}
    for planet in PLANETS:
        try:
            target = EPHEMERIS.get(planet)
            if target is None:
                continue
            pos = observer.at(t_today).observe(target).apparent()
            lon, lat, dist = pos.ecliptic_latlon()
            today_positions[planet] = lon.degrees
        except Exception:
            today_positions[planet] = None

    # مقایسه ساده جنبه‌ها (conjunction, trine, square, opposition)
    predictions = []
    natal_planets = natal_chart.get("planets", {})
    for planet, natal_data in natal_planets.items():
        natal_lon = natal_data.get("longitude_deg")
        today_lon = today_positions.get(planet)
        if natal_lon and today_lon:
            diff = abs(today_lon - natal_lon) % 360
            if diff < 8:  # conjunction
                predictions.append(f"{planet.capitalize()} امروز با موقعیت تولد شما هم‌نشین است → انرژی مشابه و پررنگ.")
            elif abs(diff - 120) < 8:  # trine
                predictions.append(f"{planet.capitalize()} امروز با موقعیت تولد شما در تریگون است → هماهنگی و فرصت‌های مثبت.")
            elif abs(diff - 90) < 8:  # square
                predictions.append(f"{planet.capitalize()} امروز با موقعیت تولد شما در مربع است → چالش و فشار احتمالی.")
            elif abs(diff - 180) < 8:  # opposition
                predictions.append(f"{planet.capitalize()} امروز با موقعیت تولد شما در مقابله است → نیاز به تعادل و مراقبت.")

    return {
        "date": target_date.isoformat(),
        "predictions": predictions,
        "status": "ok"
    }
