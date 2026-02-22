# astrology_core/Render/advanced_renderer.py

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
    "conjunction": "#333333",
    "opposition": "#e74c3c",
    "square": "#e74c3c",
    "trine": "#3498db",
    "sextile": "#3498db",
}

MAJOR_ASPECTS = {"conjunction", "opposition", "square", "trine", "sextile"}


def deg_to_rad(deg):
    return math.radians(deg)


def chart_angle(lon):
    return deg_to_rad(90 - lon)


def normalize_houses(houses_raw):
    if isinstance(houses_raw, list):
        return {f"Cusp{i+1}": {"lon": houses_raw[i]} for i in range(len(houses_raw))}
    return houses_raw or {}


def normalize_aspects(aspects_raw):
    if isinstance(aspects_raw, list):
        return {"planet_aspects": aspects_raw}
    if isinstance(aspects_raw, dict):
        return aspects_raw
    return {"planet_aspects": []}


def render_chart_pretty(
    chart,
    show_aspects=True,
    show_houses=True,
    show_points=True,
    dpi=200,
    figsize=(8, 8),
    save_as=None,        # ← NEW
    save_dir="/content", # ← NEW
    save_name="chart",   # ← NEW
):

    fig, ax = plt.subplots(
        figsize=figsize,
        dpi=dpi,
        subplot_kw={"projection": "polar"}
    )

    ax.set_theta_direction(-1)
    ax.set_theta_zero_location("E")
    ax.set_facecolor("#fafafa")
    ax.set_xticks([])
    ax.set_yticks([])

    r_zodiac = 0.85
    r_planets = 0.70
    r_houses = 0.95

    # دایره زودیاک
    circle = plt.Circle(
        (0, 0),
        r_zodiac,
        transform=ax.transData._b,
        fill=False,
        color="#555555",
        linewidth=1.2,
    )
    ax.add_artist(circle)

    # نشانه‌های زودیاک
    for i in range(12):
        lon = i * 30 + 15
        theta = chart_angle(lon)
        ax.text(
            theta,
            r_zodiac + 0.04,
            ZODIAC_SIGNS[i],
            ha="center",
            va="center",
            fontsize=16,
            color="#333333",
        )

    # خانه‌ها
    houses = normalize_houses(chart.get("houses"))
    if show_houses and houses:
        for i in range(1, 13):
            cusp = houses.get(f"Cusp{i}")
            if not cusp:
                continue
            lon = cusp["lon"]
            theta = chart_angle(lon)
            ax.plot(
                [theta, theta],
                [0, r_houses],
                color="#bbbbbb",
                linewidth=0.8,
                zorder=1,
            )
            ax.text(
                theta,
                r_houses + 0.02,
                str(i),
                ha="center",
                va="center",
                fontsize=9,
                color="#777777",
            )

    # سیارات
    planets = chart.get("planets", {})
    for name, data in planets.items():
        lon = data["lon"]
        theta = chart_angle(lon)
        symbol = PLANET_SYMBOLS.get(name, "•")

        ax.scatter(
            [theta],
            [r_planets],
            color="#111111",
            s=18,
            zorder=5,
        )
        ax.text(
            theta,
            r_planets + 0.05,
            symbol,
            ha="center",
            va="center",
            fontsize=13,
            color="#111111",
        )

    # نقاط اضافی
    if show_points:
        points = chart.get("points", {})
        for name, data in points.items():
            lon = data["lon"]
            theta = chart_angle(lon)
            symbol = PLANET_SYMBOLS.get(name, "•")
            ax.scatter([theta], [r_planets - 0.08], color="#444444", s=12, zorder=4)
            ax.text(
                theta,
                r_planets - 0.13,
                symbol,
                ha="center",
                va="center",
                fontsize=11,
                color="#444444",
            )

    # جنبه‌ها
    if show_aspects:
        aspects = normalize_aspects(chart.get("aspects"))
        for asp in aspects.get("planet_aspects", []):
            a_type = asp.get("aspect")
            if a_type not in MAJOR_ASPECTS:
                continue

            p1 = asp.get("planet1")
            p2 = asp.get("planet2")
            if p1 not in planets or p2 not in planets:
                continue

            lon1 = planets[p1]["lon"]
            lon2 = planets[p2]["lon"]
            theta1 = chart_angle(lon1)
            theta2 = chart_angle(lon2)

            color = ASPECT_COLORS.get(a_type, "#333333")
            strength = asp.get("strength", 0.5)
            lw = 0.6 + 2.0 * max(0.0, min(1.0, strength))

            ax.plot(
                [theta1, theta2],
                [r_planets, r_planets],
                color=color,
                linewidth=lw,
                alpha=0.85,
                zorder=3,
            )

    ax.set_rlim(0, 1.1)
    plt.tight_layout()
    return fig


# ساخت انیمیشن  advanced_renderer.py

from matplotlib.animation import FuncAnimation

def animate_transits(
    natal_chart,
    transit_charts,
    dpi=150,
    figsize=(8, 8),
    interval=200,  # میلی‌ثانیه بین فریم‌ها
):
    """
    natal_chart: چارت ناتال (خروجی build_chart)
    transit_charts: لیستی از چارت‌های ترانزیت (همان ساختار build_chart)
    """

    fig = render_chart_pretty(natal_chart, show_aspects=False)
    ax = fig.axes[0]

    r_planets_transit = 0.55

    # آماده‌سازی لایهٔ ترانزیت
    transit_scat = ax.scatter([], [], color="#d35400", s=18, zorder=6)
    transit_texts = []

    def init():
        transit_scat.set_offsets([])
        for txt in transit_texts:
            txt.remove()
        transit_texts.clear()
        return [transit_scat]

    def update(frame_idx):
        chart_tr = transit_charts[frame_idx]
        planets_tr = chart_tr.get("planets", {})

        thetas = []
        rs = []
        for name, data in planets_tr.items():
            lon = data["lon"]
            theta = chart_angle(lon)
            thetas.append(theta)
            rs.append(r_planets_transit)

        # تبدیل به مختصات کارتزین برای scatter
        xs = [r * math.cos(t) for r, t in zip(rs, thetas)]
        ys = [r * math.sin(t) for r, t in zip(rs, thetas)]
        offsets = list(zip(xs, ys))
        transit_scat.set_offsets(offsets)

        # متن‌ها را پاک و دوباره بساز
        for txt in transit_texts:
            txt.remove()
        transit_texts.clear()

        for (name, data), theta in zip(planets_tr.items(), thetas):
            symbol = PLANET_SYMBOLS.get(name, "•")
            txt = ax.text(
                theta,
                r_planets_transit + 0.05,
                symbol,
                ha="center",
                va="center",
                fontsize=11,
                color="#d35400",
                zorder=7,
            )
            transit_texts.append(txt)

        return [transit_scat] + transit_texts

    anim = FuncAnimation(
        fig,
        update,
        frames=len(transit_charts),
        init_func=init,
        blit=False,
        interval=interval,
        repeat=True,
    )

    return fig, anim

# ذخیره فایل 
import os

def save_chart(
    fig,
    filename="chart_output",
    directory="/content",
    format="png",
    dpi=300
):
    """
    ذخیرهٔ چارت با فرمت دلخواه
    format: png, pdf, svg, jpg, eps
    """

    # اطمینان از وجود پوشه
    os.makedirs(directory, exist_ok=True)

    # ساخت مسیر کامل
    filepath = os.path.join(directory, f"{filename}.{format}")

    # ذخیره
    fig.savefig(filepath, format=format, dpi=dpi)

    return filepath

