# handlers/sajil_handlers.py
import datetime
from typing import List, Optional, Tuple, Dict, Any
import utils

async def run_sajil_workflow(chat_id: int, text: str, get_state, save_state):

    items = text.strip().replace(",", " ").split()
    values, error = _validate(items)

    if error:
        await utils.send_message(
            utils.get_bot_token(),
            chat_id,
            utils.escape_markdown_v2(f"❌ {error}")
        )
        state = await get_state(chat_id)
        state["step"] = "SAJIL_INPUT"
        await save_state(chat_id, state)
        return

    result = _process(values)
    report = _format_report(result, text)

    await utils.send_message(
        utils.get_bot_token(),
        chat_id,
        report
    )

    state = await get_state(chat_id)
    state["step"] = "WELCOME"
    await save_state(chat_id, state)

def _validate(data: List[str]) -> Tuple[List[float], Optional[str]]:
    cleaned = []
    if not data:
        return [], "ورودی خالی است"

    for i, d in enumerate(data):
        try:
            cleaned.append(float(d))
        except ValueError:
            return [], f"ورودی {i+1} عدد نیست"

    return cleaned, None

def _process(values: List[float]) -> Dict[str, Any]:
    total = sum(values)
    count = len(values)
    avg = total / count

    return {
        "total": total,
        "average": avg,
        "count": count,
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    }

def _format_report(data: Dict[str, Any], raw: str) -> str:
    return utils.escape_markdown_v2(
        f"✨ *گزارش سجیل*\n\n"
        f"🔢 ورودی: `{utils.escape_code_block(raw)}`\n"
        f"➕ جمع: `{data['total']:.2f}`\n"
        f"➗ میانگین: `{data['average']:.2f}`\n"
        f"🧮 تعداد: `{data['count']}`\n"
        f"⏰ زمان: `{data['time']}`"
    )
