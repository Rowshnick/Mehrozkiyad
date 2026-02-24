# astrology_core/Render/draw_zodiac.py

import math
from .chart_renderer import chart_angle
from .theme import get_theme

ZODIAC_SIGNS = [
    "♈", "♉", "♊", "♋", "♌", "♍",
    "♎", "♏", "♐", "♑", "♒", "♓"
]


def draw_zodiac_circle(ax, r_zodiac=0.85, theme_name="dark"):
    theme = get_theme(theme_name)

    circle = ax.add_artist(
        ax.figure.canvas.copy_from_bbox(
            ax.bbox
        )
    )  # فقط برای سازگاری، استفادهٔ اصلی با plot است

    ax.plot(
        [0, 2 * math.pi],
        [r_zodiac, r_zodiac],
        color=theme["zodiac_circle"],
        linewidth=theme["zodiac_ring_width"],
    )


def draw_zodiac_labels(ax, r_zodiac=0.85, theme_name="dark"):
    theme = get_theme(theme_name)

    for i in range(12):
        lon = i * 30 + 15
        theta = chart_angle(lon)
        ax.text(
            theta,
            r_zodiac + 0.04,
            ZODIAC_SIGNS[i],
            ha="center",
            va="center",
            fontsize=theme["zodiac_size"],
            color=theme["zodiac_text"],
            fontname=theme["font"],
        )
