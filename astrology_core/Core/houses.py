# astrology_core/Core/houses.py
# House Engine:
# - محاسبه Asc و MC
# - ساخت خانه‌ها (Equal House از Asc)

import numpy as np

from astrology_core.Engine.planets import ts, eph


def get_asc_mc(t, latitude_deg: float, longitude_deg: float):
    """
    محاسبه Ascendant و Midheaven (MC) بر حسب طول دایرةالبروجی (درجه)
    t: زمان Skyfield (خروجی get_time)
    latitude_deg: عرض جغرافیایی محل (مثلاً 52.37 برای آمستردام)
    longitude_deg: طول جغرافیایی محل (مثلاً 4.90 برای آمستردام، شرق مثبت)
    """

    # تبدیل به رادیان
    phi = np.radians(latitude_deg)          # عرض جغرافیایی
    lon = np.radians(longitude_deg)         # طول جغرافیایی
    eps = np.radians(23.4392911)            # اوبلیکویتی

    # زمان اختری محلی (Local Sidereal Time)
    # t.gast = Greenwich Apparent Sidereal Time (ساعت)
    gast_hours = t.gast
    theta = np.radians(gast_hours * 15.0) + lon  # تبدیل به رادیان و اضافه کردن طول جغرافیایی

    # نرمال‌سازی
    theta = theta % (2 * np.pi)

    # فرمول‌های استاندارد MC و Asc روی دایرةالبروج
    # MC:
    # tan(λ_MC) = (sin(θ) * cos(ε) + tan(φ) * sin(ε)) / cos(θ)
    num_mc = np.sin(theta) * np.cos(eps) + np.tan(phi) * np.sin(eps)
    den_mc = np.cos(theta)
    lam_mc = np.degrees(np.arctan2(num_mc, den_mc)) % 360.0

    # Asc:
    # tan(λ_ASC) = -cos(θ) / (sin(θ)*cos(ε) - tan(φ)*sin(ε))
    num_asc = -np.cos(theta)
    den_asc = np.sin(theta) * np.cos(eps) - np.tan(phi) * np.sin(eps)
    lam_asc = np.degrees(np.arctan2(num_asc, den_asc)) % 360.0

    return lam_asc, lam_mc


def build_equal_houses(asc_lon: float):
    """
    ساخت خانه‌ها به روش Equal House از Asc:
    - خانه ۱ از Asc شروع می‌شود
    - هر خانه ۳۰ درجه
    خروجی: لیست ۱۲تایی طول شروع هر خانه
    """

    houses = []
    for i in range(12):
        h = (asc_lon + i * 30.0) % 360.0
        houses.append(h)
    return houses


def get_house_index(point_lon: float, houses: list):
    """
    تعیین شمارهٔ خانه برای یک نقطه (طول دایرةالبروجی) بر اساس
    خانه‌های Equal House.
    خروجی: عدد 1 تا 12
    """

    # فرض: houses = شروع هر خانه، به ترتیب از خانه ۱ تا ۱۲
    for i in range(12):
        start = houses[i]
        end = houses[(i + 1) % 12]

        if start < end:
            if start <= point_lon < end:
                return i + 1
        else:
            # عبور از 360
            if point_lon >= start or point_lon < end:
                return i + 1

    return None  # نباید برسیم اینجا، ولی برای اطمینان


def assign_planets_to_houses(planets: dict, houses: list):
    """
    نسبت دادن سیارات به خانه‌ها بر اساس طول دایرةالبروجی‌شان.
    planets: خروجی get_all_planets
    houses: خروجی build_equal_houses
    خروجی: دیکشنری {planet_name: house_number}
    """

    result = {}
    for name, data in planets.items():
        lon = data["lon"]
        h = get_house_index(lon, houses)
        result[name] = h
    return result


# ---------------------------------------------------------
# Whole Sign House System
# ---------------------------------------------------------

def build_whole_sign_houses(asc_lon: float):
    """
    ساخت خانه‌ها به روش Whole Sign:
    - خانه ۱ = درجهٔ صفر نشانهٔ Asc
    - هر خانه = ۳۰ درجه
    - Asc داخل خانهٔ ۱ قرار می‌گیرد
    """

    # نشانهٔ Asc (هر نشانه ۳۰ درجه)
    asc_sign = int(asc_lon // 30)  # 0 تا 11

    houses = []
    for i in range(12):
        # شروع هر خانه = شروع نشانه
        cusp = ((asc_sign + i) % 12) * 30
        houses.append(cusp)

    return houses


def get_house_index_whole_sign(point_lon: float, houses: list):
    """
    تعیین شمارهٔ خانه در Whole Sign:
    - هر خانه دقیقاً ۳۰ درجه است
    - houses = شروع هر خانه (۰، ۳۰، ۶۰، ...)
    """

    for i in range(12):
        start = houses[i]
        end = houses[(i + 1) % 12]

        if start < end:
            if start <= point_lon < end:
                return i + 1
        else:
            # عبور از 360
            if point_lon >= start or point_lon < end:
                return i + 1

    return None


def assign_planets_to_whole_sign_houses(planets: dict, houses: list):
    """
    نسبت دادن سیارات به خانه‌ها در Whole Sign.
    """

    result = {}
    for name, data in planets.items():
        lon = data["lon"]
        h = get_house_index_whole_sign(lon, houses)
        result[name] = h

    return result


# ---------------------------------------------------------
# Placidus House System
# ---------------------------------------------------------

def placidus_cusp(t, latitude_deg, longitude_deg, house_number):
    """
    محاسبهٔ یک کاسپ Placidus برای خانهٔ مشخص.
    house_number = 1 تا 12
    """

    # تبدیل به رادیان
    lat = np.radians(latitude_deg)
    lon = np.radians(longitude_deg)
    eps = np.radians(23.4392911)

    # زمان اختری محلی
    gast_hours = t.gast
    theta = np.radians(gast_hours * 15.0) + lon
    theta = theta % (2 * np.pi)

    # MC
    num_mc = np.sin(theta) * np.cos(eps) + np.tan(lat) * np.sin(eps)
    den_mc = np.cos(theta)
    mc = np.arctan2(num_mc, den_mc)

    # RA of MC
    ra_mc = np.arctan2(np.sin(theta), np.cos(theta))

    # جدول تقسیم Placidus
    if house_number in [11, 12]:
        factor = 3
    elif house_number in [2, 3]:
        factor = 1
    else:
        # خانه‌های 1، 4، 7، 10 مستقیم هستند
        if house_number == 10:
            return np.degrees(mc) % 360
        if house_number == 4:
            return (np.degrees(mc) + 180) % 360
        if house_number == 1:
            asc, _ = get_asc_mc(t, latitude_deg, longitude_deg)
            return asc
        if house_number == 7:
            asc, _ = get_asc_mc(t, latitude_deg, longitude_deg)
            return (asc + 180) % 360

    # زاویهٔ تقسیم
    h = np.radians(30 * factor)

    # RA هدف
    ra_target = ra_mc + h
    ra_target = (ra_target + 2 * np.pi) % (2 * np.pi)

    # تبدیل RA به طول دایرةالبروجی
    lon_cusp = np.degrees(
        np.arctan2(
            np.sin(ra_target) * np.cos(eps) - np.tan(lat) * np.sin(eps),
            np.cos(ra_target)
        )
    ) % 360

    return lon_cusp


def build_placidus_houses(t, latitude_deg, longitude_deg):
    """
    ساخت ۱۲ کاسپ Placidus
    """

    houses = []
    for h in range(1, 13):
        cusp = placidus_cusp(t, latitude_deg, longitude_deg, h)
        houses.append(cusp)

    return houses


def assign_planets_to_placidus(planets: dict, houses: list):
    """
    نسبت دادن سیارات به خانه‌های Placidus
    """

    result = {}
    for name, data in planets.items():
        lon = data["lon"]
        h = get_house_index(lon, houses)
        result[name] = h

    return result


