
from .planets import get_all_planets, get_time
from .houses import get_ascendant, get_mc, placidus_houses
from .aspects import detect_aspects
from .points import get_extra_points

def compute_natal_chart(year, month, day, hour, minute, tz_offset, lat, lon):
    t = get_time(year, month, day, hour, minute, tz_offset)
    planets = get_all_planets(t)
    asc = get_ascendant(t, lat, lon)
    mc = get_mc(t, lon)
    houses = placidus_houses(t, lat, lon)
    sun_lon = float(planets["Sun"]["lon"])
    moon_lon = float(planets["Moon"]["lon"])
    extra = get_extra_points(t, lat, lon, asc, sun_lon, moon_lon)
    all_points = {
        **planets,
        **extra,
        "Ascendant": {"lon": asc, "lat": 0.0},
        "Midheaven": {"lon": mc, "lat": 0.0},
    }
    aspects = detect_aspects(all_points)
    return {
        "planets": planets,
        "extra_points": extra,
        "ascendant": asc,
        "midheaven": mc,
        "houses": houses,
        "aspects": aspects,
        "all_points": all_points,
    }
