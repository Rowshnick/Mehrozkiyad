from astrology_engine.core.planets import (
    get_time,
    get_all_planets,
    get_aspect_engine,
    get_oob_planets
)

# ---------------------------------------------------------
# تابع کمکی برای چاپ مرتب
# ---------------------------------------------------------
def print_header(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

# ---------------------------------------------------------
# 1) ساخت زمان تست
# ---------------------------------------------------------
t = get_time(1990, 1, 1, 12, 0, 0)

# ---------------------------------------------------------
# 2) گرفتن موقعیت کامل سیارات
# ---------------------------------------------------------
planets = get_all_planets(t)

print_header("Planet Positions")
for name, data in planets.items():
    print(f"{name:8}  "
          f"lon={data['lon']:.4f}  "
          f"lat={data['lat']:.4f}  "
          f"dec={data['declination']:.4f}  "
          f"R={data['retrograde']}  "
          f"v_lon={data['speed_lon']:.4f}")

# ---------------------------------------------------------
# 3) تست OOB
# ---------------------------------------------------------
print_header("Out Of Bounds Planets")
oob = get_oob_planets(planets)
if not oob:
    print("No OOB planets.")
else:
    for item in oob:
        print(f"{item['planet']:8}  dec={item['declination']:.4f}  "
              f"amount={item['amount']:.4f}")

# ---------------------------------------------------------
# 4) تست Aspect Engine
# ---------------------------------------------------------
print_header("Aspect Engine Output")
aspects = get_aspect_engine(planets)

# گروه‌بندی جنبه‌ها
groups = {"Longitude": [], "Declination": [], "Latitude": []}
for a in aspects:
    groups[a["category"]].append(a)

# چاپ هر گروه
for cat, items in groups.items():
    print_header(cat + " Aspects")
    for a in items:
        line = f"{a['type']:18}  {a['p1']:8} - {a['p2']:8}  orb={a['orb']:.4f}"
        if a["angle"] is not None:
            line += f"  angle={a['angle']:.4f}"
        print(line)
