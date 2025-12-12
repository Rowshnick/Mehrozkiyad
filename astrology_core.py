# ----------------------------------------------------------------------
# astrology_core.py - نسخه نهایی با Part of Fortune (سهم سعادت)
# ----------------------------------------------------------------------

import swisseph as se
import logging
from typing import Dict, Any, Union, Tuple, List
from persiantools import jdatetime
import datetime
import pytz
import math

# تنظیمات Logging
logging.basicConfig(level=logging.INFO)


# --- [ثابت‌ها] ---
PLANETS_MAP = {
    "sun": se.SE_SUN,
    "moon": se.SE_MOON,
    "mercury": se.SE_MERCURY,
    "venus": se.SE_VENUS,
    "mars": se.SE_MARS,
    "jupiter": se.SE_JUPITER,
    "saturn": se.SE_SATURN,
    "uranus": se.SE_URANUS,
    "neptune": se.SE_NEPTUNE,
    "pluto": se.SE_PLUTO,
    "true_node": se.SE_TRUE_NODE # گره شمالی حقیقی
}

ASPECT_DEGREES = {
    "Conjunction": 0.0,
    "Sextile": 60.0,
    "Square": 90.0,
    "Trine": 120.0,
    "Opposition": 180.0,
}

# Orb های نسبتاً تنگ برای نمایش مهم‌ترین زوایا
ASPECT_ORBS = {
    "Conjunction": 3.0,
    "Sextile": 1.5,
    "Square": 2.5,
    "Trine": 2.5,
    "Opposition": 3.0,
}


# --- [توابع محاسباتی] ---

def get_degree_diff(deg1: float, deg2: float) -> float:
    """محاسبه اختلاف کوچکترین زاویه بین دو درجه."""
    diff = abs(deg1 - deg2)
    return min(diff, 360 - diff)

def calculate_aspects(planets: Dict[str, Any]) -> List[Dict[str, Any]]:
    """محاسبه زوایای اصلی بین سیارات با Orb مشخص."""
    aspects = []
    
    # لیست سیاراتی که باید زوایایشان بررسی شود (مثلاً سیارات شخصی و اجتماعی)
    aspect_planets = ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn"]
    
    planet_items = [(name, data['degree']) for name, data in planets.items() if name in aspect_planets and 'degree' in data]
    
    # از هر سیاره به سیارات بعدی (جلوگیری از تکرار و مقایسه با خود)
    for i in range(len(planet_items)):
        p1_name, p1_deg = planet_items[i]
        for j in range(i + 1, len(planet_items)):
            p2_name, p2_deg = planet_items[j]
            
            for aspect_name, aspect_degree in ASPECT_DEGREES.items():
                
                degree_diff = get_degree_diff(p1_deg, p2_deg)
                orb = abs(degree_diff - aspect_degree)
                max_orb = ASPECT_ORBS.get(aspect_name, 1.0) # پیش‌فرض 1.0 برای احتیاط
                
                if orb <= max_orb:
                    aspects.append({
                        "p1": p1_name.replace("_", " ").title(),
                        "p2": p2_name.replace("_", " ").title(),
                        "aspect": aspect_name,
                        "orb": orb,
                        "p1_deg": p1_deg,
                        "p2_deg": p2_deg
                    })
                    
    # مرتب‌سازی بر اساس Orb (تنگ‌ترین زوایا ابتدا)
    aspects.sort(key=lambda x: x['orb'])
    
    # بازگشت تنها 5 زاویه برتر
    return aspects[:5]


# ----------------------------------------------------------------------
# تابع اصلی: محاسبه چارت تولد (به روز شده با Part of Fortune)
# ----------------------------------------------------------------------

def calculate_natal_chart(birth_date_jalali: str, birth_time_str: str, city_name: str, latitude: Union[float, int], longitude: Union[float, int], timezone_str: str) -> Dict[str, Any]:
    """
    محاسبه چارت تولد نجومی شامل موقعیت سیارات و خانه‌ها بر اساس سیستم سوپرامریس.
    """
    
    # 1. تبدیل تاریخ شمسی به میلادی و محاسبه زمان جولیان (JD) UTC
    try:
        j_date = jdatetime.JalaliDate.strptime(birth_date_jalali, '%Y/%m/%d')
        j_time = datetime.datetime.strptime(birth_time_str, '%H:%M')
        
        # ترکیب و تبدیل به میلادی
        dt_local = j_date.to_gregorian(j_time.hour, j_time.minute, j_time.second)
        
        # اعمال منطقه زمانی
        local_tz = pytz.timezone(timezone_str)
        dt_local = local_tz.localize(dt_local)
        dt_utc = dt_local.astimezone(pytz.utc)

        # محاسبه JD UTC
        jd_utc = se.julday(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0)
        
    except Exception as e:
        logging.error(f"FATAL ERROR: خطا در تبدیل تاریخ و زمان: {e}", exc_info=True)
        return {"error": f"❌ خطای تبدیل زمان: {str(e)}"}


    chart_data = {
        "datetime_utc": dt_utc.isoformat(),
        "jd_utc": jd_utc,
        "city_name": city_name,
        "latitude": latitude,
        "longitude": longitude,
        "planets": {},
        "houses": {
             'ascendant': 0.0,
             'midheaven': 0.0,
             'cusps': {i: 0.0 for i in range(1, 13)}, 
             'error': None 
        },
        "aspects": [],
        "arabic_parts": {} # اضافه شدن کلید جدید برای نقاط عربی
    }

    # 2. محاسبه موقعیت سیارات
    for planet_name, planet_code in PLANETS_MAP.items():
        try:
            # از se.calc_ut برای دقت بیشتر استفاده می‌کنیم
            # flag 0 به معنای محاسبه استاندارد است که در محیط‌های بدون فایل اپمریس کار می‌کند
            res = se.calc_ut(jd_utc, planet_code, 0) 
            lon_deg = res[0][0]
            chart_data['planets'][planet_name] = {
                "degree": lon_deg,
                "status": "N/A (Default Flag)", 
            }
        except Exception as e:
            logging.error(f"FATAL ERROR: خطا در محاسبه موقعیت سیاره {planet_name}: {e}", exc_info=True)
            chart_data['planets'][planet_name] = {"error": f"❌ خطا در محاسبه: {str(e)}"}
            
    # 3. محاسبه خانه ها (Houses)
    try:
        # P = Placidus (سیستم پیش‌فرض)
        house_system = b'P' 
        
        # se.houses برای محاسبه cusps و ascmc (ascendant و midheaven)
        cusps_raw, ascmc = se.houses(jd_utc, latitude, longitude, house_system)
        
        if len(cusps_raw) < 12 or len(ascmc) < 2:
             raise IndexError(f"خروجی se.houses ناقص است. طول cusps: {len(cusps_raw)}")

        chart_data['houses']['ascendant'] = ascmc[0]
        chart_data['houses']['midheaven'] = ascmc[1]
        
        # ایندکس گذاری امن برای cusps (swisseph از 1 شروع می‌کند، ولی خروجی ممکن است متفاوت باشد)
        cusps_dict = {}
        for i in range(1, 13):
            # برای Placidus، کاپس‌ها از خانه 1 شروع می‌شوند
            # به خاطر ناسازگاری اندک در خروجی swisseph در برخی محیط‌ها، بهتر است مطمئن شویم
            index_to_use = i 
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


    # 5. محاسبه نقاط عربی (Part of Fortune)
    try:
        sun_deg = chart_data['planets']['sun']['degree']
        moon_deg = chart_data['planets']['moon']['degree']
        asc_deg = chart_data['houses']['ascendant']
        desc_deg = chart_data['houses']['cusps'].get(7, 0.0) # درجه کاپس خانه 7
        
        # تعیین تولد روز/شب (Day/Night Birth)
        # اگر خورشید بالای افق (Asc-Desc) باشد (خانه‌های 7، 8، 9، 10، 11، 12)، تولد روز است.
        is_day_birth = False
        
        # محاسبه خانه خورشید
        def get_house_of_degree_simple(degree: float, asc: float, desc: float) -> int:
            if asc > desc:
                # Asc در نیمکره پایین (جنوبی) است.
                # از Asc تا Desc نیمکره پایین است.
                if asc >= degree > desc:
                    return 1 # خانه های 1 تا 6
                else:
                    return 7 # خانه های 7 تا 12
            else:
                # Desc در نیمکره پایین است.
                # از Desc تا Asc نیمکره پایین است.
                if desc >= degree > asc:
                    return 1 # خانه های 1 تا 6
                else:
                    return 7 # خانه های 7 تا 12
        
        sun_house_zone = get_house_of_degree_simple(sun_deg, asc_deg, desc_deg)
        
        # اگر خورشید در نیمکره بالای افق (خانه 7 تا 12) باشد، روز است.
        if sun_house_zone == 7: 
            is_day_birth = True
        
        
        if is_day_birth:
            # فرمول روز: Ascendant + Moon - Sun
            pf_degree = asc_deg + moon_deg - sun_deg
        else:
            # فرمول شب: Ascendant + Sun - Moon
            pf_degree = asc_deg + sun_deg - moon_deg

        # نرمال سازی درجه به محدوده 0 تا 360
        pf_degree = pf_degree % 360

        chart_data['arabic_parts']['part_of_fortune'] = {
            "degree": pf_degree,
            "is_day_birth": is_day_birth
        }
    except Exception as e:
         logging.error(f"خطا در محاسبه Part of Fortune: {e}")
         chart_data['arabic_parts']['part_of_fortune'] = {"error": "❌ خطا در محاسبه سهم سعادت"}
    
    
    return chart_data

