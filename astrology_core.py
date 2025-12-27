import swisseph as swe
import logging
import os

def calculate_natal_chart(year, month, day, hour, minute, lat, lon):
    try:
        # تنظیم مسیر فایل‌های Ephemeris
        base_path = os.path.dirname(os.path.abspath(__file__))
        ephe_path = os.path.join(base_path, "ephe")
        swe.set_ephe_path(ephe_path)
        
        # محاسبه زمان جولین
        jd = swe.julday(year, month, day, hour + minute/60.0)
        
        # محاسبه خانه‌ها - بخش بحرانی
        # ما خروجی را ابتدا چک می‌کنیم تا از کرش جلوگیری شود
        try:
            result = swe.houses(jd, lat, lon, b'P')
            logging.info(f"RAW SWISSEPH RESULT: {result}") # این خط در لاگ راهگشاست
        except Exception as internal_e:
            logging.error(f"SwissEph Library Internal Error: {internal_e}")
            return {"status": "error", "message": "خطای داخلی کتابخانه نجومی"}

        # بررسی هوشمند خروجی
        if result and isinstance(result, tuple) and len(result) >= 2:
            cusps = result[0]
            ascmc = result[1]
        else:
            # اگر خروجی توپل نبود، سعی در استخراج دستی داده
            logging.warning("Non-standard output detected from SwissEph")
            return {"status": "error", "message": "داده‌های نجومی یافت نشد. مختصات را چک کنید."}

        # ادامه محاسبات (مثلاً برای خورشید)
        sun_pos = swe.calc_ut(jd, swe.SUN)[0]

        return {
            "status": "success",
            "cusps": list(cusps),
            "ascendant": ascmc[0],
            "sun": sun_pos
        }

    except Exception as e:
        logging.error(f"FINAL ERROR in astrology_core: {str(e)}")
        return {"status": "error", "message": str(e)}
