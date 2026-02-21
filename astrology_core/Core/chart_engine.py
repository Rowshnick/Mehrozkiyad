# astrology_core/Core/chart_engine.py
# نسخهٔ استاندارد و کامل

from astrology_core.Engine.planets import get_time, get_all_planets
from astrology_core.Engine.houses import compute_houses
from astrology_core.Core.aspects import compute_all_aspects
from astrology_core.Core.midpoints import build_midpoints
from astrology_core.Core.dial90 import build_90_points
from astrology_core.Core.points import get_extra_points


def build_chart(
    year,
    month,
    day,
    hour,
    minute,
    tz_offset,
    latitude_deg,
    longitude_deg,
    house_system="placidus",
    include_midpoints=True,
    include_dial90=True,
):
    """
    ساخت چارت کامل نجومی با ساختار استاندارد
    """

    # 1) زمان
    t = get_time(year, month, day, hour, minute, tz_offset)

    # 2) سیارات
    planets = get_all_planets(t)

    # 3) خانه‌ها
    house_list = compute_houses(t, latitude_deg, longitude_deg, house_system)

    # تبدیل لیست به دیکشنری استاندارد
    houses = {
        f"Cusp{i+1}": {"lon": house_list[i]}
        for i in range(12)
    }

    # 4) Asc و MC
    asc = houses["Cusp1"]["lon"]
    mc = houses["Cusp10"]["lon"]

    # 5) نقاط اضافی (Node, Lilith, Fortune, Vertex, East Point)
    extra_points = get_extra_points(
        t,
        asc,
        mc,
        latitude_deg,
        longitude_deg,
        planets
    )

    # 6) جنبه‌ها
    aspects = compute_all_aspects(planets, houses, extra_points)

    # 7) میدپوینت‌ها
    midpoints = build_midpoints(planets, houses, extra_points) if include_midpoints else {}

    # 8) دایال ۹۰ درجه
    dial90 = build_90_points(planets, houses, extra_points) if include_dial90 else {}

    # 9) خروجی نهایی استاندارد
    return {
        "time": {
            "year": year,
            "month": month,
            "day": day,
            "hour": hour,
            "minute": minute,
            "tz_offset": tz_offset,
        },
        "location": {
            "latitude": latitude_deg,
            "longitude": longitude_deg,
        },
        "planets": planets,
        "houses": houses,              # ← دیکشنری استاندارد
        "points": extra_points,        # ← دیکشنری استاندارد
        "aspects": aspects,
        "midpoints": midpoints,
        "dial90": dial90,
    }
