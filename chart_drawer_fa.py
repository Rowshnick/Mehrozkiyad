# chart_drawer_fa.py
# =============================================================================
# نسخه حرفه‌ای و رنگی چارت نجومی فارسی
# =============================================================================

import math
import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm


# -------------------------------
# تنظیم فونت فارسی
# -------------------------------
plt.rcParams['axes.unicode_minus'] = False
font_path = "fonts/Vazirmatn-Black.ttf"
fm.fontManager.addfont(font_path)
plt.rcParams['font.family'] = 'Vazirmatn'
plt.rcParams['font.size'] = 14

# -------------------------------
# رنگ‌های حرفه‌ای برای برج‌ها
# -------------------------------
SIGN_COLORS = [
    "#FF6B6B", "#FFA06B", "#FFD56B", "#E8FF6B",
    "#A6FF6B", "#6BFF8F", "#6BFFD5", "#6BE8FF",
    "#6BB6FF", "#6B7EFF", "#A06BFF", "#D56BFF"
]

# -------------------------------
# نام فارسی برج‌ها
# -------------------------------
SIGNS_FA = [
    "حمل", "ثور", "جوزا", "سرطان", "اسد", "سنبله",
    "میزان", "عقرب", "قوس", "جدی", "دلو", "حوت"
]

# -------------------------------
# نمادهای سیارات
# -------------------------------
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

# -------------------------------
# رنگ‌های سیارات
# -------------------------------
PLANET_COLORS = {
    "sun": "#FFB300",
    "moon": "#C0C0C0",
    "mercury": "#8E8E8E",
    "venus": "#FF69B4",
    "mars": "#FF3B30",
    "jupiter": "#FF9500",
    "saturn": "#C49A6C",
    "uranus": "#30D5C8",
    "neptune": "#007AFF",
    "pluto": "#8E44AD",
    "true_node": "#2ECC71",
    "chiron": "#A569BD",
    "lilith": "#000000",
}

# =============================================================================
# تابع اصلی رسم چارت
# =============================================================================

def draw_chart_wheel_fa(chart_data):
    fig, ax = plt.subplots(figsize=(10, 10), dpi=200)
    ax.set_xlim(-1.15, 1.15)
    ax.set_ylim(-1.15, 1.15)
    ax.set_aspect("equal")
    ax.axis("off")

    # -------------------------------------------------------------------------
    # 1) دایره‌های اصلی با رنگ ملایم
    # -------------------------------------------------------------------------
    outer_circle = plt.Circle((0, 0), 1.0, fill=False, linewidth=3, color="#444")
    mid_circle = plt.Circle((0, 0), 0.78, fill=False, linewidth=2, color="#888")
    inner_circle = plt.Circle((0, 0), 0.60, fill=False, linewidth=1.5, color="#AAA")

    ax.add_patch(outer_circle)
    ax.add_patch(mid_circle)
    ax.add_patch(inner_circle)

    # -------------------------------------------------------------------------
    # 2) تقسیم‌بندی ۱۲ برج با رنگ‌های اختصاصی
    # -------------------------------------------------------------------------
    for i in range(12):
        start_angle = i * 30
        end_angle = start_angle + 30

        # رنگ پس‌زمینه هر برج
        wedge = plt.matplotlib.patches.Wedge(
            center=(0, 0),
            r=1.0,
            theta1=start_angle,
            theta2=end_angle,
            width=0.22,
            facecolor=SIGN_COLORS[i],
            alpha=0.25
        )
        ax.add_patch(wedge)

        # خط جداکننده
        angle_rad = math.radians(start_angle)
        ax.plot(
            [0, math.cos(angle_rad)],
            [0, math.sin(angle_rad)],
            color="#555",
            linewidth=1.2
        )

        # نام برج
        mid_angle = start_angle + 15
        mid_rad = math.radians(mid_angle)
        tx = 0.90 * math.cos(mid_rad)
        ty = 0.90 * math.sin(mid_rad)

        ax.text(
            tx, ty, SIGNS_FA[i],
            ha="center", va="center",
            fontsize=16, fontweight="bold",
            color=SIGN_COLORS[i]
        )

    # -------------------------------------------------------------------------
    # 3) رسم سیارات با رنگ و نماد اختصاصی
    # -------------------------------------------------------------------------
    planets = chart_data["planets_list"]

    for p in planets:
        lon = p["degree"]
        name = p["name"]
        symbol = PLANET_SYMBOLS_FA.get(name, name)
        color = PLANET_COLORS.get(name, "#000")

        angle_rad = math.radians(lon)
        px = 0.68 * math.cos(angle_rad)
        py = 0.68 * math.sin(angle_rad)

        ax.text(
            px, py, symbol,
            ha="center", va="center",
            fontsize=20, fontweight="bold",
            color=color
        )

    # -------------------------------------------------------------------------
    # 4) خروجی تصویر
    # -------------------------------------------------------------------------
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=200, bbox_inches="tight")
    buf.seek(0)
    plt.close(fig)

    return buf
