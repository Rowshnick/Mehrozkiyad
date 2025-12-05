# ----------------------------------------------------------------------
# handlers/sajil_handlers.py
# منطق کامل Sajil و محاسبات وابسته.
# ----------------------------------------------------------------------

import datetime
from typing import List, Optional, Tuple, Dict, Any
import utils

async def run_sajil_workflow(chat_id: int, text: str, get_state_func, save_state_func):
    """
    اجرای گردش کار سجیل: دریافت ورودی، پردازش و ارسال نتیجه.
    """
    
    # 1. آماده‌سازی داده (تجزیه متن ورودی)
    input_list_str = text.strip().replace(',', ' ').split()
    
    clean_data, error_msg = _sajil_part_one_validate(input_list_str)
    
    if error_msg:
        await utils.send_message(
            utils.BOT_TOKEN, 
            chat_id, 
            utils.escape_markdown_v2(f"❌ خطای ورودی سجیل\\: {error_msg}"), 
        )
        # 💡 [اصلاح]: وضعیت را به SAJIL_INPUT برمی‌گردانیم تا دوباره بتواند شروع کند.
        state = await get_state_func(chat_id)
        state['step'] = 'SAJIL_INPUT' 
        await save_state_func(chat_id, state)

    else:
        # 2. پردازش اصلی
        result_data = _sajil_part_two_process(clean_data)
        
        # 3. تولید گزارش
        report = _format_sajil_report(result_data, text)
        
        await utils.send_message(
            utils.BOT_TOKEN, 
            chat_id, 
            report
        )
        
        # 4. بازگشت به منوی اصلی
        state = await get_state_func(chat_id)
        state['step'] = 'WELCOME' 
        await save_state_func(chat_id, state)

def _sajil_part_one_validate(input_list: List[str]) -> Tuple[List[float], Optional[str]]:
    """اعتبارسنجی و تبدیل لیست ورودی به اعداد ممیز شناور (Float)."""
    clean_data = []
    
    if not input_list:
        return [], "لطفاً حداقل یک عدد وارد کنید."

    for index, item in enumerate(input_list):
        try:
            float_item = float(item)
            clean_data.append(float_item)
        except (ValueError, TypeError):
            error_msg = f"داده نامعتبر در ورودی {index+1} \\('{item}'\\)\\. تمام ورودی‌ها باید عدد باشند\\."
            return [], error_msg
            
    return clean_data, None

def _sajil_part_two_process(prepared_data: List[float]) -> Dict[str, Any]:
    """اجرای منطق اصلی برنامه (محاسبه میانگین و مجموع) برای تولید گزارش سجیل."""

    if not prepared_data:
        return {"status": "Failure", "message": "داده آماده شده‌ای برای پردازش وجود ندارد."}

    total_sum = sum(prepared_data)
    total_count = len(prepared_data)
    average = total_sum / total_count
    
    result = {
        "status": "Success",
        "total_items": total_count,
        "total_sum": total_sum,
        "average_value": average,
        "report_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "generated_symbol": "☿", 
        "analysis_summary": "تحلیل خلاصه اولیه\\: مجموع ورودی‌های شما \\({total_sum}\\) نشان‌دهنده پتانسیل قوی برای تمرکز و تکمیل پروژه‌ها است\\."
    }
    
    return result

def _format_sajil_report(data: Dict[str, Any], raw_input: str) -> str:
    """فرمت دهی گزارش سجیل برای ارسال به کاربر."""
    if data['status'] == 'Failure':
        return utils.escape_markdown_v2(f"❌ گزارش سجیل تکمیل نشد\\: {data['message']}")
        
    report = (
        f"✨ *گزارش سجیل برای ورودی*\\: `{utils.escape_code_block(raw_input)}`\n"
        f"--- \n"
        f"**جمع کل اعداد**\\: `{data['total_sum']:.2f}`\n"
        f"**میانگین**\\: `{data['average_value']:.2f}`\n"
        f"**تعداد ورودی‌ها**\\: `{data['total_items']}`\n"
        f"**نماد اصلی**\\: {data['generated_symbol']}\n"
        f"--- \n"
        f"*{data['analysis_summary'].format(total_sum=data['total_sum']):s}*\n\n"
        f"\\(زمان گزارش\\: {data['report_time']}\\)\n"
    )
    return utils.escape_markdown_v2(report)
