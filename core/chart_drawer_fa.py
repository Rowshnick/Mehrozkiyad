# chart_drawer_fa.py
# =============================================================================
# ترسیم چارت نجومی فارسی با matplotlib (نسخهٔ اصلاح‌شده و حرفه‌ای)
# شامل:
# - برج‌ها
# - خانه‌ها
# - سیارات + درجه + ℞
# - زوایا (Aspects)
# - فونت فارسی Vazirmatn + fallback نمادها
# =============================================================================

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.font_manager as fm
import io
import logging
import math
from typing import Dict, Any, List, Optional

import arabic_reshaper
from bidi.algorithm import get_display

# -----------------------------------------------------------------------------
# ۱) مسیر فونت فارسی
# -----------------------------------------------------------------------------

FA_FONT_PATH = "fonts/Vazirmatn-Regular.ttf"

def fa_text(text: str) -> str:
    """شکل‌دهی و جهت‌دهی متن فارسی برای نمایش صحیح در matplotlib."""
    if not text:
        return ""
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)

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
# ۲) رنگ‌ها و نمادها
# -----------------------------------------------------------------------------

SIGN_COLORS = [
    "#f8c8dc", "#f8e0c8", "#f8f8c8", "#d0f8c8",
    "#c8f8f8", "#c8d0f8", "#e0c8f8", "#f8c8f0",
    "#f0c8c8", "#d8d8d8", "#c8f0e0", "#e0f8c8"
]

HOUSE_LINE_COLOR = "#666666"

ASPECT_COLORS = {
    "Conjunction": "#ff9800",
    "Sextile":     "#4caf50",
    "Square":      "#f44336",
    "Trine":       "#2196f3",
    "Opposition":  "#9c27b0",
}

PLANET_SYMBOLS = {
    "sun": "☉", "moon": "☽", "mercury": "☿", "venus": "♀", "mars": "♂",
    "jupiter": "♃", "saturn": "♄", "uranus": "♅", "neptune": "♆", "pluto": "♇",
    "true_node": "☊", "chiron": "⚷", "lilith": "⚸"
}

PLANET_NAMES_FA = {
    "sun": "خورشید",
    "moon": "ماه",
    "mercury": "عطارد",
    "venus": "زهره",
    "mars": "مریخ",
    "jupiter": "مشتری",
    "saturn": "زحل",
    "uranus": "اورانوس",
    "neptune": "نپتون",
    "pluto": "پلوتو",
    "true_node": "گره شمالی",
    "chiron": "کیرون",
    "lilith": "لیلـیت",
}

SIGNS_FA = [
    "حمل", "ثور", "جوزا", "سرطان", "اسد", "سنبله",
    "میزان", "عقرب", "قوس", "جدی", "دلو", "حوت"
]

# -----------------------------------------------------------------------------
# تبدیل درجه به مختصات
# -----------------------------------------------------------------------------

def polar_to_cartesian(deg: float, radius: float) -> (float, float):
    angle_rad = math.radians(deg - 90)
    return radius * math.cos(angle_rad), radius * math.sin(angle_rad)

# -----------------------------------------------------------------------------
# تابع اصلی: رسم چارت
# -----------------------------------------------------------------------------

def draw_chart_advanced_fa(chart: Dict[str, Any]) -> io.BytesIO:
    planets: List[Dict[str, Any]] = chart.get("planets_list") or []
    cusps: List[float] = chart.get("cusps") or []

    if not planets or len(cusps) != 12:
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.axis('off')
        ax.text(0.5, 0.5, fa_text("چارت ناقص است"), ha='center', va='center', fontsize=16)
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        plt.close()
        return buf

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.2, 1.2)
    ax.set_aspect('equal')
    ax.axis('off')

    outer_r = 1.0
    inner_r = 0.6
    house_r = 0.9
    planet_r = 0.7

    # -----------------------------
    # برج‌ها
    # -----------------------------
    for i in range(12):
        start_angle = i * 30
        end_angle = start_angle + 30

        wedge = patches.Wedge(
            center=(0, 0),
            r=outer_r,
            theta1=start_angle,
            theta2=end_angle,
            facecolor=SIGN_COLORS[i],
            edgecolor='white',
            linewidth=1
        )
        ax.add_patch(wedge)

        mid_deg = start_angle + 15
        x, y = polar_to_cartesian(mid_deg, (outer_r + inner_r) / 2)
        ax.text(x, y, fa_text(SIGNS_FA[i]), ha='center', va='center', fontsize=11)

    # -----------------------------
    # خانه‌ها
    # -----------------------------
    for i, cusp_deg in enumerate(cusps):
        x1, y1 = polar_to_cartesian(cusp_deg, inner_r)
        x2, y2 = polar_to_cartesian(cusp_deg, outer_r)
        ax.plot([x1, x2], [y1, y2], color=HOUSE_LINE_COLOR, linewidth=1)

        next_cusp = cusps[(i + 1) % 12]
        mid_deg = (cusp_deg + ((next_cusp - cusp_deg) % 360) / 2) % 360
        tx, ty = polar_to_cartesian(mid_deg, house_r)
        ax.text(tx, ty, str(i + 1), ha='center', va='center', fontsize=10)

    # -----------------------------
    # سیارات
    # -----------------------------
    planet_positions = {}

    for planet in planets:
        name = planet.get("name", "")
        deg = float(planet.get("degree", 0.0))
        symbol = PLANET_SYMBOLS.get(name, "?")
        is_retro = planet.get("retrograde", False)

        px, py = polar_to_cartesian(deg, planet_r)
        ax.text(px, py, symbol, ha='center', va='center', fontsize=16)

        sign_deg = float(planet.get("sign_degree", deg % 30))
        dx, dy = polar_to_cartesian(deg, planet_r - 0.08)
        ax.text(dx, dy, f"{int(sign_deg):02d}°", ha='center', va='center', fontsize=8)

        if is_retro:
            rx, ry = polar_to_cartesian(deg, planet_r + 0.06)
            ax.text(rx, ry, "℞", ha='center', va='center', fontsize=9, color="#d32f2f")

        planet_positions[name] = polar_to_cartesian(deg, planet_r - 0.02)

    # -----------------------------
    # ASC / MC
    # -----------------------------
    asc = float(chart.get("ascendant", 0.0))
    mc = float(chart.get("mc", 0.0))

    for label, deg, color in [("ASC", asc, "#d32f2f"), ("MC", mc, "#1976d2")]:
        tx, ty = polar_to_cartesian(deg, outer_r + 0.05)
        ax.text(tx, ty, label, ha='center', va='center', fontsize=10, color=color)

    # -----------------------------
    # زوایا (Aspects)
    # -----------------------------
    aspects: Optional[List[Dict[str, Any]]] = chart.get("aspects")
    if aspects:
        for asp in aspects:
            p1 = asp.get("p1")
            p2 = asp.get("p2")
            asp_name = asp.get("aspect")

            if p1 not in planet_positions or p2 not in planet_positions:
                continue

            x1, y1 = planet_positions[p1]
            x2, y2 = planet_positions[p2]

            color = ASPECT_COLORS.get(asp_name, "#888888")
            ax.plot([x1, x2], [y1, y2], color=color, linewidth=1)

    # -----------------------------
    # لیست فارسی توضیحات کنار چارت
    # -----------------------------
    info_y = 1.05
    for planet in planets:
        name = planet.get("name", "")
        sign = planet.get("sign", "")
        sign_deg = int(round(float(planet.get("sign_degree", 0.0))))
        house_name = planet.get("house_name", "")
        is_retro = planet.get("retrograde", False)

        name_fa = PLANET_NAMES_FA.get(name, name)
        txt = f"{name_fa} در {sign} {sign_deg}°، {house_name}"
        if is_retro:
            txt += " (عقب‌گرد)"

        info_y -= 0.06
        ax.text(
            1.25, info_y,
            fa_text(txt),
            fontsize=8,
            ha='right',
            va='center',
            transform=ax.transAxes
        )

    # -----------------------------
    # خروجی نهایی
    # -----------------------------
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=200)
    buf.seek(0)
    plt.close()
    return buf
