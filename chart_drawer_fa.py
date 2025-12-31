# chart_drawer_fa.py
# =============================================================================
# ترسیم چارت نجومی فارسی با matplotlib
# نسخهٔ نهایی با پشتیبانی از فونت فارسی + نمادهای نجومی
# =============================================================================

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.font_manager as fm
import io
import logging
import math

# -----------------------------------------------------------------------------
# ۱) تنظیم فونت فارسی + fallback برای نمادهای نجومی
# -----------------------------------------------------------------------------

# مسیر فونت Vazirmatn (نسخه Regular)
# اگر نام فایل متفاوت است، فقط نام فایل را تغییر بده
FA_FONT_PATH = "/usr/share/fonts/truetype/Vazirmatn/Vazirmatn-Regular.ttf"

try:
    fa_prop = fm.FontProperties(fname=FA_FONT_PATH)
    fa_name = fa_prop.get_name()
    plt.rcParams['font.family'] = [fa_name, 'DejaVu Sans']
    logging.info(f"🎨 فونت فارسی فعال شد: {fa_name}")
except Exception as e:
    logging.warning(f"⚠️ فونت فارسی یافت نشد، استفاده از DejaVu Sans → {e}")
    plt.rcParams['font.family'] = ['DejaVu Sans']

plt.rcParams['text.color'] = '#333333'

# -----------------------------------------------------------------------------
# ۲) رنگ‌های برج‌ها
# -----------------------------------------------------------------------------

SIGN_COLORS = [
    "#f8c8dc", "#f8e0c8", "#f8f8c8", "#d0f8c8",
    "#c8f8f8", "#c8d0f8", "#e0c8f8", "#f8c8f0",
    "#f0c8c8", "#d8d8d8", "#c8f0e0", "#e0f8c8"
]

# -----------------------------------------------------------------------------
# ۳) نمادهای سیارات
# -----------------------------------------------------------------------------

PLANET_SYMBOLS = {
    "sun": "☉", "moon": "☽", "mercury": "☿", "venus": "♀", "mars": "♂",
    "jupiter": "♃", "saturn": "♄", "uranus": "♅", "neptune": "♆", "pluto": "♇",
    "true_node": "☊", "chiron": "⚷", "lilith": "⚸"
}

# -----------------------------------------------------------------------------
# ۴) نام فارسی برج‌ها
# -----------------------------------------------------------------------------

SIGNS_FA = [
    "حمل", "ثور", "جوزا", "سرطان", "اسد", "سنبله",
    "میزان", "عقرب", "قوس", "جدی", "دلو", "حوت"
]

# -----------------------------------------------------------------------------
# ۵) تابع اصلی رسم چارت
# -----------------------------------------------------------------------------

def draw_chart_wheel_fa(chart: dict) -> io.BytesIO:
    """
    رسم چارت چرخشی نجومی به زبان فارسی.
    ورودی: chart_data از astrology_core
    خروجی: تصویر BytesIO برای ارسال به تلگرام
    """

    # بررسی ورودی
    if not chart.get("planets_list") or not chart.get("cusps"):
        logging.warning("⚠️ چارت ورودی ناقص است. هیچ سیاره یا خانه‌ای یافت نشد.")
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.text(0.5, 0.5, "چارت خالی است", ha='center', va='center', fontsize=16)
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        plt.close()
        return buf

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-1.1, 1.1)
    ax.set_aspect('equal')
    ax.axis('off')

    # -------------------------------------------------------------------------
    # رسم دایره اصلی
    # -------------------------------------------------------------------------
    circle = plt.Circle((0, 0), 1.0, color='black', fill=False, linewidth=2)
    ax.add_artist(circle)

    # -------------------------------------------------------------------------
    # رسم برج‌ها
    # -------------------------------------------------------------------------
    for i in range(12):
        start_angle = i * 30
        end_angle = start_angle + 30

        wedge = patches.Wedge(
            center=(0, 0),
            r=1.0,
            theta1=start_angle,
            theta2=end_angle,
            facecolor=SIGN_COLORS[i],
            edgecolor='white',
            linewidth=1
        )
        ax.add_patch(wedge)

        # نام برج فارسی
        angle_rad = math.radians(start_angle + 15)
        x = 0.75 * math.cos(angle_rad)
        y = 0.75 * math.sin(angle_rad)
        ax.text(x, y, SIGNS_FA[i], ha='center', va='center', fontsize=12)

    # -------------------------------------------------------------------------
    # رسم سیارات
    # -------------------------------------------------------------------------
    for planet in chart["planets_list"]:
        deg = planet["degree"]
        symbol = PLANET_SYMBOLS.get(planet["name"], "?")

        angle_rad = math.radians(deg)
        x = 0.55 * math.cos(angle_rad)
        y = 0.55 * math.sin(angle_rad)

        ax.text(x, y, symbol, ha='center', va='center', fontsize=18)

    # -------------------------------------------------------------------------
    # رسم Asc و MC
    # -------------------------------------------------------------------------
    asc = chart.get("ascendant", 0)
    mc = chart.get("mc", 0)

    for label, deg, color in [("ASC", asc, "red"), ("MC", mc, "blue")]:
        angle_rad = math.radians(deg)
        x = 1.05 * math.cos(angle_rad)
        y = 1.05 * math.sin(angle_rad)
        ax.text(x, y, label, ha='center', va='center', fontsize=10, color=color)

    # -------------------------------------------------------------------------
    # خروجی تصویر
    # -------------------------------------------------------------------------
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close()
    return buf
