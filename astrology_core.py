# astrology_core.py
# =============================================================================
# هسته‌ی محاسبات نجومی ربات (Swiss Ephemeris + تاریخ شمسی)
# -----------------------------------------------------------------------------
# نکات معماری:
# 1. ورودی تاریخ به‌صورت شمسی (رشته‌ی YYYY/MM/DD) و زمان به‌صورت HH:MM است.
# 2. تاریخ شمسی به کمک jdatetime به میلادی + UTC تبدیل می‌شود، سپس Julian Day
#    برای Swiss Ephemeris محاسبه می‌گردد.
# 3. خروجی ساختاریافته در دیکشنری chart_data برگردانده می‌شود که برای:
#    - ماژول تفسیر (interpret_natal_chart)
#    - ماژول ترسیم چارت (chart_drawer_fa)
#    - و سایر بخش‌ها قابل استفاده است.
# 4. توضیحات و لاگ‌ها کاملاً فارسی هستند برای سهولت نگهداری.
# نسخهٔ نهایی و بهینه‌شده – شامل Whole Sign / Placidus / Koch
# =============================================================================

import os
import logging
from typing import Dict, Any, List, Tuple

import swisseph as se
from zoneinfo import ZoneInfo
import jdatetime

logging.basicConfig(level=logging.INFO)
logging.info("CODE_VERSION: 2025-12-24-FINAL-STABLE-EPHE")

# -----------------------------------------------------------------------------
# مسیر فایل‌های اپمریس
# -----------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EPHE_PATH = os.path.join(BASE_DIR, "ephe")

if os.path.exists(EPHE_PATH):
    se.set_ephe_path(EPHE_PATH)
    logging.info(f"✅ فایل‌های نجومی Swiss Ephemeris شناسایی شدند: {EPHE_PATH}")
else:
    logging.warning(f"⚠️ پوشه ephe یافت نشد. محاسبات ممکن است ناقص باشند.")

# -----------------------------------------------------------------------------
# ثابت‌ها
# -----------------------------------------------------------------------------
PLANETS = {
    'sun': se.SUN,
    'moon': se.MOON,
    'mercury': se.MERCURY,
    'venus': se.VENUS,
    'mars': se.MARS,
    'jupiter': se.JUPITER,
    'saturn': se.SATURN,
    'uranus': se.URANUS,
    'neptune': se.NEPTUNE,
    'pluto': se.PLUTO,
    'true_node': se.TRUE_NODE,
    'chiron': se.CHIRON,
    'lilith': 12,
}

SIGNS_FA = [
    "حمل", "ثور", "جوزا", "سرطان", "اسد", "سنبله",
    "میزان", "عقرب", "قوس", "جدی", "دلو", "حوت"
]

HOUSES_LIST_FA = [f"خانه {i}" for i in range(1, 13)]

ASPECT_DEFS = [
    {'name_en': 'Conjunction', 'degree': 0,   'orb': 8},
    {'name_en': 'Sextile',     'degree': 60,  'orb': 4},
    {'name_en': 'Square',      'degree': 90,  'orb': 6},
    {'name_en': 'Trine',       'degree': 120, 'orb': 6},
    {'name_en': 'Opposition',  'degree': 180, 'orb': 6},
]

FLAGS = se.FLG_SWIEPH | se.FLG_SPEED

# =============================================================================
# توابع کمکی
# =============================================================================

def get_sign_fa(degree: float) -> str:
    return SIGNS_FA[int(degree // 30) % 12]

def get_degree_in_sign(degree: float) -> float:
    return degree % 30.0

def get_house_name_fa(house_num: int) -> str:
    if 1 <= house_num <= 12:
        return HOUSES_LIST_FA[house_num - 1]
    return "خانه نامشخص"

# -----------------------------------------------------------------------------
# محاسبه خانه‌ها
# -----------------------------------------------------------------------------

def _calc_houses(tjd_ut: float, latitude: float, longitude: float,
                 house_system: str = 'K') -> Tuple[List[float], List[float], str]:
    """
    محاسبه خانه‌ها با سیستم انتخابی.
    در صورت خطا → Whole Sign
    """
    try:
        h_sys = house_system.upper().encode('utf-8')
        cusps_raw, ascmc = se.houses(tjd_ut, latitude, longitude, h_sys)
        return list(cusps_raw), list(ascmc), house_system.upper()
    except Exception as e:
        logging.warning(f"⚠️ خطا در سیستم {house_system}: {e} → استفاده از Whole Sign")
        cusps_raw, ascmc = se.houses(tjd_ut, latitude, longitude, b'W')
        return list(cusps_raw), list(ascmc), 'W'

# -----------------------------------------------------------------------------
# تعیین خانهٔ سیاره (نسخهٔ بهینه و استاندارد)
# -----------------------------------------------------------------------------

def determine_house(lon_deg: float, cusps: List[float]) -> int:
    """
    تعیین خانهٔ سیاره بر اساس cuspها.
    سازگار با Placidus / Koch / Whole Sign
    """
    for i in range(1, 13):
        cusp_start = cusps[i]
        cusp_end = cusps[1] if i == 12 else cusps[i + 1]

        # عبور از 360 درجه
        if cusp_end < cusp_start:
            cusp_end += 360

        lon_adj = lon_deg
        if lon_adj < cusp_start:
            lon_adj += 360

        if cusp_start <= lon_adj < cusp_end:
            return i

    return 0

# =============================================================================
# محاسبه چارت ناتال
# =============================================================================

def calculate_natal_chart(
    birth_date_jalali: str,
    birth_time_str: str,
    latitude: float,
    longitude: float,
    timezone_str: str,
    house_system: str = 'K'
) -> Dict[str, Any]:

    # 1) تبدیل تاریخ شمسی → میلادی → UTC → Julian Day
    try:
        y, m, d = map(int, birth_date_jalali.split('/'))
        hh, mm = map(int, birth_time_str.split(':'))

        birth_dt_local = jdatetime.datetime(
            y, m, d, hh, mm, tzinfo=ZoneInfo(timezone_str)
        )
        birth_dt_utc = birth_dt_local.togregorian().astimezone(ZoneInfo('UTC'))

        tjd_ut = se.julday(
            birth_dt_utc.year,
            birth_dt_utc.month,
            birth_dt_utc.day,
            birth_dt_utc.hour + birth_dt_utc.minute / 60
        )
    except Exception as e:
        return {'error': f"خطا در تبدیل تاریخ/زمان: {e}"}

    # 2) محاسبه خانه‌ها
    cusps_raw, ascmc, house_sys = _calc_houses(
        tjd_ut, latitude, longitude, house_system
    )

    asc_deg = float(ascmc[0])
    mc_deg = float(ascmc[1])

    houses_struct = {
        'cusps': cusps_raw,
        'asc': asc_deg,
        'mc': mc_deg,
        'system': house_sys
    }

    # 3) محاسبه سیارات
    planets_dict = {}
    planets_list = []
    planet_longitudes = {}

    for name, pid in PLANETS.items():
        try:
            pos, _ = se.calc_ut(tjd_ut, pid, FLAGS)
            lon = float(pos[0])
            lat = float(pos[1])
            speed = float(pos[3])

            house_num = determine_house(lon, cusps_raw)

            pdata = {
                'name': name,
                'degree': lon,
                'sign': get_sign_fa(lon),
                'sign_degree': get_degree_in_sign(lon),
                'house': house_num,
                'house_name': get_house_name_fa(house_num),
                'retrograde': (speed < 0),
                'latitude': lat,
            }

            planets_dict[name] = pdata
            planets_list.append(pdata)
            planet_longitudes[name] = lon

        except Exception as e:
            logging.error(f"❌ خطا در محاسبه {name}: {e}")

    # 4) سهم سعادت
    pof = calculate_part_of_fortune(planet_longitudes, asc_deg, cusps_raw, ascmc, house_sys)

    # 5) زوایا
    aspects = calculate_aspects(planets_list)

    # 6) خروجی نهایی
    return {
        'planets': planets_dict,
        'planets_list': planets_list,
        'houses': houses_struct,
        'ascendant': asc_deg,
        'mc': mc_deg,
        'cusps': cusps_raw,
        'part_of_fortune': pof,
        'aspects': aspects,
    }

# -----------------------------------------------------------------------------
# سهم سعادت
# -----------------------------------------------------------------------------

def calculate_part_of_fortune(planet_longitudes, asc_deg, cusps_raw, ascmc, house_sys):
    if 'sun' not in planet_longitudes or 'moon' not in planet_longitudes:
        return {'degree': 0, 'sign': 'نامشخص', 'sign_degree': 0, 'house': 0}

    pof = (asc_deg + planet_longitudes['moon'] - planet_longitudes['sun']) % 360
    house_num = determine_house(pof, cusps_raw)

    return {
        'degree': pof,
        'sign': get_sign_fa(pof),
        'sign_degree': get_degree_in_sign(pof),
        'house': house_num,
        'house_name': get_house_name_fa(house_num),
    }

# -----------------------------------------------------------------------------
# زوایا
# -----------------------------------------------------------------------------

def calculate_aspects(planets_list):
    aspects = []
    filtered = [p for p in planets_list if p['name'] not in ['true_node', 'lilith', 'chiron']]

    for i in range(len(filtered)):
        for j in range(i + 1, len(filtered)):
            p1, p2 = filtered[i], filtered[j]
            lon1, lon2 = p1['degree'], p2['degree']

            angle = abs(lon1 - lon2)
            angle = min(angle, 360 - angle)

            for asp in ASPECT_DEFS:
                if abs(angle - asp['degree']) <= asp['orb']:
                    aspects.append({
                        'p1': p1['name'],
                        'p2': p2['name'],
                        'aspect': asp['name_en'],
                        'orb': round(abs(angle - asp['degree']), 2),
                    })

    return aspects

# =============================================================================
# موتور ترانزیت Swiss Ephemeris – نسخهٔ کامل و عملیاتی
# =============================================================================

from datetime import date, timedelta

# -----------------------------------------------------------------------------
# ابزار کمکی: اختلاف زاویه
# -----------------------------------------------------------------------------

def _angle_diff(a: float, b: float) -> float:
    """اختلاف دو درجه را در بازهٔ 0 تا 180 برمی‌گرداند."""
    diff = abs(a - b) % 360
    return diff if diff <= 180 else 360 - diff


# -----------------------------------------------------------------------------
# تعریف زوایا و اورب‌ها
# -----------------------------------------------------------------------------

TRANSIT_ASPECTS = {
    "conjunction": 0,
    "sextile": 60,
    "square": 90,
    "trine": 120,
    "opposition": 180,
}

TRANSIT_ORBS = {
    "conjunction": 6,
    "sextile": 4,
    "square": 5,
    "trine": 5,
    "opposition": 6,
}


# -----------------------------------------------------------------------------
# تشخیص نوع زاویه
# -----------------------------------------------------------------------------

def _detect_transit_aspect(transit_deg: float, natal_deg: float):
    diff = _angle_diff(transit_deg, natal_deg)

    for asp, exact in TRANSIT_ASPECTS.items():
        if abs(diff - exact) <= TRANSIT_ORBS[asp]:
            return asp, abs(diff - exact)

    return None, None


# -----------------------------------------------------------------------------
# محاسبه موقعیت سیارات ترانزیت در یک تاریخ
# -----------------------------------------------------------------------------

def calculate_transit_positions_for_date(d: date) -> Dict[str, float]:
    """
    خروجی:
    {
        "sun": 123.4,
        "moon": 250.1,
        "venus": 87.2,
        ...
    }
    """

    # تبدیل تاریخ میلادی → Julian Day
    tjd_ut = se.julday(d.year, d.month, d.day, 0.0)

    positions = {}

    for name, pid in PLANETS.items():
        try:
            pos, _ = se.calc_ut(tjd_ut, pid, FLAGS)
            positions[name] = float(pos[0])
        except Exception as e:
            logging.error(f"❌ خطا در محاسبه ترانزیت {name}: {e}")

    return positions


# -----------------------------------------------------------------------------
# تابع اصلی: محاسبه ترانزیت‌ها در یک بازهٔ زمانی
# -----------------------------------------------------------------------------

def calculate_transits_for_range(
    natal_chart: Dict[str, Any],
    start_date: date,
    end_date: date,
) -> List[Dict[str, Any]]:
    """
    خروجی:
    [
        {
            "date": date,
            "transit_planet": "saturn",
            "natal_point": "moon",
            "aspect": "square",
            "orb": 1.2,
        },
        ...
    ]
    """

    # -----------------------------
    # ۱) استخراج نقاط ناتال
    # -----------------------------
    natal_positions = {}

    for p in natal_chart.get("planets_list", []):
        natal_positions[p["name"].lower()] = p["degree"]

    # ASC و MC
    if "ascendant" in natal_chart:
        natal_positions["asc"] = natal_chart["ascendant"]

    if "mc" in natal_chart:
        natal_positions["mc"] = natal_chart["mc"]

    # -----------------------------
    # ۲) سیارات ترانزیت
    # -----------------------------
    transit_planets = [
        "sun", "moon", "mercury", "venus", "mars",
        "jupiter", "saturn", "uranus", "neptune", "pluto"
    ]

    natal_points = [
        "sun", "moon", "venus", "mars",
        "asc", "mc"
    ]

    # -----------------------------
    # ۳) حلقهٔ روزانه
    # -----------------------------
    results = []
    d = start_date

    while d <= end_date:

        transit_positions = calculate_transit_positions_for_date(d)

        for tplanet in transit_planets:
            if tplanet not in transit_positions:
                continue

            t_deg = transit_positions[tplanet]

            for npoint in natal_points:
                if npoint not in natal_positions:
                    continue

                n_deg = natal_positions[npoint]

                aspect, orb = _detect_transit_aspect(t_deg, n_deg)
                if aspect is None:
                    continue

                results.append({
                    "date": d,
                    "transit_planet": tplanet,
                    "natal_point": npoint,
                    "aspect": aspect,
                    "orb": orb,
                })

        d += timedelta(days=1)

    return results
