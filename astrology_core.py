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
import os

# استفاده از مسیر مطلق برای اطمینان در محیط داکر (Railway)
ephe_path = "/usr/src/app/ephe" 
se.set_ephe_path(ephe_path)

# تنظیمات لاگینگ برای ردیابی دقیق در Railway
logging.basicConfig(level=logging.INFO)
logging.info("CODE_VERSION: 2025-12-24-FINAL-STABLE-EPHE") 

# ۱. تنظیم مسیر برای پوشه ephe
base_dir = os.path.dirname(os.path.abspath(__file__))
ephe_path = os.path.join(base_dir, "ephe")

# بررسی وجود فایل‌ها قبل از شروع
test_file = os.path.join(ephe_path, "semo_18.se1")
if os.path.exists(test_file):
    se.set_ephe_path(ephe_path)
    logging.info(f"✅ فایل‌های نجومی شناسایی شدند: {ephe_path}")
else:
    se.set_ephe_path(base_dir)
    logging.warning(f"⚠️ فایل {test_file} پیدا نشد.")

# ==============================================================================
# ثابت‌ها
# ==============================================================================
PLANETS = {
    'sun': se.SUN, 'moon': se.MOON, 'mercury': se.MERCURY, 'venus': se.VENUS, 
    'mars': se.MARS, 'jupiter': se.JUPITER, 'saturn': se.SATURN, 'uranus': se.URANUS,
    'neptune': se.NEPTUNE, 'pluto': se.PLUTO, 'true_node': se.TRUE_NODE, 
    'chiron': se.CHIRON, 'lilith': 12
}

SIGNS = ["حمل", "ثور", "جوزا", "سرطان", "اسد", "سنبله", "میزان", "عقرب", "قوس", "جدی", "دلو", "حوت"]
HOUSES = [f"خانه {i}" for i in range(1, 13)]

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
    sign_index = int(degree / 30) % 12
    return SIGNS[sign_index]

def get_sign_degree(degree: float) -> float:
    return degree % 30

def get_house_name(house_num: int) -> str:
    if 1 <= house_num <= 12:
        return HOUSES[house_num - 1]
    return f"خانه 0" 

# ==============================================================================
# منطق اصلی محاسبه چارت
# ==============================================================================
def calculate_natal_chart(birth_date: str, birth_time: str, latitude: float, longitude: float, timezone_str: str, house_system: str = 'K') -> Dict[str, Any]:
    # تنظیم مجدد مسیر در هر فراخوانی برای اطمینان
    current_dir = os.path.dirname(os.path.abspath(__file__))
    target_ephe = os.path.join(current_dir, "ephe")
    se.set_ephe_path(target_ephe) 

    try:
        year, month, day = map(int, birth_date.split('/'))
        hour, minute = map(int, birth_time.split(':'))
        birth_dt_local = jdatetime.datetime(year, month, day, hour, minute, 0, tzinfo=ZoneInfo(timezone_str))
        birth_dt_utc = birth_dt_local.togregorian().astimezone(ZoneInfo('UTC'))

        tjd_ut = se.julday(
            birth_dt_utc.year, 
            birth_dt_utc.month, 
            birth_dt_utc.day, 
            birth_dt_utc.hour + birth_dt_utc.minute/60.0
        )
    except Exception as e:
        return {'error': f"خطا در تبدیل تاریخ: {e}"}

    # --- اصلاح بخش خانه‌ها با رعایت دندانه و تعریف متغیرها ---
    try:
        # تبدیل کد سیستم خانه به بایت (مثلاً 'K' یا 'P')
        h_sys = house_system.upper().encode('utf-8')
        result = se.houses(tjd_ut, latitude, longitude, h_sys)
        
        # بررسی پایداری خروجی
        if not isinstance(result, tuple) or len(result) < 2:
            logging.warning("سیستم خانه‌بندی انتخابی با شکست مواجه شد. سوئیچ به سیستم Placidus...")
            result = se.houses(tjd_ut, latitude, longitude, b'P') # سیستم جایگزین پلاسیدوس
            
        cusps_raw, ascmc = result
        cusps = [cusps_raw[i] for i in range(1, 13)] 
        ascendant_deg = ascmc[0]
        mc_deg = ascmc[1]
        
        # تعریف متغیر نهایی برای استفاده در محاسبات بعدی
        house_system_bytes = h_sys if len(result) >= 2 else b'P'
        
    except Exception as e:
        logging.error(f"Fatal House calculation failed: {str(e)}")
        return {'error': "عدم امکان محاسبه خانه‌ها برای این موقعیت جغرافیایی."}

    
    # ادامه محاسبات داخل بدنه تابع
    chart_data = {'planets': [], 'cusps': cusps, 'ascendant': ascendant_deg, 'mc': mc_deg}
    planet_positions = {} 

    for planet_name, planet_id in PLANETS.items():
    try:
        # استفاده از فلگ‌های دقیق
        FLAGS = se.FLG_SWIEPH | se.FLG_SPEED
        planet_pos, ret_flag = se.calc_ut(tjd_ut, planet_id, FLAGS)
        
        lon_deg = float(planet_pos[0])
        lat_deg = float(planet_pos[1]) # عرض جغرافیایی اکنون دقیق محاسبه می‌شود

        # تشخیص حرکت برگشتی (Retrograde) بر اساس سرعت
        is_retrograde = planet_pos[3] < 0

        # ... بقیه محاسبات خانه ...
        
        planet_data = {
            'name': planet_name,
            'degree': lon_deg,
            'sign': get_sign(lon_deg),
            'latitude': lat_deg, # مقدار اصلاح شده
            'retrograde': is_retrograde
        }
        chart_data['planets'].append(planet_data)
    except Exception as e:
        logging.error(f"Error calculating {planet_name}: {e}")
        continue

    # محاسبات نهایی
    chart_data['part_of_fortune'] = calculate_part_of_fortune(planet_positions, ascendant_deg, cusps_raw, ascmc, house_system)
    chart_data['aspects'] = calculate_aspects(chart_data['planets'])

    return chart_data

def calculate_part_of_fortune(planet_positions, ascendant_deg, cusps_raw, ascmc, house_system):
    if 'sun' not in planet_positions or 'moon' not in planet_positions or ascendant_deg == 0.0:
        return {'degree': 0.0, 'sign': 'نامشخص', 'house': 0}
    fortune_deg = (ascendant_deg + planet_positions['moon'] - planet_positions['sun']) % 360
    house = 0
    try:
        house_pos_raw = se.house_pos(fortune_deg, 0.0, cusps_raw, ascmc, house_system.upper().encode('utf-8'))
        house = int(house_pos_raw[0])
    except: pass
    return {'name': 'part_of_fortune', 'degree': fortune_deg, 'sign': get_sign(fortune_deg), 'sign_degree': get_sign_degree(fortune_deg), 'house': house, 'house_name': get_house_name(house)}

def calculate_aspects(planets_data):
    aspects = []
    aspect_planets = [p for p in planets_data if p['name'] not in ['true_node', 'lilith', 'chiron'] and p['degree'] != 0.0]
    for i in range(len(aspect_planets)):
        for j in range(i + 1, len(aspect_planets)):
            p1, p2 = aspect_planets[i], aspect_planets[j]
            angle = abs(p1['degree'] - p2['degree'])
            angle = min(angle, 360 - angle) 
            for aspect in ASPECTS:
                diff = abs(angle - aspect['degree'])
                if diff <= aspect['orb']:
                    aspects.append({'p1': p1['name'], 'p2': p2['name'], 'type': aspect['name'], 'exact_angle': round(angle, 2), 'orb': round(diff, 2)})
    return aspects

def create_chart_image(chart_data):
    # این تابع برای استفاده در رسم گرافیک حفظ شده است
    if 'ascendant' not in chart_data or chart_data['ascendant'] == 0.0:
        raise ValueError("داده‌های چارت نامعتبر هستند.")
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={'projection': 'polar'})
    ax.set_theta_zero_location("W")
    ax.set_theta_direction(-1)
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png')
    plt.close(fig)
    img_buffer.seek(0)
    return img_buffer
