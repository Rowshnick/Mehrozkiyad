# ============================================================
#  PUBLIC API LAYER (LAYER 4)
#  AstroChart high-level interface for Roshina Project
# ============================================================

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

# لایه ۳ – رندر و انیمیشن
from .Render.advanced_renderer import (
    render_chart_pretty,
    animate_transits as _animate_transits_impl,
)

# تلاش برای وصل شدن به موتور محاسبات (اگر موجود باشد)
try:
    # این مسیر را می‌توانی با ساختار واقعی پروژه‌ات تنظیم کنی
    from .Core.chart_engine import build_chart as _build_chart_impl
except Exception:
    _build_chart_impl = None


ChartDict = Dict[str, Any]


@dataclass
class AstroChart:
    """
    High-level chart object for rendering, saving, and animating charts.

    self.chart باید همان ساختاری را داشته باشد که لایه ۳ (advanced_renderer)
    انتظار دارد: شامل keys مثل "planets", "houses", "aspects", "points", ...
    """
    chart: ChartDict

    # --------------------------------------------------------
    #  ساخت نمونه از چارت آماده (dict)
    # --------------------------------------------------------
    @classmethod
    def from_chart_dict(cls, chart_data: ChartDict) -> "AstroChart":
        """
        ساخت AstroChart از یک دیکشنری چارت آماده.
        این دیکشنری می‌تواند خروجی مستقیم موتور محاسبات تو باشد.
        """
        return cls(chart=chart_data)

    # --------------------------------------------------------
    #  ساخت نمونه از داده‌های تولد (در صورت وجود موتور محاسبات)
    # --------------------------------------------------------
    @classmethod
    def from_birth(
        cls,
        year: int,
        month: int,
        day: int,
        hour: int,
        minute: int,
        lat: float,
        lon: float,
        tz_offset: float = 0.0,
        **engine_kwargs: Any,
    ) -> "AstroChart":
        """
        ساخت چارت از داده‌های تولد.
        این متد به تابع build_chart در موتور محاسبات وابسته است.
        اگر _build_chart_impl تعریف نشده باشد، خطا می‌دهد تا خودت مسیر را تنظیم کنی.
        """
        if _build_chart_impl is None:
            raise RuntimeError(
                "build_chart (موتور محاسبات) در دسترس نیست. "
                "لطفاً import مربوط به آن را در api.py تنظیم کن."
            )

        chart_data = _build_chart_impl(
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            lat=lat,
            lon=lon,
            tz_offset=tz_offset,
            **engine_kwargs,
        )
        return cls(chart=chart_data)

    # --------------------------------------------------------
    #  رندر چارت (خروجی matplotlib Figure)
    # --------------------------------------------------------
    def render(
        self,
        theme: str = "dark",
        show_aspects: bool = True,
        show_houses: bool = True,
        show_points: bool = True,
        dpi: int = 200,
        figsize: tuple = (8, 8),
        save_as: Optional[str] = None,
        save_dir: str = "/content",
        save_name: str = "chart",
    ):
        """
        رندر چارت با استفاده از رندرر پیشرفته (لایه ۳).

        اگر save_as مقدار داشته باشد (مثلاً 'png' یا 'pdf')،
        خروجی مستقیماً ذخیره می‌شود.
        """
        fig = render_chart_pretty(
            self.chart,
            theme=theme,
            show_aspects=show_aspects,
            show_houses=show_houses,
            show_points=show_points,
            dpi=dpi,
            figsize=figsize,
            save_as=save_as,
            save_dir=save_dir,
            save_name=save_name,
        )
        return fig

    # --------------------------------------------------------
    #  ذخیره چارت (wrapper ساده روی render)
    # --------------------------------------------------------
    def save(
        self,
        format: str = "png",
        filename: str = "chart_output",
        directory: str = "/content",
        theme: str = "dark",
        show_aspects: bool = True,
        show_houses: bool = True,
        show_points: bool = True,
        dpi: int = 200,
        figsize: tuple = (8, 8),
    ) -> str:
        """
        ذخیره چارت در قالب دلخواه (png, pdf, svg, ...).

        در واقع یک wrapper روی render است که پارامتر save_as را تنظیم می‌کند.
        """
        fig = self.render(
            theme=theme,
            show_aspects=show_aspects,
            show_houses=show_houses,
            show_points=show_points,
            dpi=dpi,
            figsize=figsize,
            save_as=format,
            save_dir=directory,
            save_name=filename,
        )
        # مسیر فایل در advanced_renderer برمی‌گردد، اما اینجا fig را هم داریم.
        # اگر خواستی، می‌توانیم بعداً این متد را طوری تغییر دهیم که مسیر را
        # از خود save_chart برگرداند.
        return f"{directory}/{filename}.{format}"

    # --------------------------------------------------------
    #  انیمیشن ترانزیت‌ها
    # --------------------------------------------------------
    def animate_transits(
        self,
        transit_charts: List[ChartDict],
        theme: str = "dark",
        dpi: int = 150,
        figsize: tuple = (8, 8),
        interval: int = 200,
    ):
        """
        ساخت انیمیشن ترانزیت‌ها روی چارت ناتال فعلی.

        transit_charts باید لیستی از چارت‌ها با ساختار مشابه self.chart["planets"] باشد.
        """
        fig, anim = _animate_transits_impl(
            natal_chart=self.chart,
            transit_charts=transit_charts,
            theme=theme,
            dpi=dpi,
            figsize=figsize,
            interval=interval,
        )
        return fig, anim


# ------------------------------------------------------------
#  توابع سطح بالا (Functional API) – اختیاری
# ------------------------------------------------------------

def render_chart_api(
    chart_data: ChartDict,
    theme: str = "dark",
    show_aspects: bool = True,
    show_houses: bool = True,
    show_points: bool = True,
    dpi: int = 200,
    figsize: tuple = (8, 8),
    save_as: Optional[str] = None,
    save_dir: str = "/content",
    save_name: str = "chart",
):
    """
    رندر سریع بدون ساختن AstroChart به‌صورت کلاس.
    """
    chart = AstroChart.from_chart_dict(chart_data)
    return chart.render(
        theme=theme,
        show_aspects=show_aspects,
        show_houses=show_houses,
        show_points=show_points,
        dpi=dpi,
        figsize=figsize,
        save_as=save_as,
        save_dir=save_dir,
        save_name=save_name,
    )


def animate_transits_api(
    natal_chart_data: ChartDict,
    transit_charts: List[ChartDict],
    theme: str = "dark",
    dpi: int = 150,
    figsize: tuple = (8, 8),
    interval: int = 200,
):
    """
    انیمیشن سریع ترانزیت‌ها بدون ساختن AstroChart به‌صورت کلاس.
    """
    chart = AstroChart.from_chart_dict(natal_chart_data)
    return chart.animate_transits(
        transit_charts=transit_charts,
        theme=theme,
        dpi=dpi,
        figsize=figsize,
        interval=interval,
    )
