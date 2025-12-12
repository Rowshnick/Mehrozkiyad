# ----------------------------------------------------------------------
# astrology_core.py - ماژول اصلی محاسبات آسترولوژی (نسخه نهایی و پایدار)
# ----------------------------------------------------------------------

import swisseph as se
import pytz
import datetime
import logging
from persiantools.jdatetime import JalaliDateTime
from typing import Dict, Any, Union

# پیکربندی لاگ‌گیری
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- [ثابت‌ها و تعاریف] ---

# نگاشت نام سیارات به کدهای داخلی swisseph
PLANETS_MAP = {
    'sun': se.SUN, 'moon': se.MOON, 
    'mercury': se.MERCURY, 'venus': se.VENUS, 'mars': se.MARS, 
    'jupiter': se.JUPITER, 'saturn': se.SATURN, 
    'uranus': se.URANUS, 'neptune': se.NEPTUNE, 'pluto': se.PLUTO,
    'true_node': se.MEAN_NODE, 
}

# 💡 نکته مهم: تعریف CALCULATION_FLAGS از این مکان حذف شد تا از Attribute Error در زمان استارت آپ جلوگیری شود.

# --- [تنظیمات اولیه] ---

# سعی در تنظیم مسیر اپمریس.
try:
    se.set_ephe_path('') 
    logging.info("✅ سوپرامریس (Swiss Ephemeris) با موفقیت تنظیم شد.")
except Exception as e:
    logging.error(f"❌ خطای تنظیم Swiss Ephemeris: {e}")
    

# ----------------------------------------------------------------------
# تابع اصلی: محاسبه چارت تولد
# ----------------------------------------------------------------------

def calculate_natal_chart(birth_date_jalali: str, birth_time_str: str, city_name: str, latitude: Union[float, int], longitude: Union[float, int], timezone_str: str) -> Dict[str, Any]:
    
    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except (TypeError, ValueError) as e:
        err_msg = f"خطا در تبدیل مختصات (Lat/Lon) به عدد: {e}"
        logging.error(err_msg, exc_info=True)
        return {"error": err_msg}


    # 1. تبدیل تاریخ و زمان
    try:
        j_dt_str = f"{birth_date_jalali} {birth_time_str}"
        j_date = JalaliDateTime.strptime(j_dt_str, "%Y/%m/%d %H:%M") 
        
        dt_local = j_date.to_gregorian().replace(tzinfo=pytz.timezone(timezone_str))
        dt_utc = dt_local.astimezone(pytz.utc)
        
        total_hours_utc = dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0
        
        jd_utc = se.julday(dt_utc.year, dt_utc.month, dt_utc.day, total_hours_utc, 1)
        
        logging.info(f"زمان UTC تبدیل شده: {dt_utc.isoformat()}. Julian Day: {jd_utc:.6f}")

    except Exception as e:
        err_msg = f"خطا در تبدیل تاریخ و زمان ورودی: {e}"
        logging.error(err_msg, exc_info=True)
        return {"error": err_msg}

    
    chart_data = {
        "datetime_utc": dt_utc.isoformat(),
        "jd_utc": jd_utc,
        "city_name": city_name,
        "latitude": latitude,
        "longitude": longitude,
        "planets": {},
        "houses": {}
    }

    # 2. محاسبه موقعیت سیارات
    for planet_name, planet_code in PLANETS_MAP.items():
        try:
            # 💡 استفاده از پرچم 0 (پیش‌فرض) برای جلوگیری از Attribute Error
            res = se.calc_ut(jd_utc, planet_code, 0) 
            
            lon_deg = res[0][0]
            # محاسبه سرعت (برای تعیین Direct/Retrograde) حذف شد زیرا به پرچم‌های مشکل‌زا نیاز داشت.
            
            chart_data['planets'][planet_name] = {
                "degree": lon_deg,
                "status": "N/A (Default Flag)", 
            }
            
        except Exception as e:
            logging.error(f"FATAL ERROR: خطا در محاسبه موقعیت سیاره {planet_name}: {e}", exc_info=True)
            chart_data['planets'][planet_name] = {"error": f"❌ خطا در محاسبه: {str(e)}"}
            
    # 3. محاسبه خانه ها (Houses) و آسندانت (Ascendant)
    try:
        house_system = b'P' # سیستم خانه Placidus 
        
        # 💡 استفاده از se.houses (به جای house_ut) برای سازگاری با نسخه‌های قدیمی‌تر
        cusps, ascmc = se.houses(jd_utc, latitude, longitude, house_system)
        
        chart_data['houses']['ascendant'] = ascmc[0]
        chart_data['houses']['midheaven'] = ascmc[1]
        
        chart_data['houses']['cusps'] = {i: cusps[i] for i in range(1, 13)}
        
    except Exception as e:
        err_msg = f"FATAL ERROR: خطا در محاسبه خانه‌ها و آسندانت: {e}"
        logging.error(err_msg, exc_info=True)
        chart_data['houses']['error'] = f"❌ خطا در محاسبه خانه‌ها: {str(e)}"
        
    return chart_data
