# ----------------------------------------------------------------------
# astrology_core.py - ماژول اصلی محاسبات آسترولوژی با استفاده از PYSWISSEPH (نسخه نهایی و اصلاح شده)
# ----------------------------------------------------------------------

import swisseph as se
import pytz
import datetime
import logging
from persiantools.jdatetime import JalaliDateTime
from typing import Dict, Any

# پیکربندی لاگ‌گیری (برای ثبت خطاهای داخلی محاسبات)
# این خط تضمین می‌کند که هر خطای داخلی در لاگ‌های شما ثبت شود.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- [ثابت‌ها و تعاریف] ---

# نگاشت نام سیارات به کدهای داخلی swisseph
PLANETS_MAP = {
    'sun': se.SUN, 'moon': se.MOON, 
    'mercury': se.MERCURY, 'venus': se.VENUS, 'mars': se.MARS, 
    'jupiter': se.JUPITER, 'saturn': se.SATURN, 
    'uranus': se.URANUS, 'neptune': se.NEPTUNE, 'pluto': se.PLUTO,
    'true_node': se.MEAN_NODE, # اضافه شدن گره ماه واقعی
}

# --- [تنظیمات اولیه] ---

try:
    # تعیین مسیر فایل‌های اپمریس. '' به معنای استفاده از مسیرهای پیش‌فرض است.
    se.set_ephe_path('') 
    logging.info("✅ سوپرامریس (Swiss Ephemeris) با موفقیت تنظیم شد.")
except Exception as e:
    logging.error(f"❌ خطای تنظیم Swiss Ephemeris: {e}")
    

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
        
        # محاسبه ساعت کلی UTC (ساعت + دقیقه/60 + ثانیه/3600)
        total_hours_utc = dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0
        
        # 💥 اصلاح ضروری: استفاده از se.julday به جای swe_julday و se.GREGORIAN به جای SE_GREG_CAL
        # se.julday(سال, ماه, روز, ساعت, تقویم)
        jd_utc = se.julday(dt_utc.year, dt_utc.month, dt_utc.day, total_hours_utc, se.GREGORIAN)
        
        # لاگ برای تأیید تبدیل زمان
        logging.info(f"زمان UTC تبدیل شده: {dt_utc.isoformat()}. Julian Day: {jd_utc:.6f}")

    except Exception as e:
        # ثبت خطا و بازگشت پیام خطا
        logging.error(f"خطا در تبدیل تاریخ و زمان ورودی: {e}", exc_info=True)
        return {"error": f"خطا در تبدیل تاریخ و زمان: {e}"}

    
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
            # استفاده از پرچم Topocentric برای دقت بیشتر بر اساس مختصات
            res = se.calc_ut(jd_utc, planet_code, se.SE_FLG_SWIEPH | se.SE_FLG_TOPOCTR) 
            
            lon_deg = res[0][0]
            speed_long = res[0][3]
            
            # تعیین وضعیت (مستقیم یا رجعت)
            status = "Direct"
            if speed_long < -0.000001:
                status = "Retrograde"
            
            chart_data['planets'][planet_name] = {
                "degree": lon_deg,
                "status": status,
            }
            
        except Exception as e:
            logging.error(f"خطا در محاسبه موقعیت سیاره {planet_name}: {e}", exc_info=True)
            chart_data['planets'][planet_name] = {"error": f"❌ خطا در محاسبه: {str(e)}"}
            
    # 3. محاسبه خانه ها (Houses) و آسندانت (Ascendant)
    try:
        house_system = b'P' # سیستم خانه Placidus (رایج‌ترین)
        
        # محاسبه (Houses) و cusps (نوک خانه‌ها)
        cusps, ascmc = se.house_ut(jd_utc, latitude, longitude, house_system)
        
        # آسندانت و میدهیون
        chart_data['houses']['ascendant'] = ascmc[0]
        chart_data['houses']['midheaven'] = ascmc[1]
        
        # نوک 12 خانه
        chart_data['houses']['cusps'] = {i: cusps[i] for i in range(1, 13)}
        
    except Exception as e:
        logging.error(f"خطا در محاسبه خانه‌ها و آسندانت: {e}", exc_info=True)
        chart_data['houses']['error'] = f"❌ خطا در محاسبه خانه‌ها: {str(e)}"
        
    return chart_data
