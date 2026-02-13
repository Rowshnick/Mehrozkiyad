# symbol_lib/generator/output_builder.py
# =============================================================================
# ساخت متن خروجی برای لیست سمبل‌ها
# =============================================================================

def format_symbol_list(symbols):
    """
    دریافت لیست سمبل‌ها و تبدیل آن به یک متن زیبا و قابل ارسال در تلگرام.
    هر سمبل شامل:
        - name
        - description
        - category
        - element (اختیاری)
        - keywords (اختیاری)
    """

    if not symbols:
        return "❌ هیچ سمبلی یافت نشد."

    lines = []
    for idx, sym in enumerate(symbols, start=1):
        name = sym.get("name", "—")
        desc = sym.get("description", "—")
        category = sym.get("category", "—")
        element = sym.get("element", None)
        keywords = sym.get("keywords", [])

        block = f"🔹 *{idx}. {name}*\n"
        block += f"📘 *دسته:* {category}\n"
        block += f"📝 *توضیح:* {desc}\n"

        if element:
            block += f"✨ *عنصر:* {element}\n"

        if keywords:
            kw = ", ".join(keywords)
            block += f"🔑 *کلیدواژه‌ها:* {kw}\n"

        lines.append(block)

    return "\n\n".join(lines)
