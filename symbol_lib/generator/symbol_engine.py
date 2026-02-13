"""
symbol_engine.py
موتور هوشمند و پیشرفته انتخاب نماد بر اساس:
- هدف (goal)
- فرهنگ اصلی و ثانویه
- انرژی‌ها
- وزن‌دهی پویا
- کنترل تنوع فرهنگی
- تصادفی‌سازی کنترل‌شده
- انتخاب چندمرحله‌ای (Tiered Selection)
"""

from __future__ import annotations
from typing import List, Dict, Any, Optional
import random
import math

# مسیر صحیح مطابق ساختار پروژه
from symbol_lib.library import SYMBOLS


# ==========================
#   تنظیمات و ثابت‌ها
# ==========================

WEIGHT_GOAL_MATCH = 5.0
WEIGHT_ENERGY_MATCH = 2.5
WEIGHT_PRIMARY_CULTURE = 3.0
WEIGHT_SECONDARY_CULTURE = 1.5
WEIGHT_GLOBAL_ARCHETYPE = 2.0
WEIGHT_DIVERSITY_PENALTY = -1.0

DEFAULT_RANDOMNESS = 0.3

# فعال‌سازی لاگ داخلی برای دیباگ
DEBUG_LOG = False


# ==========================
#   ابزارهای لاگ داخلی
# ==========================

def _log(*msg):
    if DEBUG_LOG:
        print("[symbol_engine]", *msg)


# ==========================
#   توابع کمکی
# ==========================

def _is_global_archetype(symbol: Dict[str, Any]) -> bool:
    return symbol.get("culture", "").strip() == "جهانی"


def _normalize_score(score: float) -> float:
    """
    نرمال‌سازی امتیاز برای جلوگیری از رشد بیش از حد.
    """
    return round(score, 4)


def _score_symbol(
    symbol: Dict[str, Any],
    goal: str,
    primary_culture: Optional[str],
    preferred_cultures: Optional[List[str]],
    energies: Optional[List[str]],
    culture_counts: Dict[str, int],
) -> float:

    score = 0.0

    uses = symbol.get("uses", []) or []
    energy_list = symbol.get("energy", []) or []
    culture = (symbol.get("culture") or "").lower()

    # ۱) تطابق goal
    if goal and goal in uses:
        score += WEIGHT_GOAL_MATCH

    # ۲) انرژی‌ها
    if energies:
        for e in energies:
            if e in energy_list:
                score += WEIGHT_ENERGY_MATCH

    # ۳) فرهنگ اصلی
    if primary_culture:
        pc = primary_culture.lower()
        if culture.startswith(pc) or pc in culture:
            score += WEIGHT_PRIMARY_CULTURE

    # ۴) فرهنگ‌های ثانویه
    if preferred_cultures:
        for c in preferred_cultures:
            cl = c.lower()
            if cl and (culture.startswith(cl) or cl in culture):
                score += WEIGHT_SECONDARY_CULTURE
                break

    # ۵) آرکتایپ جهانی
    if _is_global_archetype(symbol):
        score += WEIGHT_GLOBAL_ARCHETYPE

    # ۶) جریمهٔ تکرار فرهنگ
    if culture:
        count = culture_counts.get(culture, 0)
        if count > 0:
            score += WEIGHT_DIVERSITY_PENALTY * count

    return _normalize_score(score)


def _apply_randomness(score: float, randomness: float) -> float:
    if randomness <= 0:
        return score
    noise = random.uniform(-1.0, 1.0) * randomness * max(score, 1)
    return _normalize_score(score + noise)


# ==========================
#   انتخاب چندمرحله‌ای (Tiered Selection)
# ==========================

def _tiered_selection(scored: List[tuple[str, float]], count: int):
    """
    انتخاب مرحله‌ای:
    - ابتدا نمادهای Tier 1 (امتیاز بالا)
    - سپس Tier 2 (امتیاز متوسط)
    - سپس Tier 3 (fallback)
    """

    if not scored:
        return []

    # تقسیم به سه Tier
    max_score = scored[0][1]
    tiers = {
        "tier1": [],
        "tier2": [],
        "tier3": [],
    }

    for key, score in scored:
        if score >= max_score * 0.75:
            tiers["tier1"].append((key, score))
        elif score >= max_score * 0.45:
            tiers["tier2"].append((key, score))
        else:
            tiers["tier3"].append((key, score))

    result = []

    for tier_name in ["tier1", "tier2", "tier3"]:
        for key, score in tiers[tier_name]:
            if len(result) >= count:
                return result
            result.append(key)

    return result


# ==========================
#   موتور اصلی
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

    if count <= 0:
        return []

    exclude_ids = set(exclude_ids or [])

    # ۱) فیلتر اولیه
    candidates = {
        k: v for k, v in SYMBOLS.items()
        if (goal in (v.get("uses") or [])) and (k not in exclude_ids)
    }

    # fallback اگر goal دقیق نبود
    if not candidates:
        candidates = {k: v for k, v in SYMBOLS.items() if k not in exclude_ids}

    if not candidates:
        return []

    # ۲) شمارش فرهنگ‌ها
    culture_counts = {}
    for v in candidates.values():
        culture = (v.get("culture") or "").lower()
        if culture:
            culture_counts[culture] = 0

    # ۳) امتیازدهی
    scored = []
    for key, symbol in candidates.items():
        base = _score_symbol(
            symbol=symbol,
            goal=goal,
            primary_culture=primary_culture,
            preferred_cultures=preferred_cultures,
            energies=energies,
            culture_counts=culture_counts,
        )
        final = _apply_randomness(base, randomness)
        scored.append((key, final))

    scored.sort(key=lambda x: x[1], reverse=True)

    # ۴) انتخاب چندمرحله‌ای
    selected_keys = _tiered_selection(scored, count)

    # ۵) بازگرداندن نمادها
    return [candidates[k] for k in selected_keys]


# ==========================
#   نسخهٔ ساده
# ==========================

def get_symbols_simple(goal: str, count: int = 1, culture: Optional[str] = None):
    return select_symbols(
        goal=goal,
        count=count,
        primary_culture=culture,
        preferred_cultures=None,
        energies=None,
        randomness=DEFAULT_RANDOMNESS,
        exclude_ids=None,
    )
