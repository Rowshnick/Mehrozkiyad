# ----------------------------------------------------------------------
# astrology_core.py - ماژول اصلی محاسبات آسترولوژی (نسخه نهایی و پایدار)
# ----------------------------------------------------------------------

import datetime
from skyfield.api import load, Topos
from skyfield.timelib import Time
from typing import Dict, Any, Tuple
from persiantools.jdatetime import JalaliDateTime
import pytz 
import logging # برای گزارش‌گیری

# --- [ثابت‌ها و بارگذاری داده‌های نجومی] ---

PLANETS = ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune', 'pluto']

# 💡 تعریف نگاشت برای استفاده از 'Barycenter' در سیارات بیرونی
PLANET_MAPPING = {
    'sun': 'sun',
    'moon': 'moon',
    'mercury': 'mercury',
    'venus': 'venus',
    'mars': 'mars',
    # 💥 استفاده از مرکز ثقل برای سیارات بیرونی در de421.bsp
    'jupiter': 'jupiter barycenter', 
    'saturn': 'saturn barycenter',
    'uranus': 'uranus barycenter',
    'neptune': 'neptune barycenter',
    'pluto': 'pluto barycenter',
}

# 💥 FIX CRITICAL: تعریف اولیه EPHEMERIS در سطح ماژول برای جلوگیری از NameError
EPHEMERIS = {} 

try:
    ts = load.timescale()
    eph = load('de421.bsp')
    
    EPHEMERIS.clear() # اطمینان از پاک بودن
    
    # 💥 حلقه برای استفاده از نگاشت جدید
    for p_key, p_target in PLANET_MAPPING.items():
        EPHEMERIS[p_key] = eph[p_target]
        
    EPHEMERIS['earth'] = eph['earth'] 
    
    print("✅ داده‌های نجومی با موفقیت بارگذاری شدند.")
    
except Exception as e:
    # در صورت شکست، این خطا به کاربر برگردانده می‌شود.
    print(f"❌ خطای حیاتی در بارگذاری داده‌های نجومی (Ephemeris): {e}")
    EPHEMERIS = {} 

# ----------------------------------------------------------------------
# تابع اصلی: محاسبه چارت تولد
# ----------------------------------------------------------------------

def calculate_natal_chart(birth_date_jalali: str, birth_time_str: str, city_name: str, latitude: float, longitude: float, timezone_str: str) -> Dict[str, Any]:
    
    # 1. بررسی وضعیت بارگذاری Ephemeris
    if not EPHEMERIS: 
        return {"error": "داده‌های نجومی بارگذاری نشده‌اند. (خطای Ephemeris)"}
        
    # 2. تنظیم تاریخ و مکان
    try:
        j_dt_str = f"{birth_date_jalali} {birth_time_str}"
        j_date = JalaliDateTime.strptime(j_dt_str, "%Y/%m/%d %H:%M") 
        
        # تبدیل به زمان محلی و سپس UTC
        dt_local = j_date.to_gregorian().replace(tzinfo=pytz.timezone(timezone_str))
        dt_utc = dt_local.astimezone(pytz.utc)
        
        logging.info(f"DEBUG: Converted UTC Time: {dt_utc}, Timezone: {timezone_str}")
        
        t = ts.utc(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour, dt_utc.minute, dt_utc.second)
        
        # تنظیم محل مشاهده گر (Topos)
        location = Topos(latitude_degrees=latitude, longitude_degrees=longitude)
        observer = EPHEMERIS['earth'] + location
        
    # در صورت خطای تبدیل تاریخ/زمان، دیکشنری خطا را برمی‌گرداند
    except Exception as e:
        logging.error(f"DEBUG ERROR: Date/Time conversion failed: {e}") 
        return {"error": f"خطا در تبدیل تاریخ و زمان: {e}"}

    
    chart_data = {}

    # 3. محاسبه موقعیت سیارات
    for planet_name in PLANETS:
        try:
            planet_ephem = EPHEMERIS[planet_name] 
            position = observer.at(t).observe(planet_ephem)
            
            # 💥 FIX CRITICAL: استفاده از روش geometry_of برای رفع خطای 'Apparent' object has no attribute 'frame'
            lon_rad, _, _ = position.geometry_of(t).ecliptic_lonlat(epoch=t) 

            lon_deg = lon_rad.degrees
            
            chart_data[planet_name] = {
                "degree": lon_deg,
                "lon_dms": f"{lon_deg:.2f}°...", 
                "status": "Calculated successfully" 
            }
            
        except Exception as e:
            # اگر خطای محاسباتی جزئی رخ داد، آن را در همان آیتم ذخیره می‌کنیم
            chart_data[planet_name] = {"error": f"❌ خطا در محاسبه: {str(e)}"}
            
    logging.info(f"DEBUG FINAL CHART RESULT: {chart_data}")
    return chart_data
