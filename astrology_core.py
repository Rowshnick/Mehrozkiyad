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

# تنظیمات لاگینگ برای ردیابی دقیق در Railway
logging.basicConfig(level=logging.INFO)
logging.info("CODE_VERSION: 2025-12-24-FINAL-STABLE-EPHE") 

# ۱. تنظیم مسیر برای پوشه ephe (استفاده از مسیر مطلق برای اطمینان در محیط داکر)
base_dir = os.path.dirname(os.path.abspath(__file__))
ephe_path = os.path.join(base_dir, "ephe")

# بررسی وجود فایل‌ها قبل از شروع برای جلوگیری از خطاهای موتور نجومی
if os.path.exists(ephe_path):
    se.set_ephe_path(ephe_path)
    logging.info(f"✅ فایل‌های نجومی شناسایی شدند: {ephe_path}")
else:
    logging.warning(f"⚠️ پوشه ephe در مسیر {ephe_path} یافت نشد.")

# ==============================================================================
# ثابت‌ها (ثوابت نجومی و نام‌گذاری‌ها)
# ==============================================================================
PLANETS = {
    'sun': se.SUN, 'moon': se.MOON, 'mercury': se.MERCURY, 'venus': se.VENUS, 
    'mars': se.MARS, 'jupiter': se.JUPITER, 'saturn': se.SATURN, 'uranus': se.URANUS,
    'neptune': se.NEPTUNE, 'pluto': se.PLUTO, 'true_node': se.TRUE_NODE, 
    'chiron': se.CHIRON, 'lilith': 12
}

SIGNS = ["حمل", "ثور", "جوزا", "سرطان", "اسد", "سنبله", "میزان", "عقرب", "قوس", "جدی", "دلو", "حوت"]
HOUSES_LIST = [f"خانه {i}" for i in range(1, 13)]

ASPECTS = [
    {'name': 'تثلیث', 'degree': 120, 'orb': 6},
    {'name': 'تراضی', 'degree': 60, 'orb': 4},
    {'name': 'اقتران', 'degree': 0, 'orb': 8},
    {'name': 'تربیع', 'degree': 90, 'orb': 6},
    {'name': 'تقابل', 'degree': 180, 'orb': 6}
]

# ==============================================================================
# توابع کمکی (برج‌ها و خانه‌ها)
# ==============================================================================
def get_sign(degree: float) -> str:
    """تشخیص نام برج بر اساس درجه زودیاک"""
    return SIGNS[int(degree / 30) % 12]

def get_sign_degree(degree: float) -> float:
    """محاسبه درجه دقیق در هر برج (۰ تا ۳۰)"""
    return degree % 30

def get_house_name(house_num: int) -> str:
    """تبدیل عدد خانه به نام فارسی"""
    if 1 <= house_num <= 12:
        return HOUSES_LIST[house_num - 1]
    return "نامشخص"

# ==============================================================================
# منطق اصلی محاسبه چارت (تابع محوری)
# ==============================================================================
def calculate_natal_chart(birth_date: str, birth_time: str, latitude: float, longitude: float, timezone_str: str, house_system: str = 'K') -> Dict[str, Any]:
    """
    محاسبه کامل چارت ناتال شامل موقعیت سیارات، خانه‌ها و جنبه‌ها.
    دارای سیستم Fallback برای جلوگیری از کرش در عرض‌های جغرافیایی خاص.
    """
    try:
        # ۱. تبدیل تاریخ شمسی و ساعت محلی به زمان جولیانی UTC
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
        logging.error(f"خطای بحرانی در پارس تاریخ/زمان: {e}")
        return {'error': f"فرمت تاریخ یا ساعت اشتباه است: {e}"}

    # ۲. محاسبه خانه‌ها (بخش حساس به خطا - دارای لایه‌های محافظتی)
    try:
        # تلاش اول: با سیستم درخواستی کاربر (معمولاً Koch)
        h_sys = house_system.upper().encode('utf-8')
        result = se.houses(tjd_ut, latitude, longitude, h_sys)
        cusps_raw, ascmc = result
        house_system_bytes = h_sys
    except Exception as e:
        logging.warning(f"⚠️ سیستم {house_system} شکست خورد. تلاش با Whole Sign... خطا: {e}")
        # تلاش نهایی: سیستم Whole Sign (بسیار پایدار در تمام نقاط زمین)
        result = se.houses(tjd_ut, latitude, longitude, b'W')
        cusps_raw, ascmc = result
        house_system_bytes = b'W'

    # استخراج کپس‌ها و نقاط اصلی
    cusps = [cusps_raw[i] for i in range(1, 13)] 
    ascendant_deg = ascmc[0]
    mc_deg = ascmc[1]

    chart_data = {'planets': [], 'cusps': cusps, 'ascendant': ascendant_deg, 'mc': mc_deg}
    planet_positions = {} 

    # تنظیم فلگ‌ها: FLG_SPEED برای تشخیص حرکت برگشتی حیاتی است
    FLAGS = se.FLG_SWIEPH | se.FLG_SPEED

    # ۳. محاسبه موقعیت و جزئیات هر سیاره
    for planet_name, planet_id in PLANETS.items():
        try:
            # محاسبه طول، عرض جغرافیایی و سرعت سیاره
            planet_pos, _ = se.calc_ut(tjd_ut, planet_id, FLAGS)
            
            lon_deg = float(planet_pos[0])   # طول (درجه در زودیاک)
            lat_deg = float(planet_pos[1])   # عرض جغرافیایی (Celestial Latitude)
            speed_lon = float(planet_pos[3]) # سرعت (مثبت/منفی)

            # تعیین شماره خانه سیاره
            house = 0
            if ascendant_deg != 0.0:
                 planet_house_pos = se.house_pos(lon_deg, lat_deg, cusps_raw, ascmc, house_system_bytes)
                 house = int(planet_house_pos[0])

            p_data = {
                'name': planet_name, 
                'degree': lon_deg,
                'sign': get_sign(lon_deg), 
                'sign_degree': get_sign_degree(lon_deg),
                'house': house, 
                'house_name': get_house_name(house),
                'retrograde': speed_lon < 0,  # حرکت برگشتی اگر سرعت منفی باشد
                'latitude': lat_deg          # نمایش عرض جغرافیایی در گزارش متن
            }
            chart_data['planets'].append(p_data)
            planet_positions[planet_name] = lon_deg 
        except Exception as e:
            logging.error(f"❌ خطا در محاسبه سیاره {planet_name}: {e}")
            continue

    # ۴. محاسبات نهایی (نقطه سعادت و جنبه‌ها)
    chart_data['part_of_fortune'] = calculate_part_of_fortune(planet_positions, ascendant_deg, cusps_raw, ascmc, house_system)
    chart_data['aspects'] = calculate_aspects(chart_data['planets'])

    return chart_data

# ==============================================================================
# سایر توابع محاسباتی (نقطه سعادت و جنبه‌ها)
# ==============================================================================
def calculate_part_of_fortune(planet_positions, ascendant_deg, cusps_raw, ascmc, house_system):
    """محاسبه نقطه سعادت (Part of Fortune)"""
    if 'sun' not in planet_positions or 'moon' not in planet_positions:
        return {'degree': 0.0, 'sign': 'نامشخص'}
    
    # فرمول کلاسیک: ASC + Moon - Sun
    fortune_deg = (ascendant_deg + planet_positions['moon'] - planet_positions['sun']) % 360
    house = 0
    try:
        house_pos_raw = se.house_pos(fortune_deg, 0.0, cusps_raw, ascmc, house_system.upper().encode('utf-8'))
        house = int(house_pos_raw[0])
    except: pass
    return {
        'degree': fortune_deg, 
        'sign': get_sign(fortune_deg), 
        'sign_degree': get_sign_degree(fortune_deg), 
        'house': house, 
        'house_name': get_house_name(house)
    }

def calculate_aspects(planets_data):
    """تحلیل زوایای بین سیارات (Aspects)"""
    aspects = []
    # فیلتر کردن سیارات اصلی برای جلوگیری از شلوغی گزارش
    p_list = [p for p in planets_data if p['name'] not in ['true_node', 'lilith', 'chiron']]
    
    for i in range(len(p_list)):
        for j in range(i + 1, len(p_list)):
            p1, p2 = p_list[i], p_list[j]
            angle = abs(p1['degree'] - p2['degree'])
            angle = min(angle, 360 - angle) # کوتاه‌ترین فاصله روی دایره
            
            for aspect in ASPECTS:
                diff = abs(angle - aspect['degree'])
                if diff <= aspect['orb']:
                    aspects.append({
                        'p1': p1['name'], 
                        'p2': p2['name'], 
                        'type': aspect['name'], 
                        'orb': round(diff, 2)
                    })
    return aspects
