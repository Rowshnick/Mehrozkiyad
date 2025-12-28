# chart_drawer_fa.py
# =============================================================================
# ماژول رسم چارت ناتال به زبان فارسی
# -----------------------------------------------------------------------------
# این فایل خروجی astrology_core را دریافت کرده و یک چارت تصویری (PNG)
# از چرخۀ زودیاک، خانه‌ها و موقعیت سیارات تولید می‌کند.
#
# نکات مهم:
# - سازگار با Railway (بدون نیاز به فونت خارجی)
# - استفاده از matplotlib با فونت پیش‌فرض DejaVu Sans (پشتیبانی مناسب از فارسی)
# - هماهنگ با ساختار جدید chart_data:
#       chart_data['planets_list']
#       chart_data['houses']['cusps']
#       chart_data['ascendant']
#       chart_data['mc']
# =============================================================================

import io
import math
import matplotlib
matplotlib.use("Agg")  # برای سازگاری با Railway و محیط‌های بدون GUI
import matplotlib.pyplot as plt

# -----------------------------------------------------------------------------
# تنظیم فونت فارسی (DejaVu Sans که در matplotlib موجود است)
# -----------------------------------------------------------------------------
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 12


# =============================================================================
# تابع اصلی رسم چارت
# =============================================================================

def draw_chart_wheel_fa(chart_data):
    """
    ورودی:
        chart_data از astrology_core
    خروجی:
        BytesIO شامل تصویر PNG چارت
    """

    planets = chart_data['planets_list']
    cusps = chart_data['houses']['cusps']
    asc = chart_data['houses']['asc']
    mc = chart_data['houses']['mc']

    # -----------------------------------------------------------------------------
    # ۱) ایجاد بوم و محور
    # -----------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 8), dpi=150)
    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-1.1, 1.1)
    ax.set_aspect("equal")
    ax.axis("off")

    # -----------------------------------------------------------------------------
    # ۲) رسم دایره‌های اصلی
    # -----------------------------------------------------------------------------
    outer_r = 1.0
    inner_r = 0.75
    house_r = 0.55

    circle_outer = plt.Circle((0, 0), outer_r, fill=False, linewidth=2)
    circle_inner = plt.Circle((0, 0), inner_r, fill=False, linewidth=1.5)
    circle_house = plt.Circle((0, 0), house_r, fill=False, linewidth=1)

    ax.add_patch(circle_outer)
    ax.add_patch(circle_inner)
    ax.add_patch(circle_house)

    # -----------------------------------------------------------------------------
    # ۳) رسم برج‌ها (هر ۳۰ درجه)
    # -----------------------------------------------------------------------------
    for i in range(12):
        angle_deg = i * 30
        angle_rad = math.radians(angle_deg)

        x1 = inner_r * math.cos(angle_rad)
        y1 = inner_r * math.sin(angle_rad)
        x2 = outer_r * math.cos(angle_rad)
        y2 = outer_r * math.sin(angle_rad)

        ax.plot([x1, x2], [y1, y2], color="black", linewidth=1)

        # نام برج‌ها (فارسی)
        sign_names = [
            "حمل", "ثور", "جوزا", "سرطان", "اسد", "سنبله",
            "میزان", "عقرب", "قوس", "جدی", "دلو", "حوت"
        ]
        label_angle = math.radians(angle_deg + 15)
        lx = 0.9 * math.cos(label_angle)
        ly = 0.9 * math.sin(label_angle)
        ax.text(lx, ly, sign_names[i], ha="center", va="center")

    # -----------------------------------------------------------------------------
    # ۴) رسم خانه‌ها بر اساس cusps
    # -----------------------------------------------------------------------------
    for cusp_deg in cusps:
        angle_rad = math.radians(cusp_deg)

        x1 = house_r * math.cos(angle_rad)
        y1 = house_r * math.sin(angle_rad)
        x2 = inner_r * math.cos(angle_rad)
        y2 = inner_r * math.sin(angle_rad)

        ax.plot([x1, x2], [y1, y2], color="gray", linewidth=1)

    # -----------------------------------------------------------------------------
    # ۵) رسم سیارات
    # -----------------------------------------------------------------------------
    for p in planets:
        deg = p['degree']
        angle_rad = math.radians(deg)

        # موقعیت سیاره روی دایره داخلی
        px = 0.82 * math.cos(angle_rad)
        py = 0.82 * math.sin(angle_rad)

        # نام فارسی سیاره
        planet_fa = {
            'sun': '☉ خورشید',
            'moon': '☾ ماه',
            'mercury': '☿ عطارد',
            'venus': '♀ زهره',
            'mars': '♂ مریخ',
            'jupiter': '♃ مشتری',
            'saturn': '♄ زحل',
            'uranus': '♅ اورانوس',
            'neptune': '♆ نپتون',
            'pluto': '♇ پلوتو',
            'true_node': '☊ گره شمالی',
            'chiron': '⚷ کایرون',
            'lilith': '⚸ لیلیت',
        }.get(p['name'], p['name'])

        ax.text(px, py, planet_fa, ha="center", va="center", fontsize=10)

    # -----------------------------------------------------------------------------
    # ۶) رسم ASC و MC
    # -----------------------------------------------------------------------------
    asc_rad = math.radians(asc)
    mc_rad = math.radians(mc)

    ax.text(
        1.05 * math.cos(asc_rad),
        1.05 * math.sin(asc_rad),
        "ASC",
        fontsize=12,
        color="red",
        ha="center",
        va="center"
    )

    ax.text(
        1.05 * math.cos(mc_rad),
        1.05 * math.sin(mc_rad),
        "MC",
        fontsize=12,
        color="blue",
        ha="center",
        va="center"
    )

    # -----------------------------------------------------------------------------
    # ۷) خروجی به‌صورت BytesIO
    # -----------------------------------------------------------------------------
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png", bbox_inches="tight", dpi=150)
    buffer.seek(0)
    plt.close(fig)

    return buffer
