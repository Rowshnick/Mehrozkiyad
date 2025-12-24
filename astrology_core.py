# astrology_core.py - نسخه اصلاح شده با نام پوشه جدید ephe

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

# تنظیمات لاگینگ
logging.basicConfig(level=logging.INFO)
logging.info("CODE_VERSION: 2025-12-24-FolderFix-AstroCore-REVISED") 

# ۱. اصلاح مسیر اصلی به پوشه جدید ephe
base_dir = os.path.dirname(os.path.abspath(__file__))
ephe_path = os.path.join(base_dir, "ephe") # تغییر از ephe_data به ephe

# بررسی وجود یکی از فایل‌های اصلی
test_file = os.path.join(ephe_path, "semo_18.se1")

if os.path.exists(test_file):
    se.set_ephe_path(ephe_path)
    logging.info(f"✅ فایل‌های نجومی با موفقیت در پوشه جدید شناسایی شدند: {ephe_path}")
else:
    se.set_ephe_path(base_dir)
    logging.warning(f"⚠️ فایل {test_file} پیدا نشد. لطفاً مطمئن شوید پوشه ephe و فایل‌های se1. موجود هستند.")

# ==============================================================================
# ثابت‌ها (بدون تغییر)
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
# توابع کمکی (بدون تغییر)
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
    
    # ۲. اصلاح مسیر در داخل تابع اصلی برای هماهنگی با Railway
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ephe_path = os.path.join(base_dir, "ephe") # تغییر از ephe_data به ephe
    se.set_ephe_path(ephe_path) 

    try:
        year, month, day = map(int, birth_date.split('/'))
        hour, minute = map(int, birth_time.split(':'))
        birth_dt_local_jdate = jdatetime.datetime(year, month, day, hour, minute, 0, tzinfo=ZoneInfo(timezone_str))
        birth_dt_utc = birth_dt_local_jdate.togregorian().astimezone(ZoneInfo('UTC'))

        tjd_ut = se.julday(
            birth_dt_utc.year, 
            birth_dt_utc.month, 
            birth_dt_utc.day, 
            birth_dt_utc.hour + birth_dt_utc.minute/60.0
        )
    except Exception as e:
        return {'error': f"خطا در تبدیل تاریخ: {e}"}

    # مدیریت خروجی se.houses برای جلوگیری از IndexError
    try:
        house_system_bytes = house_system.upper().encode('utf-8')
        result = se.houses(tjd_ut, latitude, longitude, house_system_bytes)
        
        # ۳. اصلاح پیغام خطا برای پوشه جدید
        if not result or len(result) < 2:
            return {'error': "فایل‌های ephemeris (.se1) در پوشه ephe یافت نشدند."}

        cusps_raw, ascmc = result
        cusps = [cusps_raw[i] for i in range(1, 13)] 
        ascendant_deg = ascmc[0]
        mc_deg = ascmc[1]
    except Exception as e:
        return {'error': f"خطا در محاسبه خانه‌ها: {e}"}

    chart_data = {'planets': [], 'cusps': cusps, 'ascendant': ascendant_deg, 'mc': mc_deg}
    planet_positions = {} 

    for planet_name, planet_id in PLANETS.items():
        try:
            planet_pos, ret_flag = se.calc_ut(tjd_ut, planet_id, 0)
            lon_deg = float(planet_pos[0])
            lat_deg = float(planet_pos[1])

            house = 0
            if ascendant_deg != 0.0:
                 planet_house_pos = se.house_pos(lon_deg, lat_deg, cusps_raw, ascmc, house_system_bytes)
                 house = int(planet_house_pos[0])

            planet_data = {
                'name': planet_name, 'id': planet_id, 'degree': lon_deg,
                'sign': get_sign(lon_deg), 'sign_degree': get_sign_degree(lon_deg),
                'house': house, 'house_name': get_house_name(house),
                'retrograde': planet_pos[3] < 0, 'latitude': lat_deg
            }
            chart_data['planets'].append(planet_data)
            planet_positions[planet_name] = lon_deg 
        except:
            continue

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
    if 'ascendant' not in chart_data or chart_data['ascendant'] == 0.0:
        raise ValueError("داده‌های چارت نامعتبر هستند.")
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={'projection': 'polar'})
    ax.set_theta_zero_location("W")
    ax.set_theta_direction(-1)
    ax.set_xticklabels([f"{sign}" for sign in SIGNS])
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png')
    plt.close(fig)
    img_buffer.seek(0)
    return img_buffer
