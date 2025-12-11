# ----------------------------------------------------------------------
# astrology_core.py - ماژول اصلی محاسبات آسترولوژی با استفاده از PYSWISSEPH (نسخه نهایی و اصلاح شده)
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

try:
    se.set_ephe_path('') 
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
        
        # 💥 FIX CRITICAL: اصلاح نام تابع از date_to_jd به swe_julday
        # تبدیل زمان UTC به Julian Day (فرمت مورد نیاز swisseph)
        total_hours_utc = dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0
        
        # se.swe_julday(سال, ماه, روز, ساعت (ساعت + اعشار دقیقه/ثانیه), تقویم)
        jd_utc = se.swe_julday(dt_utc.year, dt_utc.month, dt_utc.day, total_hours_utc, se.SE_GREG_CAL)
        
    except Exception as e:
        return {"error": f"خطا در تبدیل تاریخ و زمان: {e}"}

    
    chart_data = {}

    # 2. محاسبه موقعیت سیارات
    for planet_name, planet_code in PLANETS_MAP.items():
        try:
            # محاسبه موقعیت سیاره:
            # FLG_SWIEPH: استفاده از ephemeris پیش‌فرض
            # FLG_TOPOCTR: محاسبات توابع مرکزی (اختیاری، اما توصیه می‌شود)
            # پرچم‌های دیگر به صورت پیش‌فرض Tropical و True Node/Mean Node هستند.
            
            res = se.calc_ut(jd_utc, planet_code, se.FLG_SWIEPH | se.FLG_TOPOCTR)
            
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
            chart_data[planet_name] = {"error": f"❌ خطا در محاسبه: {str(e)}"}
            
    return chart_data
