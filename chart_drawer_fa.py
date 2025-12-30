# chart_drawer_fa.py
# =============================================================================
# ترسیم چارت نجومی فارسی با فونت خوانا (Vazirmatn)
# =============================================================================

import math
import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# تنظیم فونت فارسی
plt.rcParams['font.family'] = 'Vazirmatn'
plt.rcParams['font.size'] = 14
plt.rcParams['axes.unicode_minus'] = False

# نام فارسی برج‌ها
SIGNS_FA = [
    "حمل", "ثور", "جوزا", "سرطان", "اسد", "سنبله",
    "میزان", "عقرب", "قوس", "جدی", "دلو", "حوت"
]

# نمادهای سیارات (برای زیبایی)
PLANET_SYMBOLS_FA = {
    "sun": "☉",
    "moon": "☾",
    "mercury": "☿",
    "venus": "♀",
    "mars": "♂",
    "jupiter": "♃",
    "saturn": "♄",
    "uranus": "♅",
    "neptune": "♆",
    "pluto": "♇",
    "true_node": "☊",
    "chiron": "⚷",
    "lilith": "⚸",
}

def draw_chart_wheel_fa(chart_data):
    """
    ترسیم چارت نجومی فارسی با فونت خوانا
    """
    fig, ax = plt.subplots(figsize=(9, 9), dpi=150)
    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-1.1, 1.1)
    ax.set_aspect("equal")
    ax.axis("off")

    # -------------------------------------------------------------------------
    # 1) دایره‌های اصلی چارت
    # -------------------------------------------------------------------------
    outer_circle = plt.Circle((0, 0), 1.0, fill=False, linewidth=2)
    inner_circle = plt.Circle((0, 0), 0.75, fill=False, linewidth=1.5)

    ax.add_patch(outer_circle)
    ax.add_patch(inner_circle)

    # -------------------------------------------------------------------------
    # 2) تقسیم‌بندی ۱۲ برج
    # -------------------------------------------------------------------------
    for i in range(12):
        angle_deg = i * 30
        angle_rad = math.radians(angle_deg)

        x1 = math.cos(angle_rad)
        y1 = math.sin(angle_rad)
        x2 = 0.75 * math.cos(angle_rad)
        y2 = 0.75 * math.sin(angle_rad)

        ax.plot([x1, x2], [y1, y2], color="black", linewidth=1)

        # نام برج‌ها
        mid_angle = angle_deg + 15
        mid_rad = math.radians(mid_angle)
        tx = 0.87 * math.cos(mid_rad)
        ty = 0.87 * math.sin(mid_rad)

        ax.text(tx, ty, SIGNS_FA[i], ha="center", va="center", fontsize=14)

    # -------------------------------------------------------------------------
    # 3) رسم سیارات
    # -------------------------------------------------------------------------
    planets = chart_data["planets_list"]

    for p in planets:
        lon = p["degree"]
        symbol = PLANET_SYMBOLS_FA.get(p["name"], p["name"])

        angle_rad = math.radians(lon)
        px = 0.62 * math.cos(angle_rad)
        py = 0.62 * math.sin(angle_rad)

        ax.text(px, py, symbol, ha="center", va="center", fontsize=16)

    # -------------------------------------------------------------------------
    # 4) خروجی تصویر
    # -------------------------------------------------------------------------
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    buf.seek(0)
    plt.close(fig)

    return buf
