# ----------------------------------------------------------------------
# astrology_core.py - ماژول اصلی محاسبات آسترولوژی (اصلاح نهایی برای Ephemeris)
# ----------------------------------------------------------------------

import datetime
from skyfield.api import load, Topos
from skyfield.timelib import Time
from typing import Dict, Any, Tuple
from persiantools.jdatetime import JalaliDateTime
import pytz 
import subprocess
import sys

# 💥 FIX: حذف دستور نصب مجدد در زمان اجرا (Runtime Reinstall) 
# این دستور باعث مشکلات فایل و ناسازگاری‌های غیرضروری در محیط Railway می‌شود.
# اگر پکیج‌ها در Dockerfile به درستی نصب شده باشند، نیازی به این کار نیست.

# --- [ثابت‌ها و بارگذاری داده‌های نجومی] ---

# 💡 توجه: لیستی از سیارات مورد نیاز (نام‌های استاندارد Skyfield)
PLANETS = ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune', 'pluto']

try:
    # 💡 FIX Ephemeris: استفاده از فایل استاندارد و کامل de421.bsp 
    ts = load.timescale()
    eph = load('de421.bsp')
    
    # اطمینان از اینکه همه سیارات مورد نیاز در Ephemeris موجود هستند
    EPHEMERIS = {}
    for p in PLANETS:
        # اگر سیاره مستقیماً در eph موجود نبود، ممکن است خطایی رخ دهد، که با try/except حل می‌شود
        EPHEMERIS[p] = eph[p]
        
    EPHEMERIS['earth'] = eph['earth'] 
    
    print("✅ داده‌های نجومی با موفقیت بارگذاری شدند.")
    
except Exception as e:
    # این خطا دقیقاً همان خطایی است که در لاگ‌ها دیدیم (missing 'MARS' یا 'JUPITER')
    print(f"❌ خطای حیاتی در بارگذاری داده‌های نجومی (Ephemeris): {e}")
    EPHEMERIS = {} 

# ----------------------------------------------------------------------
# تابع اصلی: محاسبه چارت تولد
# ----------------------------------------------------------------------

def calculate_natal_chart(birth_date_jalali: str, birth_time_str: str, city_name: str, latitude: float, longitude: float, timezone_str: str) -> Dict[str, Any]:
    
    # 1. بررسی وضعیت بارگذاری Ephemeris
    if not EPHEMERIS:
        # اگر دیکشنری EPHEMERIS خالی باشد، یعنی بارگذاری در زمان شروع برنامه شکست خورده است
        return {"error": "داده‌های نجومی بارگذاری نشده‌اند. (خطای Ephemeris)"}
        
    # 2. تنظیم تاریخ و مکان
    try:
        # ts از بخش global بارگذاری می‌شود
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

    # 3. محاسبه موقعیت سیارات
    for planet_name in PLANETS:
        try:
            # استفاده از آبجکت‌های از قبل بارگذاری شده
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
                "lon_dms": f"{lon_deg:.2f}°...", 
                "status": "Calculated successfully" 
            }
            
        except KeyError:
            # اگر بارگذاری Ephemeris موفق بود، اما سیاره‌ای در PLANETS پیدا نشد (نباید اتفاق بیفتد)
            chart_data[planet_name] = {"error": f"❌ سیاره '{planet_name}' در Ephemeris موجود نیست."}
        except Exception as e:
            chart_data[planet_name] = {"error": f"❌ خطا در محاسبه: {str(e)}"}
            
    return chart_data
