# ============================================================
#  CHART_ENGINE (THEME-DRIVEN VERSION)
#  Fully rewritten by Roshina Project
# ============================================================

import math
from datetime import datetime


# ============================
#  SAMPLE DATA HELPERS
# ============================

def _wrap_lon(lon):
    """Normalize longitude to 0–360."""
    return lon % 360


def _sample_planets():
    """
    سیارات نمونه برای تست رندر.
    این مقادیر واقعی نجومی نیستند، فقط برای تست گرافیک هستند.
    """
    return {
        "Sun":     {"lon": _wrap_lon(15.0)},    # 15° Aries
        "Moon":    {"lon": _wrap_lon(92.0)},    # 2° Cancer
        "Mercury": {"lon": _wrap_lon(40.0)},    # 10° Taurus
        "Venus":   {"lon": _wrap_lon(130.0)},   # 10° Leo
        "Mars":    {"lon": _wrap_lon(210.0)},   # 0° Scorpio
        "Jupiter": {"lon": _wrap_lon(275.0)},   # 5° Capricorn
        "Saturn":  {"lon": _wrap_lon(305.0)},   # 5° Aquarius
        "Uranus":  {"lon": _wrap_lon(45.0)},    # 15° Taurus
        "Neptune": {"lon": _wrap_lon(330.0)},   # 0° Pisces
        "Pluto":   {"lon": _wrap_lon(250.0)},   # 10° Sagittarius
        "Node":    {"lon": _wrap_lon(180.0)},   # 0° Libra
        "Lilith":  {"lon": _wrap_lon(60.0)},    # 0° Gemini
        "Fortune": {"lon": _wrap_lon(10.0)},    # 10° Aries
    }


def _sample_houses():
    """
    خانه‌های نمونه (سیستم ساده ۳۰ درجه‌ای فقط برای تست).
    """
    houses = {}
    for i in range(12):
        lon = _wrap_lon(i * 30.0)  # هر خانه ۳۰ درجه
        houses[f"Cusp{i+1}"] = {"lon": lon}
    return houses


def _sample_aspects(planets):
    """
    چند جنبهٔ نمونه بین سیارات برای تست خطوط جنبه‌ها.
    """
    def aspect_strength(exact_deg_diff, orb=6):
        diff = min(abs(exact_deg_diff), 360 - abs(exact_deg_diff))
        return max(0.0, 1.0 - diff / orb)

    def angle(p1, p2):
        return _wrap_lon(planets[p2]["lon"] - planets[p1]["lon"])

    aspects = []

    # Sun – Moon (Opposition)
    diff = angle("Sun", "Moon")
    aspects.append({
        "planet1": "Sun",
        "planet2": "Moon",
        "aspect": "opposition",
        "strength": aspect_strength(diff - 180),
    })

    # Sun – Mars (Trine)
    diff = angle("Sun", "Mars")
    aspects.append({
        "planet1": "Sun",
        "planet2": "Mars",
        "aspect": "trine",
        "strength": aspect_strength(diff - 120),
    })

    # Moon – Venus (Square)
    diff = angle("Moon", "Venus")
    aspects.append({
        "planet1": "Moon",
        "planet2": "Venus",
        "aspect": "square",
        "strength": aspect_strength(diff - 90),
    })

    # Mercury – Uranus (Conjunction)
    diff = angle("Mercury", "Uranus")
    aspects.append({
        "planet1": "Mercury",
        "planet2": "Uranus",
        "aspect": "conjunction",
        "strength": aspect_strength(diff - 0),
    })

    return {"planet_aspects": aspects}


def _sample_points():
    """
    نقاط حساس نمونه (برای تست).
    """
    return {
        "Fortune": {"lon": _wrap_lon(10.0)},
        "Node": {"lon": _wrap_lon(180.0)},
        "Lilith": {"lon": _wrap_lon(60.0)},
    }


# ============================
#  PUBLIC API
# ============================

def build_sample_chart():
    """
    ساخت یک چارت نمونه برای تست رندر.
    خروجی با ساختار مورد نیاز رندر سازگار است.
    """
    planets = _sample_planets()
    houses = _sample_houses()
    aspects = _sample_aspects(planets)
    points = _sample_points()

    chart = {
        "meta": {
            "type": "sample",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "note": "Sample chart for rendering test",
        },
        "planets": planets,
        "houses": houses,
        "aspects": aspects,
        "points": points,
    }
    return chart


if __name__ == "__main__":
    # تست سریع در صورت اجرای مستقیم فایل
    from astrology_core.Render.advanced_renderer import render_chart_pretty

    chart = build_sample_chart()
    fig = render_chart_pretty(chart, theme="roshina", save_as="png", save_dir=".", save_name="sample_chart")
    print("Sample chart rendered and saved as sample_chart.png")










# astrology_core/Core/chart_engine.py
# نسخهٔ اصلاح‌شده برای معماری جدید

import numpy as np

# =========================
#  IMPORTS (NEW ARCHITECTURE)
# =========================

# زمان و سیارات
from ..Engine.planets import (
    get_time,
    get_all_planets,
)

# سیستم‌های خانه‌ها (فایل جدید تو)
from .houses import (
    get_asc_mc,
    build_equal_houses,
    build_whole_sign_houses,
    build_placidus_houses,
    build_koch_houses,
    build_porphyry_houses,
    build_regiomontanus_houses,
    build_campanus_houses,
)

# جنبه‌ها و میدپوینت‌ها (اگر فایل‌ها موجودند)
try:
    from .aspects import compute_all_aspects
except:
    compute_all_aspects = None

try:
    from .midpoints import build_midpoints
except:
    build_midpoints = None


# =========================
#  انتخاب سیستم خانه‌ها
# =========================

def compute_houses(t, lat, lon, system="placidus"):
    system = system.lower()

    if system == "equal":
        asc, _ = get_asc_mc(t, lat, lon)
        return build_equal_houses(asc)

    elif system == "whole":
        asc, _ = get_asc_mc(t, lat, lon)
        return build_whole_sign_houses(asc)

    elif system == "placidus":
        return build_placidus_houses(t, lat, lon)

    elif system == "koch":
        return build_koch_houses(t, lat, lon)

    elif system == "porphyry":
        return build_porphyry_houses(t, lat, lon)

    elif system == "regiomontanus":
        return build_regiomontanus_houses(t, lat, lon)

    elif system == "campanus":
        return build_campanus_houses(t, lat, lon)

    else:
        raise ValueError(f"Unknown house system: {system}")


# =========================
#  ساخت چارت کامل
# =========================

def build_chart(
    year, month, day,
    hour, minute,
    tz_offset,
    latitude_deg, longitude_deg,
    house_system="placidus",
    include_midpoints=True,
    include_dial90=True,
):
    """
    خروجی: دیکشنری کامل چارت
    """

    # 1) زمان Skyfield
    t = get_time(year, month, day, hour, minute, tz_offset)

    # 2) سیارات
    planets = get_all_planets(t)

    # 3) خانه‌ها
    houses = compute_houses(t, latitude_deg, longitude_deg, house_system)

    # 4) جنبه‌ها
    if compute_all_aspects:
        aspects = compute_all_aspects(planets)
    else:
        aspects = {"planet_aspects": []}

    # 5) میدپوینت‌ها
    if include_midpoints and build_midpoints:
        midpoints = build_midpoints(planets)
    else:
        midpoints = {}

    # 6) خروجی نهایی
    chart = {
        "planets": planets,
        "houses": {f"Cusp{i+1}": {"lon": houses[i]} for i in range(12)},
        "aspects": aspects,
        "midpoints": midpoints,
        "meta": {
            "house_system": house_system,
            "latitude": latitude_deg,
            "longitude": longitude_deg,
            "include_midpoints": include_midpoints,
            "include_dial90": include_dial90,
        }
    }

    return chart
