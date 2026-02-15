# sajil/engine.py

from .models import SajilInput, SajilResult
from .validators import validate_sajil_input
from .numerology import basic_numerology_profile, life_path_number
from .gematria import basic_gematria_profile
from .symbol_mapper import suggest_symbols_by_life_path, filter_existing_symbols


def compute_sajil(data: SajilInput) -> SajilResult:
    # 1) اعتبارسنجی
    validate_sajil_input(data)

    # 2) پروفایل عددشناسی
    num_profile = basic_numerology_profile(data.birth_date)
    lp = int(num_profile["life_path_number"])

    # 3) پروفایل گیمیاتریا
    gem_profile = basic_gematria_profile(data.first_name)

    # 4) پیشنهاد نماد
    symbol_ids = suggest_symbols_by_life_path(lp)
    symbol_ids = filter_existing_symbols(symbol_ids)

    # 5) ساخت خلاصه و جزئیات
    summary = (
        f"سجیل {data.first_name} بر اساس تاریخ تولد {data.birth_date} و عدد مسیر زندگی {lp} محاسبه شد."
    )

    details_lines = [
        f"🔢 عدد مسیر زندگی شما: {num_profile['life_path_number']}",
        f"🧭 تفسیر عددی: {num_profile['life_path_description']}",
        "",
        f"🔡 ارزش گیمیاتریای نام: {gem_profile['name_gematria_value']}",
        f"📜 توضیح: {gem_profile['name_gematria_note']}",
    ]
    details = "\n".join(details_lines)

    meta = {
        "life_path_number": num_profile["life_path_number"],
        "name_gematria_value": gem_profile["name_gematria_value"],
    }

    return SajilResult(
        summary=summary,
        details=details,
        symbols=symbol_ids,
        meta=meta,
    )
