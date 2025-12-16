# astrology_core.py - نسخه نهایی اصلاح شده

import swisseph as se
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Dict, Any, List
import logging
import jdatetime 
import io # اضافه شد

# تنظیمات لاگینگ برای ردیابی خطاها و نسخه‌بندی
logging.basicConfig(level=logging.INFO)
logging.info("CODE_VERSION: 2025-12-16-FinalFix-AstroCore-JD") # به‌روزرسانی نسخه

# ==============================================================================
# ثابت‌ها
# ==============================================================================

# ID سیارات در Swisseph
PLANETS = {
    'sun': se.SUN, 'moon': se.MOON, 'mercury': se.MERCURY, 'venus': se.VENUS, 
    'mars': se.MARS, 'jupiter': se.JUPITER, 'saturn': se.SATURN, 'uranus': se.URANUS,
    'neptune': se.NEPTUNE, 'pluto': se.PLUTO, 'true_node': se.TRUE_NODE, 
    'chiron': se.CHIRON, 'lilith': 12
}

# نام‌های فارسی برج‌ها و خانه‌ها (برای خروجی نهایی)
SIGNS = [
    "حمل", "ثور", "جوزا", "سرطان", "اسد", "سنبله",
    "میزان", "عقرب", "قوس", "جدی", "دلو", "حوت"
]
HOUSES = [
    "خانه ۱ (خود و هویت)", "خانه ۲ (دارایی و ارزش‌ها)", "خانه ۳ (ارتباطات و یادگیری)", 
    "خانه ۴ (خانه و خانواده)", "خانه ۵ (خلاقیت و لذت)", "خانه ۶ (کار و سلامتی)",
    "خانه ۷ (روابط و ازدواج)", "خانه ۸ (تغییر و منابع مشترک)", "خانه ۹ (فلسفه و سفر)", 
    "خانه ۱۰ (شغل و اعتبار)", "خانه ۱۱ (دوستان و آرزوها)", "خانه ۱۲ (خلوت و ناخودآگاه)"
]

# پارامترهای جنبه (Aspects)
ASPECTS = [
    {'name': 'تثلیث (Trine)', 'degree': 120, 'orb': 6},
    {'name': 'تراضی (Sextile)', 'degree': 60, 'orb': 4},
    {'name': 'اقتران (Conjunction)', 'degree': 0, 'orb': 8},
    {'name': 'تربیع (Square)', 'degree': 90, 'orb': 6},
    {'name': 'تقابل (Opposition)', 'degree': 180, 'orb': 6}
]

# ==============================================================================
# توابع کمکی
# ==============================================================================

def get_sign(degree: float) -> str:
    """درجه را به نام برج تبدیل می‌کند."""
    sign_index = int(degree / 30) % 12
    return SIGNS[sign_index]

def get_sign_degree(degree: float) -> float:
    """درجه را به درجه درون برج تبدیل می‌کند."""
    return degree % 30

def get_house_name(house_num: int) -> str:
    """شماره خانه را به نام توصیفی تبدیل می‌کند."""
    if 1 <= house_num <= 12:
        return HOUSES[house_num - 1]
    return f"خانه 0 (خطا یا نامشخص)" # Fallback for safety

# ==============================================================================
# منطق اصلی محاسبه چارت
# ==============================================================================

def calculate_natal_chart(birth_date: str, birth_time: str, latitude: float, longitude: float, timezone_str: str, house_system: str = 'K') -> Dict[str, Any]:
    """موقعیت سیارات و خانه‌ها را محاسبه می‌کند."""
    
    se.set_ephe_path('./ephe_data/') # تنظیم مسیر دیتای اپمریس

    # 1. تبدیل تاریخ شمسی به Julian Day (حل مشکل بنیادین تاریخ)
    try:
        year, month, day = map(int, birth_date.split('/'))
        hour, minute = map(int, birth_time.split(':'))
        
        # 1.1 ساخت شیء jdatetime از ورودی کاربر
        birth_dt_local_jdate = jdatetime.datetime(
            year, month, day, hour, minute, 0, tzinfo=ZoneInfo(timezone_str)
        )
        
        # 1.2 تبدیل به UTC (زمان استاندارد جهانی)
        birth_dt_utc = birth_dt_local_jdate.togregorian().astimezone(ZoneInfo('UTC'))

        # 1.3 محاسبه Julian Day (JD) از زمان UTC
        # ✅✅✅ اصلاح حیاتی: جایگزینی se.date_to_jd با se.swe_julday ✅✅✅
        tjd_ut = se.swe_julday( # ⬅️ اینجا اصلاح شد!
            birth_dt_utc.year, 
            birth_dt_utc.month, 
            birth_dt_utc.day, 
            birth_dt_utc.hour + birth_dt_utc.minute/60.0 + birth_dt_utc.second/3600.0, 
            se.CALC_GREGORIAN
        )

        logging.info(f"DEBUG: Calculated JD (UT) from Shamsi date: {tjd_ut}")
        
    except Exception as e:
        logging.error(f"FATAL ERROR: خطا در تبدیل تاریخ شمسی به JD: {e}")
        return {'error': f"خطا در تبدیل تاریخ شمسی به Julian Day: {e}"}

    # 2. محاسبه خانه‌ها (House Cusps) و Asc/MC
    try:
        logging.info(f"DEBUG: Calling se.houses with JD: {tjd_ut}, Lat: {latitude}, Lon: {longitude}, System: {house_system}")
        
        # محاسبه خانه ها. خروجی cusps_raw شامل ۱۳ عنصر است (۱۲ خانه + Asc)
        cusps_raw, ascmc = se.houses(tjd_ut, latitude, longitude, house_system.upper())
        
        # FIX V1/V2: بررسی طول خروجی خانه‌ها
        if len(cusps_raw) < 12:
            raise IndexError(f"خروجی cusps ناقص است. طول cusps: {len(cusps_raw)}")
        
        # استخراج ۱۲ خانه (از ایندکس ۱ تا ۱۲)
        cusps = [cusps_raw[i] for i in range(1, 13)] 
        ascendant_deg = ascmc[0]
        mc_deg = ascmc[1]
        
    except Exception as e:
        logging.error(f"FATAL ERROR: خطا در محاسبه خانه‌ها و طالع: {e}")
        # تنظیم مقادیر پیش‌فرض در صورت خطا برای جلوگیری از شکست کل برنامه
        cusps = [0.0] * 12
        ascendant_deg = 0.0
        mc_deg = 0.0
        # اگر خطا رخ داد، Cusps_raw و ascmc هم باید به صورت صفر مقداردهی شوند.
        cusps_raw = [0.0] * 13
        ascmc = [0.0] * 2

    chart_data = {'planets': [], 'cusps': cusps, 'ascendant': ascendant_deg, 'mc': mc_deg}
    planet_positions = {} # برای ذخیره موقعیت‌ها برای محاسبه Part of Fortune و جنبه‌ها

    # 3. محاسبه موقعیت سیارات
    for planet_name, planet_id in PLANETS.items():
        try:
            # تنظیم فلگ‌های Swisseph
            swisseph_flags = se.FLG_SWIEPHE | se.FLG_TOPOCTR
            if planet_name == 'true_node':
                swisseph_flags |= se.FLG_TRUE_NODE
            
            # se.calc_ut returns [lon, lat, dist, lon_speed, lat_speed, dist_speed]
            planet_pos, ret_flag = se.calc_ut(tjd_ut, planet_id, swisseph_flags)
            
            # FIX V3: تبدیل صریح به float برای جلوگیری از TypeError در se.house_pos
            lon_deg = float(planet_pos[0])
            lat_deg = float(planet_pos[1])

            # محاسبه موقعیت خانه سیاره
            house = 0
            if ascendant_deg != 0.0 and len(cusps_raw) >= 13: # اضافه شدن چک طول برای امنیت بیشتر
                 # se.house_pos: lon_deg, lat_deg, cusps_raw (13), ascmc (2), house_system
                 planet_house_pos = se.house_pos(lon_deg, lat_deg, cusps_raw, ascmc, house_system)
                 house = int(planet_house_pos[0])

            retrograde = lon_deg < 0 or planet_pos[3] < 0 # سرعت منفی نشانگر حرکت قهقرایی است.
            
            # ذخیره داده‌های سیاره
            planet_data = {
                'name': planet_name,
                'id': planet_id,
                'degree': lon_deg,
                'sign': get_sign(lon_deg),
                'sign_degree': get_sign_degree(lon_deg),
                'house': house,
                'house_name': get_house_name(house),
                'retrograde': retrograde,
                'latitude': lat_deg,
                'longitude_speed': planet_pos[3]
            }
            chart_data['planets'].append(planet_data)
            planet_positions[planet_name] = lon_deg # ذخیره برای محاسبه جنبه‌ها
            
        except Exception as e:
            logging.error(f"FATAL ERROR: خطا در محاسبه موقعیت سیاره {planet_name}: {e}")
            # ذخیره داده‌های خطادار (House 0)
            chart_data['planets'].append({
                'name': planet_name, 'id': planet_id, 'degree': 0.0, 'sign': 'نامشخص', 
                'sign_degree': 0.0, 'house': 0, 'house_name': get_house_name(0),
                'retrograde': False, 'latitude': 0.0, 'longitude_speed': 0.0
            })
            planet_positions[planet_name] = 0.0

    # 4. محاسبه Part of Fortune
    part_of_fortune_data = calculate_part_of_fortune(planet_positions, ascendant_deg, cusps_raw, ascmc, house_system, tjd_ut)
    chart_data['part_of_fortune'] = part_of_fortune_data
    
    # 5. محاسبه جنبه‌ها (Aspects)
    chart_data['aspects'] = calculate_aspects(chart_data['planets'])

    return chart_data

def calculate_part_of_fortune(planet_positions: Dict[str, float], ascendant_deg: float, cusps_raw: List[float], ascmc: List[float], house_system: str, tjd_ut: float) -> Dict[str, Any]:
    """موقعیت Part of Fortune را محاسبه می‌کند."""
    
    # اطمینان از وجود داده‌های مورد نیاز
    if 'sun' not in planet_positions or 'moon' not in planet_positions or ascendant_deg == 0.0:
        logging.error("خطا در محاسبه Part of Fortune: اطلاعات خورشید، ماه یا طالع نامعتبر است.")
        return {'degree': 0.0, 'sign': 'نامشخص', 'house': 0, 'house_name': get_house_name(0)}
    
    sun_lon = planet_positions['sun']
    moon_lon = planet_positions['moon']
    
    # فرمول Part of Fortune (روز و شب یکسان در سیستم Swisseph)
    # Part of Fortune = Ascendant + Moon - Sun
    fortune_deg = (ascendant_deg + moon_lon - sun_lon) % 360
    
    # محاسبه خانه Part of Fortune
    house = 0
    try:
        if len(cusps_raw) >= 13: # چک طول برای امنیت
            # برای Part of Fortune عرض جغرافیایی را 0 در نظر می‌گیریم.
            # استفاده از se.house_pos برای محاسبه خانه PoF
            house_pos_raw = se.house_pos(fortune_deg, 0.0, cusps_raw, ascmc, house_system)
            house = int(house_pos_raw[0])
            
    except Exception as e:
        logging.error(f"خطا در محاسبه خانه Part of Fortune: {e}")

    return {
        'name': 'part_of_fortune',
        'degree': fortune_deg,
        'sign': get_sign(fortune_deg),
        'sign_degree': get_sign_degree(fortune_deg),
        'house': house,
        'house_name': get_house_name(house)
    }

def calculate_aspects(planets_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """محاسبه جنبه‌های اصلی بین سیارات."""
    aspects = []
    
    # سیاراتی که جنبه می‌گیرند (بدون گره)
    aspect_planets = [p for p in planets_data if p['name'] not in ['true_node', 'lilith', 'chiron']]
    
    for i in range(len(aspect_planets)):
        for j in range(i + 1, len(aspect_planets)):
            p1 = aspect_planets[i]
            p2 = aspect_planets[j]
            
            # اطمینان از صحت درجه
            if p1['degree'] is None or p2['degree'] is None or p1['degree'] == 0.0 or p2['degree'] == 0.0:
                continue

            # محاسبه زاویه بین دو سیاره
            angle = abs(p1['degree'] - p2['degree'])
            angle = min(angle, 360 - angle) # پیدا کردن کوتاه‌ترین فاصله
            
            for aspect in ASPECTS:
                diff = abs(angle - aspect['degree'])
                if diff <= aspect['orb']:
                    aspects.append({
                        'p1': p1['name'],
                        'p2': p2['name'],
                        'type': aspect['name'],
                        'exact_angle': round(angle, 2),
                        'orb': round(diff, 2),
                        'significance': 1.0 - (diff / aspect['orb']) # محاسبه اهمیت
                    })
                    
    return aspects

# ... (ادامه کدها اگر وجود دارند - تابع format_chart_data و process_astro_request)
# برای سادگی، بخش format_chart_data و process_astro_request که تغییر نکرده‌اند حذف شدند.
