import swisseph as swe
import os
import logging

def calculate_natal_chart(year, month, day, hour, minute, lat, lon):
    try:
        # تنظیم دقیق مسیر
        base_path = os.path.dirname(os.path.abspath(__file__))
        ephe_path = os.path.join(base_path, "ephe")
        swe.set_ephe_path(ephe_path)
        
        # چاپ محتویات پوشه در لاگ برای اطمینان (فقط برای دیباگ)
        logging.info(f"Files in ephe folder: {os.listdir(ephe_path)}")
        
        jd = swe.julday(year, month, day, hour + minute/60.0)
        
        # فراخوانی با متد ایمن
        res = swe.houses(jd, lat, lon, b'P')
        
        # بررسی اینکه آیا خروجی طبق انتظار است یا خیر
        if len(res) < 2:
            logging.error(f"Error: SwissEph returned incomplete data: {res}")
            return {"status": "error", "message": "داده‌های نجومی یافت نشد. فایل‌های پوشه ephe را بررسی کنید."}

        cusps = res[0]
        ascmc = res[1]
        
        # محاسبه خورشید
        sun_pos = swe.calc_ut(jd, swe.SUN)[0]

        return {
            "status": "success",
            "cusps": list(cusps),
            "ascendant": ascmc[0],
            "sun": sun_pos
        }

    except Exception as e:
        logging.error(f"CRITICAL ERROR: {str(e)}")
        return {"status": "error", "message": f"خطای سیستمی: {str(e)}"}

