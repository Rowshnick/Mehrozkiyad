# sajil/symbol_mapper.py

from typing import List
from symbol_lib.library import SYMBOLS


def suggest_symbols_by_life_path(life_path_number: int) -> List[str]:
    """
    نگاشت ساده عدد مسیر زندگی به چند نماد.
    بعداً می‌توانی این نگاشت را عمیق‌تر و دقیق‌تر کنی.
    """
    mapping = {
        1: ["celtic_sun", "awen"],
        2: ["celtic_knot_circle", "double_spiral"],
        3: ["lotus_buddhist", "tibetan_flower"],
        4: ["celtic_tree_of_life", "celtic_knot"],
        5: ["celtic_horse", "tibetan_cloud"],
        6: ["claddagh", "celtic_moon"],
        7: ["celtic_raven", "tibetan_mandala"],
        8: ["celtic_dragon", "vajra"],
        9: ["celtic_triple_goddess", "eight_auspicious_symbols"],
    }
    return mapping.get(life_path_number, [])


def filter_existing_symbols(symbol_ids: List[str]) -> List[str]:
    return [sid for sid in symbol_ids if sid in SYMBOLS]
