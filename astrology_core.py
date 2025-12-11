# ----------------------------------------------------------------------
# astrology_core.py - ماژول اصلی محاسبات آسترولوژی (نسخه نهایی و قوی‌ترین اصلاح)
# ----------------------------------------------------------------------

import datetime
from skyfield.api import load, Topos
from skyfield.timelib import Time
from typing import Dict, Any, Tuple
from persiantools.jdatetime import JalaliDateTime
import pytz 
import logging 

# --- [ثابت‌ها و بارگذاری داده‌های نجومی] ---

PLANETS = ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune', 'pluto']

PLANET_MAPPING = {
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

# 💥 FIX: تعریف اولیه EPHEMERIS در سطح ماژول برای جلوگیری از NameError
EPHEMERIS = {} 
ts = None # تعریف سراسری برای timescale
eph = None # تعریف سراسری برای ephemeris

try:
    ts = load.timescale()
    eph = load('de421.bsp')
    
    EPHEMERIS.clear() 
    
    for p_key, p_target in PLANET_MAPPING.items():
        EPHEMERIS[p_key] = eph[p_target]
        
    EPHEMERIS['earth'] = eph['earth'] 
    
    print("✅ داده‌های نجومی با موفقیت بارگذاری شدند.")
    
except Exception as e:
    print(f"❌ خطای حیاتی در بارگذاری داده‌های نجومی (Ephemeris): {e}")
    EPHEMERIS = {} 

# ----------------------------------------------------------------------
# تابع اصلی: محاسبه چارت تولد
# ----------------------------------------------------------------------

def calculate_natal_chart(birth_date_jalali: str, birth_time_str: str, city_name: str, latitude: float, longitude: float, timezone_str: str) -> Dict[str, Any]:
    
    # 1. بررسی وضعیت بارگذاری Ephemeris
    # همچنین مطمئن می‌شویم که eph و ts تعریف شده باشند.
    if not EPHEMERIS or eph is None or ts is None: 
        return {"error": "داده‌های نجومی بارگذاری نشده‌اند. (خطای Ephemeris)"}
        
    # 2. تنظیم تاریخ و مکان
    try:
        j_dt_str = f"{birth_date_jalali} {birth_time_str}"
        j_date = JalaliDateTime.strptime(j_dt_str, "%Y/%m/%d %H:%M") 
        
        dt_local = j_date.to_gregorian().replace(tzinfo=pytz.timezone(timezone_str))
        dt_utc = dt_local.astimezone(pytz.utc)
        
        logging.info(f"DEBUG: Converted UTC Time: {dt_utc}, Timezone: {timezone_str}")
        
        t = ts.utc(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour, dt_utc.minute, dt_utc.second)
        
        location = Topos(latitude_degrees=latitude, longitude_degrees=longitude)
        observer = EPHEMERIS['earth'] + location
        
    except Exception as e:
        return {"error": f"خطا در تبدیل تاریخ و زمان: {e}"}

    
    chart_data = {}

    # 3. محاسبه موقعیت سیارات
    for planet_name in PLANETS:
        try:
            planet_ephem = EPHEMERIS[planet_name] 
            position = observer.at(t).observe(planet_ephem)
            
            # 💥 FIX CRITICAL V3: استفاده از روش frame_of برای بیشترین سازگاری با نسخه‌های مختلف Skyfield
            # این روش مستقیماً طول دایرةالبروجی را محاسبه می‌کند و از خطاهای مکرر 'frame' و 'geometry_of' جلوگیری می‌کند.
            
            # استفاده از frame_of برای تبدیل به مختصات دایرةالبروجی (Ecliptic Coordinates)
            lon_rad, _, _ = position.frame_of(eph['earth'].target).ecliptic_lonlat(epoch=t)

            lon_deg = lon_rad.degrees
            
            chart_data[planet_name] = {
                "degree": lon_deg,
                "lon_dms": f"{lon_deg:.2f}°...", 
                "status": "Calculated successfully" 
            }
            
        except Exception as e:
            chart_data[planet_name] = {"error": f"❌ خطا در محاسبه: {str(e)}"}
            
    logging.info(f"DEBUG FINAL CHART RESULT: {chart_data}")
    return chart_data
