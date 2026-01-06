# sajil_part_one.py
# =============================================================================
# بخش اول: اعتبارسنجی ورودی‌های سجیل
# -----------------------------------------------------------------------------
# این ماژول فقط یک کار انجام می‌دهد:
#   - ورودی کاربر را بررسی و به لیست اعداد ممیز شناور تبدیل می‌کند.
# =============================================================================

from typing import List, Tuple, Optional

def sajil_part_one_validate(input_list: List[str]) -> Tuple[List[float], Optional[str]]:
    """
    ورودی:
        input_list → لیستی از رشته‌ها (ورودی خام کاربر)
    خروجی:
        (clean_data, error_message)
    """

    clean_data = []

    if not input_list:
        return [], "لطفاً حداقل یک عدد وارد کنید."

    for index, item in enumerate(input_list):
        try:
            clean_data.append(float(item))
        except (ValueError, TypeError):
            return [], f"داده نامعتبر در ورودی {index+1}: '{item}'. تمام ورودی‌ها باید عدد باشند."

    return clean_data, None
