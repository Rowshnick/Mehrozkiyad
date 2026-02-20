#aspects.py

import numpy as np

# تعریف جنبه‌ها و زاویهٔ دقیق آن‌ها
ASPECTS = {
    "Conjunction": 0,
    "Opposition": 180,
    "Trine": 120,
    "Square": 90,
    "Sextile": 60,
}

# اورب استاندارد
ORB = 6

def angle_diff(a, b):
    """
    اختلاف زاویه‌ای بین دو نقطه روی دایره (۰ تا ۱۸۰ درجه)
    """
    d = abs(a - b) % 360
    return min(d, 360 - d)

def detect_aspects(objects):
    """
    objects باید دیکشنری‌ای باشد که هر کلید یک سیاره/نقطه و مقدار آن:
    {"lon": ..., "lat": ...}

    خروجی: لیستی از جنبه‌ها
    """
    aspects = []
    keys = list(objects.keys())

    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            p1 = keys[i]
            p2 = keys[j]

            lon1 = objects[p1]["lon"]
            lon2 = objects[p2]["lon"]

            diff = angle_diff(lon1, lon2)

            for asp_name, asp_angle in ASPECTS.items():
                if abs(diff - asp_angle) <= ORB:
                    aspects.append({
                        "p1": p1,
                        "p2": p2,
                        "aspect": asp_name,
                        "orb": abs(diff - asp_angle)
                    })

    return aspects
