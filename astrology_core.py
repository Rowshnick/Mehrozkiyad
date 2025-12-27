import swisseph as swe
import logging
import os

def calculate_natal_chart(year, month, day, hour, minute, lat, lon):
    try:
        # 1. تنظیم مسیر فایل‌های نجومی (Ephemeris)
        base_path = os.path.dirname(os.path.abspath(__file__))
        ephe_path = os.path.join(base_path, "ephe")
        swe.set_ephe_path(ephe_path)
        
        # 2. محاسبه زمان جولین (Julian Day)
        # تبدیل ساعت محلی به زمان اعشاری
        decimal_hour = hour + (minute / 60.0)
        jd = swe.julday(year, month, day, decimal_hour)
        
        # 3. محاسبه خانه‌ها (House Cusps) با متد Placidus ('P')
        # خروجی این تابع معمولاً یک توپل شامل (cusps, ascmc) است
        result = swe.houses(jd, lat, lon, b'P')
        
        # --- بخش اصلاحی برای رفع خطای Tuple Index ---
        if not result or not isinstance(result, tuple) or len(result) < 2:
            logging.error(f"Invalid SwissEph result: {result}")
            return {"status": "error", "message": "اختلال در محاسبات نجومی - خروجی نامعتبر"}
            
        cusps = result[0]
        ascmc = result[1]
        
        # 4. محاسبه موقعیت سیارات (مثال برای خورشید)
        sun_pos = swe.calc_ut(jd, swe.SUN)[0]
        
        # در اینجا می‌توانید بقیه سیارات را اضافه کنید...

        return {
            "status": "success",
            "cusps": list(cusps),
            "ascendant": ascmc[0],
            "mc": ascmc[1],
            "sun": sun_pos
        }

    except Exception as e:
        logging.error(f"Critical error in calculate_natal_chart: {str(e)}")
        # برگرداندن خطا به جای کرش کردن کل برنامه
        return {"status": "error", "message": str(e)}
