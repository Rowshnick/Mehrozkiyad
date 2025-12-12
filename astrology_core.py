# ----------------------------------------------------------------------
# astrology_core.py - نسخه نهایی با محاسبه زوایا (Aspects)
# ----------------------------------------------------------------------

import swisseph as se
import pytz
import datetime
import logging
from persiantools.jdatetime import JalaliDateTime
from typing import Dict, Any, Union, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- [ثابت‌ها و تعاریف] ---

PLANETS_MAP = {
    'sun': se.SUN, 'moon': se.MOON, 
    'mercury': se.MERCURY, 'venus': se.VENUS, 'mars': se.MARS, 
    'jupiter': se.JUPITER, 'saturn': se.SATURN, 
    'uranus': se.URANUS, 'neptune': se.NEPTUNE, 'pluto': se.PLUTO,
    'true_node': se.MEAN_NODE, 
}

# تعریف زوایای اصلی و اورب (Orb - حداکثر فاصله مجاز) برای چارت تولد
ASPECT_DEGREES = {
    "Conjunction": 0.0,      # اقتران
    "Sextile": 60.0,         # تسدیس
    "Square": 90.0,          # تربيع
    "Trine": 120.0,          # تثلیث
    "Opposition": 180.0,     # تقابل
}

ASPECT_ORBS = {
    "Conjunction": 8.0,
    "Opposition": 8.0,
    "Trine": 6.0,
    "Square": 6.0,
    "Sextile": 4.0,
}

# --- [توابع محاسباتی جدید] ---

def calculate_aspects(planets_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """محاسبه زوایای اصلی بین سیارات بر اساس درجه‌های آن‌ها."""
    aspects = []
    
    planet_names = list(planets_data.keys())
    
    for i in range(len(planet_names)):
        for j in range(i + 1, len(planet_names)):
            p1_name = planet_names[i]
            p2_name = planet_names[j]
            
            # اگر محاسبه سیاره با خطا مواجه شده، صرفنظر کن
            if 'error' in planets_data[p1_name] or 'error' in planets_data[p2_name]:
                continue
                
            p1_deg = planets_data[p1_name]['degree']
            p2_deg = planets_data[p2_name]['degree']
            
            # محاسبه فاصله زاویه‌ای و تنظیم برای کوتاه‌ترین فاصله در دایره (حداکثر 180 درجه)
            diff = abs(p1_deg - p2_deg)
            if diff > 180:
                diff = 360 - diff
                
            for aspect_name, aspect_degree in ASPECT_DEGREES.items():
                orb = ASPECT_ORBS[aspect_name]
                
                # بررسی اینکه آیا فاصله در محدوده Orb قرار دارد
                if abs(diff - aspect_degree) <= orb:
                    aspects.append({
                        "p1": p1_name.capitalize(),
                        "p2": p2_name.capitalize(),
                        "aspect": aspect_name,
                        "degree": aspect_degree,
                        "orb": abs(diff - aspect_degree)
                    })
                    
    # مرتب‌سازی بر اساس تنگی Orb (کوچکترین Orb مهم‌ترین است)
    aspects.sort(key=lambda x: x['orb'])
    
    # فقط 5 زاویه‌ی تنگ (مهم) را برمی‌گردانیم
    return aspects[:5]


# --- [تنظیمات اولیه] ---

try:
    se.set_ephe_path('') 
    logging.info("✅ سوپرامریس (Swiss Ephemeris) با موفقیت تنظیم شد.")
except Exception as e:
    logging.error(f"❌ خطای تنظیم Swiss Ephemeris: {e}")
    
# ----------------------------------------------------------------------
# تابع اصلی: محاسبه چارت تولد (به روز شده)
# ----------------------------------------------------------------------

def calculate_natal_chart(birth_date_jalali: str, birth_time_str: str, city_name: str, latitude: Union[float, int], longitude: Union[float, int], timezone_str: str) -> Dict[str, Any]:
    
    # ... (بخش تبدیل تاریخ و زمان - بدون تغییر)
    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except (TypeError, ValueError) as e:
        return {"error": f"خطا در تبدیل مختصات: {e}"}

    try:
        j_dt_str = f"{birth_date_jalali} {birth_time_str}"
        j_date = JalaliDateTime.strptime(j_dt_str, "%Y/%m/%d %H:%M") 
        dt_local = j_date.to_gregorian().replace(tzinfo=pytz.timezone(timezone_str))
        dt_utc = dt_local.astimezone(pytz.utc)
        total_hours_utc = dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0
        jd_utc = se.julday(dt_utc.year, dt_utc.month, dt_utc.day, total_hours_utc, 1)
        
    except Exception as e:
        return {"error": f"خطا در تبدیل تاریخ و زمان: {e}"}

    
    chart_data = {
        "datetime_utc": dt_utc.isoformat(),
        "jd_utc": jd_utc,
        "city_name": city_name,
        "latitude": latitude,
        "longitude": longitude,
        "planets": {},
        # ساختار دهی houses و aspects قبل از تلاش برای محاسبه
        "houses": {
             'ascendant': 0.0,
             'midheaven': 0.0,
             'cusps': {i: 0.0 for i in range(1, 13)}, 
             'error': None 
        },
        "aspects": [] # 💡 اضافه شدن کلید جدید برای زوایا
    }

    # 2. محاسبه موقعیت سیارات (بدون تغییر)
    for planet_name, planet_code in PLANETS_MAP.items():
        try:
            res = se.calc_ut(jd_utc, planet_code, 0) 
            lon_deg = res[0][0]
            chart_data['planets'][planet_name] = {
                "degree": lon_deg,
                "status": "N/A (Default Flag)", 
            }
        except Exception as e:
            logging.error(f"FATAL ERROR: خطا در محاسبه موقعیت سیاره {planet_name}: {e}", exc_info=True)
            chart_data['planets'][planet_name] = {"error": f"❌ خطا در محاسبه: {str(e)}"}
            
    # 3. محاسبه خانه ها (Houses) (با مدیریت خطای نهایی)
    try:
        house_system = b'P' 
        cusps_raw, ascmc = se.houses(jd_utc, latitude, longitude, house_system)
        
        if len(cusps_raw) < 12 or len(ascmc) < 2:
             raise IndexError(f"خروجی se.houses ناقص است. طول cusps: {len(cusps_raw)}")

        chart_data['houses']['ascendant'] = ascmc[0]
        chart_data['houses']['midheaven'] = ascmc[1]
        
        # ایندکس گذاری امن برای cusps
        cusps_dict = {}
        for i in range(1, 13):
            index_to_use = i if len(cusps_raw) > 12 else i - 1 
            if index_to_use >= 0 and index_to_use < len(cusps_raw):
                cusps_dict[i] = cusps_raw[index_to_use]
            else:
                cusps_dict[i] = 0.0 

        chart_data['houses']['cusps'] = cusps_dict
        chart_data['houses']['error'] = None 
        
    except Exception as e:
        err_msg = f"FATAL ERROR: خطا در محاسبه خانه‌ها و آسندانت: {e}"
        logging.error(err_msg, exc_info=True)
        chart_data['houses']['error'] = f"❌ خطای محاسبه خانه‌ها: {str(e)}"
    
    # 4. محاسبه زوایا (Aspects)
    chart_data['aspects'] = calculate_aspects(chart_data['planets'])
    
    return chart_data
