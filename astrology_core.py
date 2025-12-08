# ----------------------------------------------------------------------
# astrology_core.py - ماژول اصلی محاسبات آسترولوژی (نسخه نهایی و پایدار)
# ----------------------------------------------------------------------

import datetime
from skyfield.api import load, Topos
from skyfield.timelib import Time
from typing import Dict, Any, Tuple
from persiantools.jdatetime import JalaliDateTime
import pytz 
# 💥 FIX: حذف ایمپورت‌های subprocess و sys
# import subprocess
# import sys 

# --- [ثابت‌ها و بارگذاری داده‌های نجومی] ---

# 💥 FIX: حذف کامل کد نصب مجدد در زمان اجرا (Runtime Force Install)

PLANETS = ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune', 'pluto']

try:
    # 💡 FIX Ephemeris: استفاده مجدد از فایل استاندارد de421.bsp (پایدارترین گزینه)
    ts = load.timescale()
    eph = load('de421.bsp')
    
    EPHEMERIS = {}
    for p in PLANETS:
        # Skyfield از این شیوه برای دسترسی به سیارات استفاده می‌کند
        EPHEMERIS[p] = eph[p]
        
    EPHEMERIS['earth'] = eph['earth'] 
    
    print("✅ داده‌های نجومی با موفقیت بارگذاری شدند. (تکیه بر نصب Dockerfile)")
    
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
        
        dt_local = j_date.to_gregorian().replace(tzinfo=pytz.timezone(timezone_str))
        dt_utc = dt_local.astimezone(pytz.utc)
        
        t = ts.utc(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour, dt_utc.minute, dt_utc.second)
    except Exception as e:
        return {"error": f"خطا در تبدیل تاریخ و زمان: {e}"}

    # تنظیم محل مشاهده گر (Topos)
    location = Topos(latitude_degrees=latitude, longitude_degrees=longitude)
    observer = EPHEMERIS['earth'] + location
    
    chart_data = {}

    # 3. محاسبه موقعیت سیارات
    for planet_name in PLANETS:
        try:
            planet_ephem = EPHEMERIS[planet_name] 
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
