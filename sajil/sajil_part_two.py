# sajil_part_two.py
# =============================================================================
# بخش دوم: پردازش داده‌های سجیل
# -----------------------------------------------------------------------------
# این ماژول منطق اصلی را اجرا می‌کند:
#   - محاسبه مجموع
#   - محاسبه میانگین
#   - تولید تحلیل اولیه
# =============================================================================

import datetime
from typing import List, Dict, Any

def sajil_part_two_process(prepared_data: List[float]) -> Dict[str, Any]:
    """
    ورودی:
        prepared_data → لیست اعداد معتبر
    خروجی:
        result → دیکشنری شامل نتایج پردازش
    """

    if not prepared_data:
        return {"status": "Failure", "message": "هیچ داده‌ای برای پردازش وجود ندارد."}

    total_sum = sum(prepared_data)
    total_count = len(prepared_data)
    average = total_sum / total_count

    return {
        "status": "Success",
        "total_items": total_count,
        "total_sum": total_sum,
        "average_value": average,
        "report_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "generated_symbol": "☿",
        "analysis_summary": (
            "تحلیل اولیه: مجموع ورودی‌های شما ({total_sum}) نشان‌دهنده "
            "تمرکز، نظم و توانایی برنامه‌ریزی مؤثر است."
        )
    }
