# ----------------------------------------------------------------------
# astrology_core.py - ماژول اصلی محاسبات آسترولوژی (نسخه تصحیح شده)
# ----------------------------------------------------------------------

import datetime
from skyfield.api import load, Topos
from skyfield.timelib import Time
from typing import Dict, Any, Tuple
from persiantools.jdatetime import JalaliDateTime
import pytz 

# --- [ثابت‌ها و بارگذاری داده‌های نجومی] ---

PLANETS = ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune', 'pluto']

# 💡 FIX: تعریف نگاشت برای استفاده از 'Barycenter' در سیارات بیرونی (راه حل خطای Ephemeris)
PLANET_MAPPING = {
    'sun': 'sun',
    'moon': 'moon',
    'mercury': 'mercury',
    'venus': 'venus',
    'mars': 'mars',
    # 💥 اصلاحیه حیاتی: استفاده از مرکز ثقل برای سیارات بیرونی در de421.bsp
    'jupiter': 'jupiter barycenter', 
    'saturn': 'saturn barycenter',
    'uranus': 'uranus barycenter',
    'neptune': 'neptune barycenter',
    'pluto': 'pluto barycenter',
}


try:
    ts = load.timescale()
    eph = load('de421.bsp')
    
    EPHEMERIS = {}
    
    # 💥 اصلاحیه: حلقه برای استفاده از نگاشت جدید
    for p_key, p_target in PLANET_MAPPING.items():
        # p_key: نام سیاره برای استفاده در کد (مثل 'jupiter')
        # p_target: نام هدف در فایل Ephemeris (مثل 'jupiter barycenter')
        EPHEMERIS[p_key] = eph[p_target]
        
    EPHEMERIS['earth'] = eph['earth'] 
    
    print("✅ داده‌های نجومی با موفقیت بارگذاری شدند.")
    
except Exception as e:
    # در صورت شکست، این خطا به کاربر برگردانده می‌شود.
    print(f"❌ خطای حیاتی در بارگذاری داده‌های نجومی (Ephemeris): {e}")
    EPHEMERIS = {} 

# ----------------------------------------------------------------------
# تابع اصلی: محاسبه چارت تولد (بدون تغییر)
# ----------------------------------------------------------------------

def calculate_natal_chart(birth_date_jalali: str, birth_time_str: str, city_name: str, latitude: float, longitude: float, timezone_str: str) -> Dict[str, Any]:
    
    # 1. بررسی وضعیت بارگذاری Ephemeris
    if not EPHEMERIS:
        return {"error": "داده‌های نجومی بارگذاری نشده‌اند. (خطای Ephemeris)"}
        
    # ... بقیه کد (بدون تغییر)
    # ... (کد شما در این بخش بدون تغییر است، زیرا از کلیدهای تصحیح شده استفاده می‌کند)
    
    for planet_name in PLANETS:
        try:
            planet_ephem = EPHEMERIS[planet_name] # این خط اکنون به هدف درست هدایت می‌شود!
            position = observer.at(t).observe(planet_ephem)
            
            # 💥 FIX Defensive Coding: رفع خطای geometry_of با سازگاری به عقب (Skyfield Version Conflict)
            try:
                # روش جدید
                lon_rad, _, _ = position.geometry_of(t).ecliptic_lonlat(epoch=t)
            except AttributeError:
                # روش قدیمی
                pos_apparent = position.apparent()
                lon_rad, _, _ = pos_apparent.frame.ecliptic_lonlat(epoch=t) 

            lon_deg = lon_rad.degrees
            
            chart_data[planet_name] = {
                "degree": lon_deg,
                "lon_dms": f"{lon_deg:.2f}°...", 
                "status": "Calculated successfully" 
            }
            
        except Exception as e:
            chart_data[planet_name] = {"error": f"❌ خطا در محاسبه: {str(e)}"}
            
    return chart_data
