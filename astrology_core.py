# ----------------------------------------------------------------------
# astrology_core.py - ماژول اصلی محاسبات آسترولوژی
# ----------------------------------------------------------------------

import datetime
from skyfield.api import load, Topos
from skyfield.timelib import Time
from typing import Dict, Any, Tuple
from persiantools.jdatetime import JalaliDateTime
import pytz 
import subprocess
import sys

# 💥 [FIX 1: Runtime Force Install - برای شکستن کش Skyfield]
try:
    result = subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "--force-reinstall", "skyfield"], 
                            capture_output=True, text=True, check=False)
    if result.returncode == 0:
        print("✅ Skyfield successfully re-installed and upgraded at runtime.")
    else:
        print(f"❌ Failed to force-reinstall Skyfield at runtime. Error: {result.stderr}")
except Exception as e:
    print(f"Error during runtime Skyfield check: {e}")
# ----------------------------------------------------------------------

# --- [ثابت‌ها و بارگذاری داده‌های نجومی] ---

PLANETS = ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune', 'pluto']

try:
    # 💡 FIX Ephemeris: استفاده از فایل جدید de440s.bsp برای حل خطای missing 'JUPITER'
    ts = load.timescale()
    eph = load('de440s.bsp')
    
    EPHEMERIS = {p: eph[p] for p in PLANETS}
    EPHEMERIS['earth'] = eph['earth'] 
    
except Exception as e:
    print(f"❌ خطای حیاتی در بارگذاری داده‌های نجومی (Ephemeris): {e}")
    EPHEMERIS = {} 

# ----------------------------------------------------------------------
# تابع اصلی: محاسبه چارت تولد
# ----------------------------------------------------------------------

def calculate_natal_chart(birth_date_jalali: str, birth_time_str: str, city_name: str, latitude: float, longitude: float, timezone_str: str) -> Dict[str, Any]:
    
    if not EPHEMERIS:
        return {"error": "داده‌های نجومی بارگذاری نشده‌اند. (خطای Ephemeris)"}
        
    # 1. تنظیم تاریخ و مکان
    try:
        # ساختن آبجکت JalaliDateTime از دو رشته ورودی
        j_dt_str = f"{birth_date_jalali} {birth_time_str}"
        j_date = JalaliDateTime.strptime(j_dt_str, "%Y/%m/%d %H:%M")
        
        # تبدیل به UTC
        dt_local = j_date.to_gregorian().replace(tzinfo=pytz.timezone(timezone_str))
        dt_utc = dt_local.astimezone(pytz.utc)
        
        t = ts.utc(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour, dt_utc.minute, dt_utc.second)
    except Exception as e:
        return {"error": f"خطا در تبدیل تاریخ و زمان: {e}"}

    # تنظیم محل مشاهده گر (Topos)
    location = Topos(latitude_degrees=latitude, longitude_degrees=longitude)
    observer = EPHEMERIS['earth'] + location
    
    chart_data = {}

    # 2. محاسبه موقعیت سیارات
    for planet_name in PLANETS:
        try:
            planet_ephem = EPHEMERIS[planet_name]
            position = observer.at(t).observe(planet_ephem)
            
            # 💥 FIX Defensive Coding: رفع خطای geometry_of با سازگاری به عقب
            try:
                lon_rad, _, _ = position.geometry_of(t).ecliptic_lonlat(epoch=t)
            except AttributeError:
                pos_apparent = position.apparent()
                lon_rad, _, _ = pos_apparent.frame.ecliptic_lonlat(epoch=t) 

            lon_deg = lon_rad.degrees
            
            chart_data[planet_name] = {
                "degree": lon_deg,
                "lon_dms": f"{int(lon_deg)}°...", 
                "status": "Calculated successfully" 
            }
            
        except Exception as e:
            chart_data[planet_name] = {"error": f"❌ خطا در محاسبه: {str(e)}"}
            
    return chart_data
