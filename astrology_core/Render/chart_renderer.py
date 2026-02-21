# astrology_core/Render/chart_renderer.py

import math
import matplotlib.pyplot as plt

ZODIAC_SIGNS = [
    "♈", "♉", "♊", "♋", "♌", "♍",
    "♎", "♏", "♐", "♑", "♒", "♓"
]

PLANET_SYMBOLS = {
    "Sun": "☉",
    "Moon": "☽",
    "Mercury": "☿",
    "Venus": "♀",
    "Mars": "♂",
    "Jupiter": "♃",
    "Saturn": "♄",
    "Uranus": "♅",
    "Neptune": "♆",
    "Pluto": "♇",
    "Node": "☊",
    "Lilith": "⚸",
    "Fortune": "⊗",
}

ASPECT_COLORS = {
    "conjunction": "black",
    "opposition": "red",
    "square": "red",
    "trine": "blue",
    "sextile": "blue",
}

MAJOR_ASPECTS = {"conjunction", "opposition", "square", "trine", "sextile"}


def deg_to_rad(deg):
    return math.radians(deg)


def chart_angle(lon):
    """
    تبدیل طول دایرةالبروجی به زاویهٔ روی چارت.
    اینجا 0° = سمت راست (شرق)، خلاف جهت عقربه‌های ساعت.
    """
    return deg_to_rad(90 - lon)


def render_chart(
    chart,
    style="classic",
    show_aspects=True,
    show_houses=True,
    show_points=True,
    dpi=150,
    figsize=(8, 8),
):
    """
    ورودی: خروجی build_chart
    خروجی: matplotlib Figure
    """

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi, subplot_kw={"projection": "polar"})
    ax.set_theta_direction(-1)  # خلاف جهت عقربه‌های ساعت
    ax.set_theta_zero_location("E")  # 0° در شرق (راست)

    # پس‌زمینه
    ax.set_facecolor("white")
    ax.set_xticks([])
    ax.set_yticks([])

    # شعاع‌ها
    r_outer = 1.0
    r_zodiac = 0.85
    r_planets = 0.70
    r_houses = 0.95

    # 1) دایرهٔ زودیاک
    circle = plt.Circle((0, 0), r_zodiac, transform=ax.transData._b, fill=False, color="gray", linewidth=1.0)
    ax.add_artist(circle)

    # 2) نشانه‌ها (Signs)
    for i in range(12):
        lon = i * 30 + 15  # وسط هر نشانه
        theta = chart_angle(lon)
        ax.text(
            theta,
            r_zodiac + 0.03,
            ZODIAC_SIGNS[i],
            ha="center",
            va="center",
            fontsize=14,
        )

    # 3) خانه‌ها (Houses)
    houses = chart.get("houses", {})
    if show_houses and houses:
        for i in range(1, 13):
            cusp = houses.get(f"Cusp{i}")
            if cusp is None:
                continue
            lon = cusp["lon"]
            theta = chart_angle(lon)
            ax.plot([theta, theta], [0, r_houses], color="gray", linewidth=0.6)
            ax.text(
                theta,
                r_houses + 0.02,
                str(i),
                ha="center",
                va="center",
                fontsize=8,
                color="gray",
            )

    # 4) سیارات
    planets = chart.get("planets", {})
    for name, data in planets.items():
        lon = data["lon"]
        theta = chart_angle(lon)

        symbol = PLANET_SYMBOLS.get(name, "•")

        # نقطه
        ax.scatter([theta], [r_planets], color="black", s=10, zorder=5)

        # نماد
        ax.text(
            theta,
            r_planets + 0.05,
            symbol,
            ha="center",
            va="center",
            fontsize=12,
            color="black",
        )

    # 5) نقاط اضافی (Node, Lilith, ...)
    if show_points:
        points = chart.get("points", {})
        for name, data in points.items():
            lon = data["lon"]
            theta = chart_angle(lon)
            symbol = PLANET_SYMBOLS.get(name, "•")

            ax.scatter([theta], [r_planets - 0.08], color="black", s=8, zorder=4)
            ax.text(
                theta,
                r_planets - 0.13,
                symbol,
                ha="center",
                va="center",
                fontsize=10,
                color="black",
            )

    # 6) جنبه‌ها
    if show_aspects:
        aspects = chart.get("aspects", {}).get("planet_aspects", [])
        for asp in aspects:
            a_type = asp["aspect"]
            if a_type not in MAJOR_ASPECTS:
                continue

            p1 = asp["planet1"]
            p2 = asp["planet2"]

            if p1 not in planets or p2 not in planets:
                continue

            lon1 = planets[p1]["lon"]
            lon2 = planets[p2]["lon"]

            theta1 = chart_angle(lon1)
            theta2 = chart_angle(lon2)

            color = ASPECT_COLORS.get(a_type, "black")
            strength = asp.get("strength", 0.5)
            lw = 0.5 + 2.0 * max(0.0, min(1.0, strength))

            ax.plot(
                [theta1, theta2],
                [r_planets, r_planets],
                color=color,
                linewidth=lw,
                alpha=0.8,
                zorder=3,
            )

    ax.set_rlim(0, 1.1)
    plt.tight_layout()
    return fig
