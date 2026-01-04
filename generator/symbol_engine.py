"""
symbol_engine.py
موتور هوشمند انتخاب نماد بر اساس هدف، فرهنگ، انرژی و تنظیمات پیشرفته.

این موتور:
- از library.SYMBOLS استفاده می‌کند
- برای هر نماد امتیاز محاسبه می‌کند
- بهترین نمادها را بر اساس امتیاز + مقدار تصادف کنترل‌شده برمی‌گزیند
"""

from __future__ import annotations

from typing import List, Dict, Any, Optional
import random

from library.library import SYMBOLS


# ==========================
#   تنظیمات و ثابت‌ها
# ==========================

# وزن‌های پایه برای امتیازدهی
WEIGHT_GOAL_MATCH = 5.0          # نمادهایی که goal را در uses دارند
WEIGHT_ENERGY_MATCH = 2.5        # هر تطابق انرژی
WEIGHT_PRIMARY_CULTURE = 3.0     # فرهنگ اصلی انتخاب‌شده توسط کاربر
WEIGHT_SECONDARY_CULTURE = 1.5   # فرهنگ‌های ترجیحی ثانویه
WEIGHT_GLOBAL_ARCHETYPE = 2.0    # نمادهای GLOBAL_ARCHETYPES
WEIGHT_DIVERSITY_PENALTY = -1.0  # جریمهٔ تکرار زیاد یک فرهنگ

# شدت تصادفی بودن (۰ = کاملاً منطقی، ۱ = خیلی رندوم)
DEFAULT_RANDOMNESS = 0.3


# ==========================
#   توابع کمکی
# ==========================

def _is_global_archetype(symbol: Dict[str, Any]) -> bool:
    """
    تشخیص اینکه آیا نماد از دستهٔ آرکتایپ‌های جهانی است یا نه.
    بر اساس culture = "جهانی" و نام دسته در ساختار فعلی.
    """
    return symbol.get("culture", "").strip() == "جهانی"


def _score_symbol(
    symbol: Dict[str, Any],
    goal: str,
    primary_culture: Optional[str],
    preferred_cultures: Optional[List[str]],
    energies: Optional[List[str]],
    culture_counts: Dict[str, int],
) -> float:
    """
    محاسبهٔ امتیاز پایه برای یک نماد.
    """
    score = 0.0

    uses = symbol.get("uses", []) or []
    energy_list = symbol.get("energy", []) or []
    culture = (symbol.get("culture") or "").lower()

    # ۱) تطابق goal
    if goal and goal in uses:
        score += WEIGHT_GOAL_MATCH

    # ۲) تطابق انرژی‌ها
    if energies:
        for e in energies:
            if e in energy_list:
                score += WEIGHT_ENERGY_MATCH

    # ۳) فرهنگ اصلی
    if primary_culture:
        pc = primary_culture.lower()
        if culture.startswith(pc) or pc in culture:
            score += WEIGHT_PRIMARY_CULTURE

    # ۴) فرهنگ‌های ترجیحی ثانویه
    if preferred_cultures:
        for c in preferred_cultures:
            cl = c.lower()
            if cl and (culture.startswith(cl) or cl in culture):
                score += WEIGHT_SECONDARY_CULTURE
                break

    # ۵) آرکتایپ‌های جهانی
    if _is_global_archetype(symbol):
        score += WEIGHT_GLOBAL_ARCHETYPE

    # ۶) جریمهٔ تکرار یک فرهنگ برای تنوع
    if culture:
        count = culture_counts.get(culture, 0)
        if count > 0:
            score += WEIGHT_DIVERSITY_PENALTY * count

    return score


def _apply_randomness(score: float, randomness: float) -> float:
    """
    افزودن نویز تصادفی کنترل‌شده به امتیاز.
    randomness بین ۰ و ۱ است.
    """
    if randomness <= 0:
        return score
    noise = random.uniform(-1.0, 1.0) * randomness * score
    return score + noise


# ==========================
#   اینترفیس عمومی موتور
# ==========================

def select_symbols(
    goal: str,
    count: int = 1,
    primary_culture: Optional[str] = None,
    preferred_cultures: Optional[List[str]] = None,
    energies: Optional[List[str]] = None,
    randomness: float = DEFAULT_RANDOMNESS,
    exclude_ids: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    موتور پیشرفتهٔ انتخاب نماد.

    پارامترها:
    - goal: هدف اصلی (مثلاً "wealth" / "love" / "protection" / "calm" / "success" / "spiritual" / "general")
    - count: تعداد نماد خروجی
    - primary_culture: فرهنگ اصلی ترجیحی (مثلاً "ایران", "چین", "هند", "egyptian", "iran", "chinese")
    - preferred_cultures: لیستی از فرهنگ‌های ثانویهٔ ترجیحی
    - energies: لیستی از انرژی‌های موردنظر (مثلاً ["آرامش", "رشد", "قدرت"])
    - randomness: شدت تصادفی بودن (۰ تا ۱)
    - exclude_ids: لیست کلیدهایی که نباید انتخاب شوند

    خروجی:
    - لیستی از دیکشنری نمادها (هر نماد همان ساختاری را دارد که در library تعریف شده)
    """

    if count <= 0:
        return []

    exclude_ids = set(exclude_ids or [])

    # ۱) فیلتر اولیه: فقط نمادهایی که با goal مرتبط‌اند
    candidates: Dict[str, Dict[str, Any]] = {
        k: v for k, v in SYMBOLS.items()
        if (goal in (v.get("uses") or [])) and (k not in exclude_ids)
    }

    # اگر هیچ نمادی دقیقاً با goal نبود → fallback به همهٔ نمادها به‌جز exclude
    if not candidates:
        candidates = {k: v for k, v in SYMBOLS.items() if k not in exclude_ids}

    if not candidates:
        return []

    # ۲) شمارش فرهنگ‌ها برای تنوع
    culture_counts: Dict[str, int] = {}
    for v in candidates.values():
        culture = (v.get("culture") or "").lower()
        if culture:
            culture_counts[culture] = 0

    # ۳) امتیازدهی + تصادف کنترل‌شده
    scored: List[tuple[str, float]] = []

    for key, symbol in candidates.items():
        base_score = _score_symbol(
            symbol=symbol,
            goal=goal,
            primary_culture=primary_culture,
            preferred_cultures=preferred_cultures,
            energies=energies,
            culture_counts=culture_counts,
        )
        final_score = _apply_randomness(base_score, randomness)

        scored.append((key, final_score))

    # ۴) مرتب‌سازی بر اساس امتیاز نهایی
    scored.sort(key=lambda x: x[1], reverse=True)

    # ۵) انتخاب نمادهای برتر + به‌روزرسانی شمارش فرهنگ‌ها برای تنوع
    selected: List[Dict[str, Any]] = []
    used_cultures: Dict[str, int] = {}

    for key, score in scored:
        if len(selected) >= count:
            break
        symbol = candidates[key]
        culture = (symbol.get("culture") or "").lower()

        # تنوع: اگر از یک فرهنگ خیلی برداشته شده، می‌توانی اینجا محدود کنی (در صورت تمایل)
        # فعلاً فقط می‌شماریم:
        if culture:
            used_cultures[culture] = used_cultures.get(culture, 0) + 1

        selected.append(symbol)

    return selected


# ==========================
#   نسخهٔ ساده‌تر برای استفادهٔ سریع
# ==========================

def get_symbols_simple(
    goal: str,
    count: int = 1,
    culture: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    این تابع نسخهٔ ساده‌شدهٔ موتور است:
    فقط goal و culture می‌گیرد و count نماد برتر را برمی‌گرداند.
    """
    return select_symbols(
        goal=goal,
        count=count,
        primary_culture=culture,
        preferred_cultures=None,
        energies=None,
        randomness=DEFAULT_RANDOMNESS,
        exclude_ids=None,
    )
