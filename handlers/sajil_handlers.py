# handlers/sajil_handlers.py
# =============================================================================
# مدیریت کامل گردش‌کار سجیل (Sajil Workflow)
# -----------------------------------------------------------------------------
# این فایل:
#   - ورودی کاربر را دریافت می‌کند
#   - آن را اعتبارسنجی می‌کند
#   - پردازش انجام می‌دهد
#   - گزارش نهایی را به‌صورت MarkdownV2-safe ارسال می‌کند
#   - state را به منوی اصلی برمی‌گرداند
# =============================================================================

from typing import List, Dict, Any
import utils

from sajil_part_one import sajil_part_one_validate
from sajil_part_two import sajil_part_two_process


# =============================================================================
# تابع اصلی گردش‌کار
# =============================================================================

async def run_sajil_workflow(chat_id: int, text: str, get_state_func, save_state_func):
    """
    اجرای کامل گردش‌کار سجیل:
        1) دریافت ورودی
        2) اعتبارسنجی
        3) پردازش
        4) تولید گزارش
        5) ارسال خروجی
    """

    # 1) آماده‌سازی ورودی
    input_list = text.strip().replace(",", " ").split()

    clean_data, error_msg = sajil_part_one_validate(input_list)

    if error_msg:
        await utils.send_message(
            utils.BOT_TOKEN,
            chat_id,
            utils.escape_markdown_v2(f"❌ خطای ورودی سجیل:\n{error_msg}")
        )

        state = await get_state_func(chat_id)
        state["step"] = "SAJIL_INPUT"
        await save_state_func(chat_id, state)
        return

    # 2) پردازش
    result = sajil_part_two_process(clean_data)

    # 3) تولید گزارش
    report = format_sajil_report(result, text)

    # 4) ارسال گزارش
    await utils.send_message(utils.BOT_TOKEN, chat_id, report)

    # 5) بازگشت به منوی اصلی
    state = await get_state_func(chat_id)
    state["step"] = "WELCOME"
    state["data"] = {}
    await save_state_func(chat_id, state)


# =============================================================================
# فرمت‌دهی گزارش نهایی
# =============================================================================

def format_sajil_report(data: Dict[str, Any], raw_input: str) -> str:
    """
    تولید گزارش نهایی سجیل به‌صورت MarkdownV2-safe
    """

    if data["status"] == "Failure":
        return utils.escape_markdown_v2(f"❌ گزارش سجیل تکمیل نشد:\n{data['message']}")

    report = (
        f"✨ *گزارش سجیل برای ورودی*:\n"
        f"`{utils.escape_code_block(raw_input)}`\n"
        f"---\n"
        f"**جمع کل اعداد:** `{data['total_sum']:.2f}`\n"
        f"**میانگین:** `{data['average_value']:.2f}`\n"
        f"**تعداد ورودی‌ها:** `{data['total_items']}`\n"
        f"**نماد:** {data['generated_symbol']}\n"
        f"---\n"
        f"*{data['analysis_summary'].format(total_sum=data['total_sum'])}*\n\n"
        f"_(زمان گزارش: {data['report_time']})_"
    )

    return utils.escape_markdown_v2(report)
