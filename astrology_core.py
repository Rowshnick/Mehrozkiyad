# ==== astrology_core.py ====

import swisseph as se
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Dict, Any, List
import logging
import jdatetime 
import io 
import math
import os

# تنظیمات لاگینگ
logging.basicConfig(level=logging.INFO)
logging.info("CODE_VERSION: 2025-12-27-STABLE-PRODUCTION") 

# تنظیم مسیر فایل‌های نجومی
base_dir = os.path.dirname(os.path.abspath(__file__))
ephe_path = os.path.join(base_dir, "ephe")

if os.path.exists(ephe_path):
    se.set_ephe_path(ephe_path)
    logging.info(f"✅ Ephe Path Set: {ephe_path}")
else:
    logging.warning(f"⚠️ Warning: Ephe folder not found at {ephe_path}")

# ثابت‌ها
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

# توابع کمکی
def get_sign(degree: float) -> str:
    return SIGNS[int(degree / 30) % 12]

def get_sign_degree(degree: float) -> float:
    return degree % 30

def get_house_name(house_num: int) -> str:
    if 1 <= house_num <= 12:
        return HOUSES_LIST[house_num - 1]
    return "نامشخص"

# منطق اصلی محاسبه
def calculate_natal_chart(birth_date: str, birth_time: str, latitude: float, longitude: float, timezone_str: str, house_system: str = 'K') -> Dict[str, Any]:
    try:
        logging.info(f"PROCESS: Calculating chart for {birth_date} {birth_time}")
        
        # تبدیل تاریخ جلالی به میلادی و UTC
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

        # محاسبه خانه‌ها
        try:
            h_sys = house_system.upper().encode('utf-8')
            cusps_raw, ascmc = se.houses(tjd_ut, latitude, longitude, h_sys)
            h_sys_final = h_sys
        except Exception as e:
            logging.warning(f"Falling back to Whole Sign System due to: {e}")
            cusps_raw, ascmc = se.houses(tjd_ut, latitude, longitude, b'W')
            h_sys_final = b'W'

        cusps = [cusps_raw[i] for i in range(1, 13)] 
        ascendant_deg = ascmc[0]
        mc_deg = ascmc[1]

        chart_data = {'planets': [], 'cusps': cusps, 'ascendant': ascendant_deg, 'mc': mc_deg}
        planet_positions = {} 
        FLAGS = se.FLG_SWIEPH | se.FLG_SPEED

        for planet_name, planet_id in PLANETS.items():
            planet_pos, _ = se.calc_ut(tjd_ut, planet_id, FLAGS)
            lon_deg = float(planet_pos[0])
            lat_deg = float(planet_pos[1])
            speed_lon = float(planet_pos[3])

            house = 0
            if ascendant_deg != 0.0:
                try:
                    # اصلاح خروجی برای جلوگیری از خطای tuple index out of range
                    planet_house_pos = se.house_pos(lon_deg, lat_deg, latitude, h_sys_final, cusps_raw)
                    if isinstance(planet_house_pos, (list, tuple)):
                        house = int(planet_house_pos[0])
                    else:
                        house = int(planet_house_pos)
                except Exception as e:
                    logging.warning(f"Error calculating house for {planet_name}: {e}")
                    house = 0

            p_data = {
                'name': planet_name, 
                'degree': lon_deg,
                'sign': get_sign(lon_deg), 
                'sign_degree': get_sign_degree(lon_deg),
                'house': house, 
                'house_name': get_house_name(house),
                'retrograde': speed_lon < 0,
                'latitude': lat_deg
            }
            chart_data['planets'].append(p_data)
            planet_positions[planet_name] = lon_deg 

        # اصلاح فراخوانی: اضافه شدن متغیر latitude
        chart_data['part_of_fortune'] = calculate_part_of_fortune(planet_positions, ascendant_deg, cusps_raw, ascmc, h_sys_final, latitude)
        chart_data['aspects'] = calculate_aspects(chart_data['planets'])

        return chart_data

    except Exception as e:
        logging.error(f"Critical error in calculate_natal_chart: {e}")
        return None

def calculate_part_of_fortune(planet_positions, ascendant_deg, cusps_raw, ascmc, h_sys_bytes, latitude):
    if 'sun' not in planet_positions or 'moon' not in planet_positions:
        return {'degree': 0.0, 'sign': 'نامشخص'}
    
    fortune_deg = (ascendant_deg + planet_positions['moon'] - planet_positions['sun']) % 360
    house = 0
    try:
        # اصلاح خروجی برای جلوگیری از خطای index out of range
        house_pos_raw = se.house_pos(fortune_deg, 0.0, latitude, h_sys_bytes, cusps_raw)
        if isinstance(house_pos_raw, (list, tuple)):
            house = int(house_pos_raw[0])
        else:
            house = int(house_pos_raw)
    except: 
        house = 0
        
    return {
        'degree': fortune_deg, 
        'sign': get_sign(fortune_deg), 
        'sign_degree': get_sign_degree(fortune_deg), 
        'house': house, 
        'house_name': get_house_name(house)
    }

def calculate_aspects(planets_data):
    aspects = []
    p_list = [p for p in planets_data if p['name'] not in ['true_node', 'lilith', 'chiron']]
    for i in range(len(p_list)):
        for j in range(i + 1, len(p_list)):
            p1, p2 = p_list[i], p_list[j]
            angle = abs(p1['degree'] - p2['degree'])
            angle = min(angle, 360 - angle) 
            for aspect in ASPECTS:
                if abs(angle - aspect['degree']) <= aspect['orb']:
                    aspects.append({
                        'p1': p1['name'], 
                        'p2': p2['name'], 
                        'type': aspect['name'], 
                        'orb': round(abs(angle - aspect['degree']), 2)
                    })
    return aspects
