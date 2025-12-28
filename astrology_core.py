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
# =============================================================================

import os
import logging
from typing import Dict, Any, List, Tuple

import swisseph as se
from zoneinfo import ZoneInfo
import jdatetime  # برای تبدیل تاریخ شمسی به میلادی

# -----------------------------------------------------------------------------
# تنظیمات لاگینگ
# -----------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logging.info("CODE_VERSION: 2025-12-24-FINAL-STABLE-EPHE")

# -----------------------------------------------------------------------------
# تنظیم مسیر فایل‌های اپمریس (ephe) به‌صورت مطلق
# -----------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EPHE_PATH = os.path.join(BASE_DIR, "ephe")

if os.path.exists(EPHE_PATH):
    se.set_ephe_path(EPHE_PATH)
    logging.info(f"✅ فایل‌های نجومی Swiss Ephemeris شناسایی شدند: {EPHE_PATH}")
else:
    logging.warning(f"⚠️ پوشه ephe در مسیر {EPHE_PATH} یافت نشد. "
                    f"اگر فایل‌های اپمریس موجود نباشند، محاسبات ممکن است با خطا مواجه شوند.")

# =============================================================================
# ثابت‌ها
# =============================================================================

# لیست سیارات و نقاط مورد استفاده در چارت
PLANETS: Dict[str, int] = {
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
    'true_node': se.TRUE_NODE,  # گره شمالی حقیقی
    'chiron': se.CHIRON,
    'lilith': 12,               # لیلیت (نقطه فرضی)
}

# نام برج‌ها به زبان فارسی (بر اساس 30 درجه برای هر برج)
SIGNS_FA: List[str] = [
    "حمل", "ثور", "جوزا", "سرطان", "اسد", "سنبله",
    "میزان", "عقرب", "قوس", "جدی", "دلو", "حوت"
]

# نام خانه‌ها به فارسی (برای برچسب‌گذاری)
HOUSES_LIST_FA: List[str] = [f"خانه {i}" for i in range(1, 13)]

# تعریف زوایا (Aspects) به‌صورت استاندارد انگلیسی
# توضیح: این نام‌ها با ماژول‌های تفسیر و ترسیم چارت هماهنگ هستند.
ASPECT_DEFS: List[Dict[str, Any]] = [
    {'name_en': 'Conjunction', 'degree': 0,   'orb': 8},
    {'name_en': 'Sextile',     'degree': 60,  'orb': 4},
    {'name_en': 'Square',      'degree': 90,  'orb': 6},
    {'name_en': 'Trine',       'degree': 120, 'orb': 6},
    {'name_en': 'Opposition',  'degree': 180, 'orb': 6},
]

# فلگ‌های محاسبه Swiss Ephemeris
FLAGS = se.FLG_SWIEPH | se.FLG_SPEED


# =============================================================================
# توابع کمکی
# =============================================================================

def get_sign_fa(degree: float) -> str:
    """
    تبدیل درجه طول دایره‌البروج (0 تا 360) به نام برج فارسی.
    هر 30 درجه یک برج.
    """
    index = int(degree // 30) % 12
    return SIGNS_FA[index]


def get_degree_in_sign(degree: float) -> float:
    """
    درجه‌ی داخل برج را برمی‌گرداند (0 تا کمتر از 30).
    مثال: اگر degree = 35 باشد، خروجی 5.0 است (5 درجه ثور).
    """
    return degree % 30.0


def get_house_name_fa(house_num: int) -> str:
    """
    نام فارسی خانه را بر اساس شماره (1 تا 12) برمی‌گرداند.
    """
    if 1 <= house_num <= 12:
        return HOUSES_LIST_FA[house_num - 1]
    return "خانه نامشخص"


def _calc_houses(tjd_ut: float, latitude: float, longitude: float,
                 house_system: str = 'K') -> Tuple[List[float], List[float], bytes]:
    """
    محاسبه‌ی خانه‌ها با سیستم انتخابی. در صورت بروز خطا، روی Whole Sign (W) فالبک می‌کند.
    خروجی:
      - cusps_raw: آرایه 13 تایی (0 بلااستفاده، 1 تا 12 = لبه خانه‌ها)
      - ascmc: آرایه 10 تایی که [0]=Asc و [1]=MC است
      - house_system_bytes: سیستم خانه‌ها به‌صورت بایت
    """
    try:
        h_sys = house_system.upper().encode('utf-8')
        cusps_raw, ascmc = se.houses(tjd_ut, latitude, longitude, h_sys)
        house_system_bytes = h_sys
    except Exception as e:
        logging.warning(
            f"⚠️ خطا در محاسبه‌ی خانه‌ها با سیستم {house_system} ({e}). "
            f"استفاده از سیستم Whole Sign (W) به‌عنوان فالبک."
        )
        cusps_raw, ascmc = se.houses(tjd_ut, latitude, longitude, b'W')
        house_system_bytes = b'W'

    return cusps_raw, ascmc, house_system_bytes


# =============================================================================
# توابع اصلی محاسباتی
# =============================================================================

def calculate_natal_chart(
    birth_date_jalali: str,
    birth_time_str: str,
    latitude: float,
    longitude: float,
    timezone_str: str,
    house_system: str = 'K'
) -> Dict[str, Any]:
    """
    محاسبه چارت تولد (ناتال) بر اساس:
      - تاریخ شمسی (رشته: YYYY/MM/DD)
      - زمان (رشته: HH:MM)
      - مختصات جغرافیایی (عرض و طول)
      - نام منطقه زمانی (مثلاً: Asia/Tehran)
      - سیستم خانه‌ها (مثل K = Koch, P = Placidus, W = Whole Sign و ...)

    خروجی: دیکشنری chart_data شامل:
      - planets_dict: دیکشنری سیارات با کلید نام سیاره (برای تفسیر)
      - planets_list: لیست سیارات (برای ترسیم چارت)
      - houses: اطلاعات خانه‌ها (لبه‌ها، Asc، MC، سیستم)
      - ascendant, mc
      - part_of_fortune
      - aspects
    در صورت خطای تبدیل تاریخ، {'error': "..."} برگردانده می‌شود.
    """

    # -------------------------------------------------------------------------
    # 1. تبدیل تاریخ شمسی به میلادی و سپس UTC و Julian Day
    # -------------------------------------------------------------------------
    try:
        year, month, day = map(int, birth_date_jalali.split('/'))
        hour, minute = map(int, birth_time_str.split(':'))

        # استفاده از jdatetime برای ساخت datetime شمسی با منطقه زمانی کاربر
        birth_dt_local_j = jdatetime.datetime(
            year, month, day, hour, minute, 0,
            tzinfo=ZoneInfo(timezone_str)
        )

        # تبدیل به میلادی (Gregorian) و سپس UTC
        birth_dt_utc = birth_dt_local_j.togregorian().astimezone(ZoneInfo('UTC'))

        # محاسبه Julian Day در زمان جهانی (UT)
        tjd_ut = se.julday(
            birth_dt_utc.year,
            birth_dt_utc.month,
            birth_dt_utc.day,
            birth_dt_utc.hour + birth_dt_utc.minute / 60.0
        )
    except Exception as e:
        logging.error(f"❌ خطا در تبدیل تاریخ/زمان شمسی به میلادی و Julian Day: {e}")
        return {'error': f"خطا در تبدیل تاریخ یا زمان: {e}"}

    # -------------------------------------------------------------------------
    # 2. محاسبه خانه‌ها و نقاط اصلی (Asc, MC)
    # -------------------------------------------------------------------------
    cusps_raw, ascmc, house_system_bytes = _calc_houses(
        tjd_ut, latitude, longitude, house_system
    )

    # cusps_raw آرایه‌ای با 13 مقدار است (اندیس 0 بلااستفاده)
    cusps: List[float] = [cusps_raw[i] for i in range(1, 13)]

    ascendant_deg: float = float(ascmc[0])
    mc_deg: float = float(ascmc[1])

    # ساخت ساختار خانه‌ها برای استفاده در تفسیر و نمایش
    houses_struct: Dict[str, Any] = {
        'cusps': cusps,
        'asc': ascendant_deg,
        'mc': mc_deg,
        'system': house_system_bytes.decode(errors='ignore')
    }

    # -------------------------------------------------------------------------
    # 3. محاسبه موقعیت سیارات
    # -------------------------------------------------------------------------
    planets_dict: Dict[str, Dict[str, Any]] = {}
    planets_list: List[Dict[str, Any]] = []  # برای سازگاری با ماژول‌های قدیمی
    planet_longitudes: Dict[str, float] = {}

    for planet_name, planet_id in PLANETS.items():
        try:
            planet_pos, _ = se.calc_ut(tjd_ut, planet_id, FLAGS)
            lon_deg = float(planet_pos[0])   # طول دایره‌البروج
            lat_deg = float(planet_pos[1])   # عرض
            speed_lon = float(planet_pos[3]) # سرعت طول

            # تعیین خانه‌ی سیاره
            house_num = 0
            try:
                if ascendant_deg != 0.0:
                    house_pos = se.house_pos(
                        lon_deg, lat_deg, cusps_raw, ascmc, house_system_bytes
                    )
                    house_num = int(house_pos[0])
            except Exception as e:
                logging.warning(f"⚠️ خطا در محاسبه خانه برای {planet_name}: {e}")
                house_num = 0

            p_data: Dict[str, Any] = {
                'name': planet_name,
                'degree': lon_deg,
                'sign': get_sign_fa(lon_deg),
                'sign_degree': get_degree_in_sign(lon_deg),
                'house': house_num,
                'house_name': get_house_name_fa(house_num),
                'retrograde': (speed_lon < 0),
                'latitude': lat_deg,
            }

            planets_dict[planet_name] = p_data
            planets_list.append(p_data)
            planet_longitudes[planet_name] = lon_deg

        except Exception as e:
            logging.error(f"❌ خطا در محاسبه موقعیت سیاره {planet_name}: {e}")

    # -------------------------------------------------------------------------
    # 4. محاسبه سهم سعادت (Part of Fortune)
    # -------------------------------------------------------------------------
    part_of_fortune = calculate_part_of_fortune(
        planet_longitudes, ascendant_deg, cusps_raw, ascmc, house_system
    )

    # -------------------------------------------------------------------------
    # 5. محاسبه زوایا (Aspects) بین سیارات اصلی
    # -------------------------------------------------------------------------
    aspects = calculate_aspects(planets_list)

    # -------------------------------------------------------------------------
    # 6. ساخت خروجی نهایی chart_data
    # -------------------------------------------------------------------------
    chart_data: Dict[str, Any] = {
        # دو ساختار برای سیارات:
        # - planets: دیکشنری بر اساس نام سیاره (برای تفسیر)
        # - planets_list: لیست (برای ترسیم چارت و سازگاری قدیمی)
        'planets': planets_dict,
        'planets_list': planets_list,

        # اطلاعات خانه‌ها و نقاط اصلی
        'houses': houses_struct,
        'ascendant': ascendant_deg,
        'mc': mc_deg,

        # لبه خانه‌ها به‌صورت لیست ساده (در صورت نیاز به سازگاری)
        'cusps': cusps,

        # نقاط ویژه
        'part_of_fortune': part_of_fortune,

        # زوایا
        'aspects': aspects,
    }

    logging.info("✅ محاسبه چارت ناتال با موفقیت انجام شد.")
    return chart_data


def calculate_part_of_fortune(
    planet_longitudes: Dict[str, float],
    ascendant_deg: float,
    cusps_raw,
    ascmc,
    house_system: str
) -> Dict[str, Any]:
    """
    محاسبه سهم سعادت (Part of Fortune) بر اساس فرمول کلاسیک:
      POF = Asc + Moon - Sun
    (در صورت نبودن اطلاعات خورشید یا ماه، مقدار پیش‌فرض برگردانده می‌شود.)
    """

    if 'sun' not in planet_longitudes or 'moon' not in planet_longitudes:
        logging.warning("⚠️ سهم سعادت محاسبه نشد: موقعیت خورشید یا ماه موجود نیست.")
        return {
            'degree': 0.0,
            'sign': 'نامشخص',
            'sign_degree': 0.0,
            'house': 0,
            'house_name': get_house_name_fa(0)
        }

    fortune_deg = (ascendant_deg +
                   planet_longitudes['moon'] -
                   planet_longitudes['sun']) % 360.0

    house_num = 0
    try:
        house_pos = se.house_pos(
            fortune_deg, 0.0, cusps_raw, ascmc, house_system.upper().encode('utf-8')
        )
        house_num = int(house_pos[0])
    except Exception as e:
        logging.warning(f"⚠️ خطا در محاسبه خانه برای سهم سعادت: {e}")
        house_num = 0

    return {
        'degree': fortune_deg,
        'sign': get_sign_fa(fortune_deg),
        'sign_degree': get_degree_in_sign(fortune_deg),
        'house': house_num,
        'house_name': get_house_name_fa(house_num),
    }


def calculate_aspects(planets_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    محاسبه زوایا (Aspects) بین سیارات اصلی.
    - سیارات کمکی مثل true_node, lilith, chiron حذف می‌شوند.
    - خروجی لیستی از دیکشنری‌ها با کلیدهای:
        'p1', 'p2', 'aspect', 'orb'
      که 'aspect' نام استاندارد انگلیسی (Conjunction, Square, ...) است.
    """

    aspects: List[Dict[str, Any]] = []

    # فقط سیارات اصلی را برای زوایا در نظر می‌گیریم
    filtered_planets = [
        p for p in planets_list
        if p.get('name') not in ['true_node', 'lilith', 'chiron']
    ]

    n = len(filtered_planets)
    for i in range(n):
        for j in range(i + 1, n):
            p1 = filtered_planets[i]
            p2 = filtered_planets[j]

            lon1 = float(p1['degree'])
            lon2 = float(p2['degree'])

            angle = abs(lon1 - lon2)
            # کوتاه‌ترین فاصله روی دایره (0 تا 180)
            angle = min(angle, 360.0 - angle)

            for aspect_def in ASPECT_DEFS:
                target = aspect_def['degree']
                orb = aspect_def['orb']

                if abs(angle - target) <= orb:
                    aspects.append({
                        'p1': p1['name'],
                        'p2': p2['name'],
                        'aspect': aspect_def['name_en'],  # اسم استاندارد انگلیسی
                        'orb': round(abs(angle - target), 2),
                    })

    return aspects
