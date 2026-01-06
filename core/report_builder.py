# report_builder.py
# =============================================================================
# ساخت گزارش چندصفحه‌ای ناتال پرو (متن + PDF)
# =============================================================================

from typing import Dict, Any, List
from datetime import datetime

from fpdf import FPDF  # مطمئن شو fpdf2 در requirements هست


# -----------------------------------------------------------------------------
# ۱) ابزارهای کمکی برای متن
# -----------------------------------------------------------------------------

def _safe_get_birth_info(chart_data: Dict[str, Any]) -> Dict[str, str]:
    """
    از chart_data اطلاعات اصلی تولد را استخراج می‌کند.
    اگر چیزی نبود، مقدار پیش‌فرض می‌گذارد.
    """
    meta = chart_data.get("meta", {}) if isinstance(chart_data.get("meta"), dict) else {}

    return {
        "name": meta.get("name", "بدون نام"),
        "jalali_date": meta.get("jalali_date", meta.get("birth_jalali", "نامشخص")),
        "gregorian_date": meta.get("gregorian_date", meta.get("birth_gregorian", "نامشخص")),
        "time": meta.get("time", meta.get("birth_time", "نامشخص")),
        "city": meta.get("city", meta.get("birth_city", "نامشخص")),
        "timezone": meta.get("timezone", "Asia/Tehran"),
    }


def _split_natal_text_by_domain(natal_text: str) -> Dict[str, str]:
    """
    متن تفسیر ناتال را به بخش‌های مجزا تبدیل می‌کند.
    اگر متن ساختار مشخصی نداشت، کل متن در بخش «خلاصهٔ ناتال» قرار می‌گیرد.
    """
    sections: Dict[str, List[str]] = {}
    current = "خلاصه ناتال"

    lines = natal_text.splitlines()
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("🔷"):
            current = stripped.replace("🔷", "").strip()
            sections.setdefault(current, [])
        else:
            sections.setdefault(current, []).append(line)

    return {
        title: "\n".join(content).strip()
        for title, content in sections.items()
        if content
    }
  # -----------------------------------------------------------------------------
# ۲) ساخت متن ساختارمند گزارش ناتال
# -----------------------------------------------------------------------------

def build_natal_report_text(chart_data: Dict[str, Any], natal_text: str) -> str:
    """
    یک متن طولانی، بخش‌بندی‌شده و آمادهٔ PDF برمی‌سازد
    بر اساس:
      - chart_data (برای مشخصات تولد)
      - natal_text (خلاصه/تفسیر ناتال از موتور تفسیر)
    """
    info = _safe_get_birth_info(chart_data)
    sections_parsed = _split_natal_text_by_domain(natal_text)

    name = info["name"]
    jalali_date = info["jalali_date"]
    gregorian_date = info["gregorian_date"]
    time = info["time"]
    city = info["city"]
    timezone = info["timezone"]

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines: List[str] = []

    # -------------------------------------------------------------------------
    # صفحه ۱ – جلد
    # -------------------------------------------------------------------------
    lines.append("گزارش کامل چارت تولد")
    lines.append("======================================")
    lines.append(f"نام: {name}")
    lines.append(f"تاریخ تولد (جلالی): {jalali_date}")
    lines.append(f"تاریخ تولد (میلادی): {gregorian_date}")
    lines.append(f"ساعت تولد: {time}")
    lines.append(f"شهر تولد: {city}")
    lines.append(f"منطقه زمانی: {timezone}")
    lines.append("")
    lines.append(f"زمان تولید گزارش: {now_str}")
    lines.append("")
    lines.append("این گزارش بر اساس داده‌های نجومی چارت تولد شما و قوانین تفسیر حرفه‌ای تهیه شده است.")
    lines.append("\n" + "=" * 40 + "\n")

    # -------------------------------------------------------------------------
    # صفحه ۲ – مقدمه
    # -------------------------------------------------------------------------
    lines.append("۱) مقدمه")
    lines.append("--------------------------------------")
    lines.append("این گزارش یک تحلیل جامع از چارت تولد شماست. هدف آن کمک به شناخت عمیق‌تر خود،")
    lines.append("درک الگوهای رفتاری، شناسایی فرصت‌ها و چالش‌ها و ارائهٔ مسیرهای عملی برای رشد است.")
    lines.append("")
    lines.append("چارت تولد یک نقشهٔ احتمالات است—not سرنوشت قطعی. شما همیشه اختیار دارید.")
    lines.append("\n" + "=" * 40 + "\n")

    # -------------------------------------------------------------------------
    # صفحه ۳ – مشخصات تولد
    # -------------------------------------------------------------------------
    lines.append("۲) مشخصات تولد")
    lines.append("--------------------------------------")
    lines.append(f"- تاریخ تولد (جلالی): {jalali_date}")
    lines.append(f"- تاریخ تولد (میلادی): {gregorian_date}")
    lines.append(f"- ساعت تولد: {time}")
    lines.append(f"- شهر تولد: {city}")
    lines.append(f"- منطقه زمانی: {timezone}")
    lines.append("")
    lines.append("این اطلاعات پایهٔ محاسبهٔ چارت شما هستند.")
    lines.append("\n" + "=" * 40 + "\n")

    # -------------------------------------------------------------------------
    # بخش‌های اصلی (شخصیت، روابط، شغل، چالش‌ها، شانس‌ها)
    # -------------------------------------------------------------------------

    title_map = {
        "شخصیت و هویت": "۳) شخصیت و هویت",
        "روابط عاطفی": "۴) روابط عاطفی",
        "شغل و مسیر زندگی": "۵) شغل و مسیر زندگی",
        "چالش‌های درونی": "۶) چالش‌های درونی",
        "شانس و نقاط طلایی": "۷) شانس‌ها و نقاط طلایی",
    }

    for key, chapter_title in title_map.items():
        content = sections_parsed.get(key)
        if not content:
            continue

        lines.append(chapter_title)
        lines.append("--------------------------------------")
        lines.append(content)
        lines.append("\n" + "=" * 40 + "\n")

    # -------------------------------------------------------------------------
    # بخش‌های اضافی (اگر متن ناتال بخش‌های دیگری داشت)
    # -------------------------------------------------------------------------
    for other_title, content in sections_parsed.items():
        if other_title in title_map:
            continue
        lines.append(f"{other_title}")
        lines.append("--------------------------------------")
        lines.append(content)
        lines.append("\n" + "=" * 40 + "\n")

    # -------------------------------------------------------------------------
    # چک‌لیست ۳۰ روزه
    # -------------------------------------------------------------------------
    lines.append("۸) چک‌لیست عملی ۳۰ روزه")
    lines.append("--------------------------------------")
    lines.append("این چک‌لیست برای فعال‌سازی انرژی‌های مثبت چارت شما طراحی شده است:")
    lines.append("")
    lines.append("• هر روز ۵ دقیقه نوشتن احساسات و افکار.")
    lines.append("• یک تصمیم مهم را با تأمل و مشورت بگیر، نه با عجله.")
    lines.append("• یک گفت‌وگوی صادقانه با یک فرد مهم.")
    lines.append("• یک قدم کوچک در مسیر استعدادهای خلاقانه.")
    lines.append("• یک ساعت تنهایی در هفته برای خودآگاهی.")
    lines.append("\n" + "=" * 40 + "\n")

    # -------------------------------------------------------------------------
    # جمع‌بندی نهایی
    # -------------------------------------------------------------------------
    lines.append("۹) جمع‌بندی نهایی")
    lines.append("--------------------------------------")
    lines.append("چارت تولد تو ترکیبی از استعدادها، چالش‌ها و فرصت‌هاست. ")
    lines.append("این گزارش به تو کمک می‌کند مسیرهای پررنگ‌تر زندگی‌ات را ببینی و آگاهانه‌تر انتخاب کنی.")
    lines.append("")
    lines.append("به یاد داشته باش: چارت تو «سرنوشت» نیست؛ «نقشه» است.")
    lines.append("این تو هستی که انتخاب می‌کنی چگونه از این نقشه استفاده کنی.")
    lines.append("\n" + "=" * 40 + "\n")

    return "\n".join(lines)
  # -----------------------------------------------------------------------------
# ۳) ساخت PDF از متن گزارش
# -----------------------------------------------------------------------------

class PDF(FPDF):
    """
    یک کلاس ساده PDF با پشتیبانی از فونت فارسی.
    توجه: باید فونت فارسی (مثل Vazirmatn) را در مسیر پروژه قرار دهی.
    """
    def header(self):
        self.set_font("Vazir", size=10)
        self.cell(0, 10, txt="گزارش چارت تولد", ln=1, align="C")
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font("Vazir", size=8)
        page_num = f"صفحه {self.page_no()}"
        self.cell(0, 10, txt=page_num, align="C")


def _init_pdf() -> PDF:
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # اضافه‌کردن فونت فارسی
    try:
        pdf.add_font("Vazir", "", "/app/fonts/Vazirmatn-Regular.ttf", uni=True)
    except Exception:
        # اگر فونت پیدا نشد، از فونت پیش‌فرض استفاده می‌کنیم
        pass

    pdf.set_font("Vazir", size=12)
    return pdf


def build_natal_pdf_report(chart_data: Dict[str, Any], natal_text: str) -> bytes:
    """
    از chart_data و متن تفسیر ناتال، یک PDF چندصفحه‌ای تولید می‌کند و
    آن را به‌صورت bytes برمی‌گرداند (برای ارسال به تلگرام).
    """
    report_text = build_natal_report_text(chart_data, natal_text)
    pdf = _init_pdf()

    pdf.add_page()

    # چاپ متن فارسی با multi_cell
    for line in report_text.split("\n"):
        pdf.multi_cell(0, 8, txt=line)

    # خروجی PDF به bytes
    pdf_bytes = pdf.output(dest="S").encode("latin1", "ignore")
    return pdf_bytes
  
