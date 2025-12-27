import swisseph as swe
import os
import logging

def calculate_natal_chart(year, month, day, hour, minute, lat, lon):
    try:
        # تنظیم مسیر فایل‌های نجومی
        base_path = os.path.dirname(os.path.abspath(__file__))
        ephe_path = os.path.join(base_path, "ephe")
        swe.set_ephe_path(ephe_path)
        
        # تبدیل تاریخ و زمان به زمان جهانی (Julian Day)
        # توجه: اگر از تاریخ شمسی استفاده می‌کنید، باید ابتدا به میلادی تبدیل شود
        jd = swe.julday(year, month, day, hour + minute/60.0)
        
        # محاسبه خانه‌ها (Cusps)
        # اضافه کردن چک امنیتی برای خروجی
        res = swe.houses(jd, lat, lon, b'P')
        
        if not res or len(res) < 2:
            logging.error(f"SwissEph Error: Invalid output for Houses. Result: {res}")
            return {"status": "error", "message": "فایل‌های دیتابیس نجومی (ephe) ناقص هستند یا لود نشدند."}
            
        cusps = res[0]
        ascmc = res[1]
        
        # محاسبه موقعیت خورشید (نمونه)
        sun_res = swe.calc_ut(jd, swe.SUN)
        if not sun_res:
            return {"status": "error", "message": "خطا در محاسبه موقعیت سیارات"}
            
        sun_pos = sun_res[0]

        return {
            "status": "success",
            "cusps": list(cusps),
            "ascendant": ascmc[0],
            "sun": sun_pos
        }

    except Exception as e:
        logging.error(f"CRITICAL ERROR in astrology_core: {str(e)}")
        return {"status": "error", "message": str(e)}
