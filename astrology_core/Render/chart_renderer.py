# ============================================================
#  CHART RENDERER (THEME-DRIVEN VERSION)
#  Fully rewritten for Roshina Project
# ============================================================

# astrology_core/Render/chart_renderer.py

import math
import matplotlib.pyplot as plt

from .theme import get_theme
from .draw_zodiac import draw_zodiac_circle, draw_zodiac_labels
from .draw_houses import draw_houses
from .draw_planets import draw_planets
from .draw_aspects import draw_aspects


def deg_to_rad(deg):
    return math.radians(deg)


def chart_angle(lon):
    return deg_to_rad(90 - lon)


def render_chart(
    chart,
    theme="dark",
    show_aspects=True,
    show_houses=True,
    show_points=True,
    dpi=150,
    figsize=(8, 8),
):
    theme_dict = get_theme(theme)

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi, subplot_kw={"projection": "polar"})
    ax.set_theta_direction(-1)
    ax.set_theta_zero_location("E")
    ax.set_facecolor(theme_dict["background"])
    ax.set_xticks([])
    ax.set_yticks([])

    r_zodiac = 0.85
    r_planets = 0.70
    r_houses = 0.95

    # زودیاک
    draw_zodiac_circle(ax, r_zodiac=r_zodiac, theme_name=theme)
    draw_zodiac_labels(ax, r_zodiac=r_zodiac, theme_name=theme)

    # خانه‌ها
    draw_houses(ax, chart, r_houses=r_houses, theme_name=theme, show_houses=show_houses)

    # سیارات و نقاط
    draw_planets(ax, chart, r_planets=r_planets, theme_name=theme, show_points=show_points)

    # جنبه‌ها
    draw_aspects(ax, chart, r_planets=r_planets, theme_name=theme, show_aspects=show_aspects)

    ax.set_rlim(0, 1.1)
    plt.tight_layout()
    return fig
