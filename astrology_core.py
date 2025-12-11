# ----------------------------------------------------------------------
# astrology_core.py - ماژول اصلی محاسبات آسترولوژی با استفاده از PYSWISSEPH
# ----------------------------------------------------------------------

import swisseph as se
import pytz
import datetime
from persiantools.jdatetime import JalaliDateTime
from typing import Dict, Any

# --- [ثابت‌ها و تعاریف] ---

# نگاشت نام سیارات به کدهای داخلی swisseph
PLANETS_MAP = {
    'sun': se.SUN, 'moon': se.MOON, 
    'mercury': se.MERCURY, 'venus': se.VENUS, 'mars': se.MARS, 
    'jupiter': se.JUPITER, 'saturn': se.SATURN, 
    'uranus': se.URANUS, 'neptune': se.NEPTUNE, 'pluto': se.PLUTO,
}

# --- [تنظیمات اولیه] ---

# swisseph از فرمت فایل‌های استاندارد نجومی استفاده می‌کند.
# اگر این پوشه وجود ندارد، swisseph به صورت خودکار از مکان‌های پیش‌فرض جستجو می‌کند.
try:
    # تعیین مسیر فایل‌های ephemeris (اختیاری، اما خوب است)
    se.set_ephe_path('') # جستجو در مسیرهای پیش فرض
    print("✅ سوپرامریس (Swiss Ephemeris) با موفقیت تنظیم شد.")
except Exception as e:
    print(f"❌ خطای تنظیم Swiss Ephemeris: {e}")
    

# ----------------------------------------------------------------------
# تابع اصلی: محاسبه چارت تولد
# ----------------------------------------------------------------------

def calculate_natal_chart(birth_date_jalali: str, birth_time_str: str, city_name: str, latitude: float, longitude: float, timezone_str: str) -> Dict[str, Any]:
    
    # 1. تبدیل تاریخ و زمان
    try:
        j_dt_str = f"{birth_date_jalali} {birth_time_str}"
        j_date = JalaliDateTime.strptime(j_dt_str, "%Y/%m/%d %H:%M") 
        
        # تبدیل به زمان محلی و سپس UTC
        dt_local = j_date.to_gregorian().replace(tzinfo=pytz.timezone(timezone_str))
        dt_utc = dt_local.astimezone(pytz.utc)
        
        # تبدیل زمان UTC به Julian Day (فرمت مورد نیاز swisseph)
        # swisseph از زمان UTC برای محاسبه استفاده می‌کند.
        jd_utc = se.date_to_jd(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0)[1]
        
    except Exception as e:
        return {"error": f"خطا در تبدیل تاریخ و زمان: {e}"}

    
    chart_data = {}

    # 2. محاسبه موقعیت سیارات
    for planet_name, planet_code in PLANETS_MAP.items():
        try:
            # محاسبه موقعیت سیاره:
            # jd_utc: زمان
            # planet_code: کد سیاره
            # se.FLG_ECLIP_TRUE: پرچم برای موقعیت حقیقی دایرةالبروجی (Ecliptic True Position)
            
            # 💡 توجه: swisseph به طور پیش‌فرض موقعیت‌های Astrometric را برای محاسبات آسترولوژی استفاده می‌کند.
            # برای حالت رجعت (R/D)، پارامتر 'res' را بررسی می‌کنیم.
            res = se.calc_ut(jd_utc, planet_code, se.FLG_SWIEPH | se.FLG_TOPOCTR | se.FLG_SIDEREAL)
            
            # res[0] = [longitude, latitude, distance, speed_long, speed_lat, speed_dist]
            lon_deg = res[0][0]
            speed_long = res[0][3]
            
            # تعیین وضعیت (مستقیم یا رجعت)
            status = "Direct"
            if speed_long < 0:
                status = "Retrograde"
            
            chart_data[planet_name] = {
                "degree": lon_deg,
                "lon_dms": f"{lon_deg:.2f}°...", 
                "status": status
            }
            
        except Exception as e:
            # اگر خطای محاسباتی جزئی رخ داد، آن را در همان آیتم ذخیره می‌کنیم
            chart_data[planet_name] = {"error": f"❌ خطا در محاسبه: {str(e)}"}
            
    return chart_data
