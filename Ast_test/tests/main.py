import json
from astrology_engine.core.planets import (
    get_time,
    get_all_planets,
    get_aspect_engine,
    get_oob_planets
)

# ---------------------------------------------------------
# ابزارهای کمکی
# ---------------------------------------------------------

def print_header(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)

def group_aspects(aspects):
    groups = {"Longitude": [], "Declination": [], "Latitude": []}
    for a in aspects:
        groups[a["category"]].append(a)
    return groups

def sort_aspects(aspects):
    return sorted(aspects, key=lambda x: x["orb"])

def filter_aspects(aspects, max_orb=2.0):
    return [a for a in aspects if a["orb"] <= max_orb]

# ---------------------------------------------------------
# 1) تست چند تاریخ پشت‌سرهم
# ---------------------------------------------------------

dates = [
    (1990, 1, 1, 12, 0, 0),
    (2000, 6, 15, 18, 30, 0),
    (2024, 5, 10, 14, 0, 0),
]

print_header("MULTI-DATE TEST")

for y, m, d, hh, mm, ss in dates:
    t = get_time(y, m, d, hh, mm, ss)
    planets = get_all_planets(t)
    print(f"\nDate: {y}-{m}-{d}  {hh}:{mm}")
    print(f"Sun lon: {planets['Sun']['lon']:.4f}  Moon lon: {planets['Moon']['lon']:.4f}")

# ---------------------------------------------------------
# 2) تست ترانزیت‌ها (Transit Engine ساده)
# ---------------------------------------------------------

print_header("TRANSIT TEST (Sun Transit to Natal Sun)")

# چارت تولد
natal_t = get_time(1990, 1, 1, 12, 0, 0)
natal = get_all_planets(natal_t)
natal_sun = natal["Sun"]["lon"]

# ترانزیت یک روز خاص
transit_t = get_time(2024, 5, 10, 12, 0, 0)
transit = get_all_planets(transit_t)
transit_sun = transit["Sun"]["lon"]

angle = abs(transit_sun - natal_sun)
if angle > 180:
    angle = 360 - angle

print(f"Transit Sun angle to Natal Sun: {angle:.4f}°")

# ---------------------------------------------------------
# 3) تست Progressions (Secondary Progressed Sun)
# ---------------------------------------------------------

print_header("SECONDARY PROGRESSION TEST")

# 1 روز = 1 سال
progressed_t = get_time(1990, 1, 2, 12, 0, 0)
progressed = get_all_planets(progressed_t)

print(f"Progressed Sun lon: {progressed['Sun']['lon']:.4f}")

# ---------------------------------------------------------
# 4) تست Aspect Engine با گروه‌بندی و مرتب‌سازی
# ---------------------------------------------------------

print_header("ASPECT ENGINE — SORTED & GROUPED")

t = get_time(1990, 1, 1, 12, 0, 0)
planets = get_all_planets(t)
aspects = get_aspect_engine(planets)

groups = group_aspects(aspects)

for cat, items in groups.items():
    print_header(cat)
    for a in sort_aspects(items):
        line = f"{a['type']:18}  {a['p1']:8} - {a['p2']:8}  orb={a['orb']:.4f}"
        if a["angle"] is not None:
            line += f"  angle={a['angle']:.4f}"
        print(line)

# ---------------------------------------------------------
# 5) تست فیلتر جنبه‌ها (فقط جنبه‌های مهم)
# ---------------------------------------------------------

print_header("FILTERED ASPECTS (orb <= 1°)")

filtered = filter_aspects(aspects, max_orb=1.0)
for a in filtered:
    print(f"{a['category']:12} {a['type']:18} {a['p1']:8}-{a['p2']:8} orb={a['orb']:.4f}")

# ---------------------------------------------------------
# 6) خروجی JSON
# ---------------------------------------------------------

print_header("JSON OUTPUT")

json_output = json.dumps(aspects, indent=4)
print(json_output)
