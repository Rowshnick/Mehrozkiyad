# sajil/formatter.py

from .models import SajilResult
from symbol_lib.library import SYMBOLS


def format_sajil_text(result: SajilResult) -> str:
    lines = [
        "🔮 *گزارش سجیل شخصی شما*",
        "",
        result.summary,
        "",
        "────────────",
        "",
        result.details,
    ]

    if result.symbols:
        lines.append("")
        lines.append("✨ نمادهای پیشنهادی برای شما:")
        for sid in result.symbols:
            sym = SYMBOLS.get(sid)
            if not sym:
                continue
            lines.append(f"- *{sym['name']}* — {sym['description']}")

    return "\n".join(lines)
