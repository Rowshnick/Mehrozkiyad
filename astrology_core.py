# astrology_core.py - نسخه نهایی اصلاح شده، مقاوم در برابر خطا و آماده برای تصویرسازی

import swisseph as se
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Dict, Any, List
import logging
import jdatetime 
import io 
import math
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

# تنظیمات لاگینگ برای ردیابی خطاها و نسخه‌بندی
logging.basicConfig(level=logging.INFO)
logging.info("CODE_VERSION: 2025-12-16-FinalFix-AstroCore-FINAL-ROBUST") 

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

# نام‌های فارسی برج‌ها 
SIGNS = [
    "حمل", "ثور", "جوزا", "سرطان", "اسد", "سنبله",
    "میزان", "عقرب", "قوس", "جدی", "دلو", "حوت"
]
HOUSES = [
    "خانه ۱", "خانه ۲", "خانه ۳", "خانه ۴", "خانه ۵", "خانه ۶",
    "خانه ۷", "خانه ۸", "خانه ۹", "خانه ۱۰", "خانه ۱۱", "خانه ۱۲"
]

# پارامترهای جنبه (Aspects)
ASPECTS = [
    {'name': 'تثلیث', 'degree': 120, 'orb': 6},
    {'name': 'تراضی', 'degree': 60, 'orb': 4},
    {'name': 'اقتران', 'degree': 0, 'orb': 8},
    {'name': 'تربیع', 'degree': 90, 'orb': 6},
    {'name': 'تقابل', 'degree': 180, 'orb': 6}
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
    return f"خانه 0" 

# ==============================================================================
# منطق اصلی محاسبه چارت
# ==============================================================================

def calculate_natal_chart(birth_date: str, birth_time: str, latitude: float, longitude: float, timezone_str: str, house_system: str = 'K') -> Dict[str, Any]:
    """موقعیت سیارات و خانه‌ها را محاسبه می‌کند."""
    
    # تنظیم مسیر دیتای اپمریس (اگرچه در داکر باید از طریق متغیر محیطی انجام شود)
    se.set_ephe_path('./ephe_data/') 

    # 1. تبدیل تاریخ شمسی به Julian Day
    try:
        year, month, day = map(int, birth_date.split('/'))
        hour, minute = map(int, birth_time.split(':'))
        
        birth_dt_local_jdate = jdatetime.datetime(
            year, month, day, hour, minute, 0, tzinfo=ZoneInfo(timezone_str)
        )
        
        birth_dt_utc = birth_dt_local_jdate.togregorian().astimezone(ZoneInfo('UTC'))

        tjd_ut = se.julday(
            birth_dt_utc.year, 
            birth_dt_utc.month, 
            birth_dt_utc.day, 
            birth_dt_utc.hour + birth_dt_utc.minute/60.0 + birth_dt_utc.second/3600.0
        )

        logging.info(f"DEBUG: Calculated JD (UT) from Shamsi date: {tjd_ut}")
        
    except Exception as e:
        logging.error(f"FATAL ERROR: خطا در تبدیل تاریخ شمسی به JD: {e}")
        return {'error': f"خطا در تبدیل تاریخ شمسی به Julian Day: {e}"}

    # 2. محاسبه خانه‌ها (House Cusps) و Asc/MC
    try:
        logging.info(f"DEBUG: Calling se.houses with JD: {tjd_ut}, Lat: {latitude}, Lon: {longitude}, System: {house_system}")
        
        # رفع خطای "argument 4 must be a byte string of length 1, not str"
        house_system_bytes = house_system.upper().encode('utf-8')
        
        # 💡 اصلاح حیاتی: دریافت نتیجه خام و بررسی طول تاپل برای جلوگیری از خطای "tuple index out of range"
        result = se.houses(tjd_ut, latitude, longitude, house_system_bytes)
        
        if not isinstance(result, tuple) or len(result) < 2:
            # اگر swisseph.houses نتیجه نامعتبر برگرداند (دلیل اصلی خطای tuple index out of range)
            error_details = f"swisseph.houses returned unexpected result length: {len(result) if isinstance(result, tuple) else 'Not a tuple'}"
            logging.error(f"FATAL ERROR: {error_details}")
            return {'error': f"خطا در محاسبه خانه‌ها و طالع: {error_details}. لطفاً مختصات یا تاریخ را بررسی کنید."}

        # اگر طول تاپل درست بود، می‌توانیم آن را Unpack کنیم.
        cusps_raw, ascmc = result

        if len(cusps_raw) < 12:
            raise IndexError(f"خروجی cusps ناقص است. طول cusps: {len(cusps_raw)}")
        
        # استخراج ۱۲ خانه (از ایندکس ۱ تا ۱۲)
        cusps = [cusps_raw[i] for i in range(1, 13)] 
        ascendant_deg = ascmc[0]
        mc_deg = ascmc[1]
        
    except Exception as e:
        logging.error(f"FATAL ERROR: خطا در محاسبه خانه‌ها و طالع: {e}")
        # در صورت بروز هر خطای دیگری، یک دیکشنری خطا برمی‌گرداند.
        return {'error': f"خطا در محاسبه خانه‌ها و طالع (Houses/Ascendant): {e}"}

    chart_data = {'planets': [], 'cusps': cusps, 'ascendant': ascendant_deg, 'mc': mc_deg}
    planet_positions = {} 

    # 3. محاسبه موقعیت سیارات
    for planet_name, planet_id in PLANETS.items():
        try:
            # رفع خطای "module 'swisseph' has no attribute 'FLG_SWIEPHE'" با استفاده از مدیریت خطا
            swisseph_flags = 0 
            try:
                # تلاش برای استفاده از فلگ‌های کامل دقت
                swisseph_flags = se.FLG_SWIEPHE | se.FLG_TOPOCTR 
            except AttributeError:
                # در صورت خطا، از فلگ 0 استفاده کن
                logging.warning("WARNING: FLG_SWIEPHE or FLG_TOPOCTR not found. Defaulting to 0 flags (lower precision).")
                swisseph_flags = 0
            
            if planet_name == 'true_node':
                try:
                     swisseph_flags |= se.FLG_TRUE_NODE
                except AttributeError:
                     # اگر فلگ گره شمالی هم پیدا نشد، ادامه بده
                     pass 
            
            # se.calc_ut returns [lon, lat, dist, lon_speed, lat_speed, dist_speed]
            planet_pos, ret_flag = se.calc_ut(tjd_ut, planet_id, swisseph_flags)
            
            lon_deg = float(planet_pos[0])
            lat_deg = float(planet_pos[1])

            # محاسبه موقعیت خانه سیاره
            house = 0
            if ascendant_deg != 0.0 and len(cusps_raw) >= 13: 
                 # در اینجا house_system.upper() باید به صورت رشته معمولی فرستاده شود
                 planet_house_pos = se.house_pos(lon_deg, lat_deg, cusps_raw, ascmc, house_system.upper())
                 house = int(planet_house_pos[0])

            retrograde = lon_deg < 0 or planet_pos[3] < 0 
            
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
            planet_positions[planet_name] = lon_deg 
            
        except Exception as e:
            logging.error(f"FATAL ERROR: خطا در محاسبه موقعیت سیاره {planet_name}: {e}")
            planet_positions[planet_name] = 0.0

    # 4. محاسبه Part of Fortune
    part_of_fortune_data = calculate_part_of_fortune(planet_positions, ascendant_deg, cusps_raw, ascmc, house_system)
    chart_data['part_of_fortune'] = part_of_fortune_data
    
    # 5. محاسبه جنبه‌ها (Aspects)
    chart_data['aspects'] = calculate_aspects(chart_data['planets'])

    return chart_data

def calculate_part_of_fortune(planet_positions: Dict[str, float], ascendant_deg: float, cusps_raw: List[float], ascmc: List[float], house_system: str) -> Dict[str, Any]:
    # ... (بدون تغییر) ...
    if 'sun' not in planet_positions or 'moon' not in planet_positions or ascendant_deg == 0.0 or planet_positions.get('sun', 0.0) == 0.0:
        logging.error("خطا در محاسبه Part of Fortune: اطلاعات خورشید، ماه یا طالع نامعتبر است.")
        return {'degree': 0.0, 'sign': 'نامشخص', 'house': 0, 'house_name': get_house_name(0)}
    
    sun_lon = planet_positions['sun']
    moon_lon = planet_positions['moon']
    
    # محاسبه Part of Fortune
    fortune_deg = (ascendant_deg + moon_lon - sun_lon) % 360
    
    house = 0
    try:
        if len(cusps_raw) >= 13: 
            house_pos_raw = se.house_pos(fortune_deg, 0.0, cusps_raw, ascmc, house_system.upper())
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
    # ... (بدون تغییر) ...
    aspects = []
    
    aspect_planets = [p for p in planets_data if p['name'] not in ['true_node', 'lilith', 'chiron'] and p['degree'] != 0.0]
    
    for i in range(len(aspect_planets)):
        for j in range(i + 1, len(aspect_planets)):
            p1 = aspect_planets[i]
            p2 = aspect_planets[j]
            
            if p1['degree'] is None or p2['degree'] is None:
                continue

            angle = abs(p1['degree'] - p2['degree'])
            angle = min(angle, 360 - angle) 
            
            for aspect in ASPECTS:
                diff = abs(angle - aspect['degree'])
                if diff <= aspect['orb']:
                    aspects.append({
                        'p1': p1['name'],
                        'p2': p2['name'],
                        'type': aspect['name'],
                        'exact_angle': round(angle, 2),
                        'orb': round(diff, 2),
                        'significance': 1.0 - (diff / aspect['orb']) 
                    })
                    
    return aspects


# ==============================================================================
# تابع جدید: تولید چارت تصویری
# ==============================================================================

def create_chart_image(chart_data: Dict[str, Any]) -> io.BytesIO:
    """نقشه تولد را به صورت یک تصویر PNG در یک بافر حافظه برمی‌گرداند.
    توجه: این تابع یک Placeholder است و نیاز به کدنویسی گرافیکی کامل دارد."""
    
    # اطمینان از وجود داده‌ها
    if 'ascendant' not in chart_data or chart_data['ascendant'] == 0.0:
        raise ValueError("داده‌های چارت نامعتبر هستند. محاسبه ناموفق بوده است.")

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={'projection': 'polar'})

    # 1. تنظیمات اولیه چارت (دایره 360 درجه)
    ax.set_theta_zero_location("W") # تنظیم صفر درجه (شروع حمل) روی سمت راست (غرب)
    ax.set_theta_direction(-1)      # جهت عقربه‌های ساعت
    ax.set_xticks(math.radians(range(0, 360, 30))) # تقسیم بندی 30 درجه ای برای برج ها
    
    # 2. رسم دایره‌ها (Houses/Signs)
    # رسم دایره برج‌ها
    ax.add_patch(Circle((0, 0), radius=1, facecolor='none', edgecolor='black', linewidth=1))

    # 3. نمایش سیارات (Placeholder)
    # مثال: رسم موقعیت خورشید
    for planet in chart_data.get('planets', []):
        if planet['degree'] != 0.0:
            angle_rad = math.radians(planet['degree'])
            # موقعیت سیاره (شعاع 0.8 برای داخل چارت)
            ax.plot(angle_rad, 0.8, marker='o', markersize=10, linestyle='none')
            # نمایش نام سیاره (نیاز به فونت فارسی دارد)
            # ax.text(angle_rad, 0.9, planet['name'], ha='center', va='center')


    ax.set_rticks([]) # حذف خطوط شعاعی
    ax.set_xticklabels([f"{sign}" for sign in SIGNS]) # نمایش نام برج ها

    # تنظیم محدودیت شعاعی
    ax.set_rlim(0, 1)

    plt.title("نقشه تولد (چارت ناتال)", pad=20)
    plt.tight_layout()

    # ذخیره در حافظه
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png')
    plt.close(fig) # بستن شکل برای آزاد کردن حافظه
    img_buffer.seek(0)
    
    return img_buffer
