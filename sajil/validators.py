# sajil/validators.py

from typing import List
from datetime import datetime
from .models import SajilInput


class SajilValidationError(Exception):
    def __init__(self, messages: List[str]):
        self.messages = messages
        super().__init__("\n".join(messages))


def validate_sajil_input(data: SajilInput) -> None:
    errors: List[str] = []

    # نام
    if not data.first_name or not data.first_name.strip():
        errors.append("نام نمی‌تواند خالی باشد.")

    # تاریخ تولد
    normalized = data.birth_date.replace("/", "-")
    try:
        _ = datetime.fromisoformat(normalized)
    except Exception:
        errors.append("فرمت تاریخ تولد نامعتبر است. مثال: 1990-08-03 یا 1370-05-12")

    if errors:
        raise SajilValidationError(errors)
