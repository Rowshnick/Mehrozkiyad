# ============================================================
#  CHART_ENGINE_REAL (REAL VERSION)
#  Fully rewritten by Roshina Project
# ============================================================

from datetime import datetime
from .planets import compute_planets
from .houses import compute_houses
from .aspects import compute_aspects

def build_chart_from_datetime(date, time, lat, lon, tz):
    """Build a real natal chart from birth data."""

    # 1) ساخت datetime کامل
    dt = datetime.combine(date, time)

    # 2) محاسبه سیارات
    planets = compute_planets(dt, tz)

    # 3) محاسبه خانه‌ها
    houses = compute_houses(dt, lat, lon, tz)

    # 4) محاسبه جنبه‌ها
    aspects = compute_aspects(planets)

    # 5) ساخت ساختار نهایی چارت
    chart = {
        "planets": planets,
        "houses": houses,
        "aspects": aspects,
        "meta": {
            "datetime": dt,
            "lat": lat,
            "lon": lon,
            "tz": tz
        }
    }

    return chart
