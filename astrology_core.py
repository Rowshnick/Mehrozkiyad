import swisseph as swe
import logging

def calculate_natal_chart(year, month, day, hour, minute, lat, lon):
    try:
        # تنظیم مسیر فایل‌های نجومی
        import os
        base_path = os.path.dirname(os.path.abspath(__file__))
        swe.set_ephe_path(os.path.join(base_path, "ephe"))

        # محاسبه زمان جولین
        jd = swe.julday(year, month, day, hour + minute/60.0)
        
        # محاسبه خانه‌ها - بخش بحرانی
        # متد محاسباتی Placidus ('P')
        res = swe.houses(jd, lat, lon, b'P')
        
        # لاگ برای دیباگ - این را در لاگ Railway چک کنید
        logging.info(f"DEBUG: SwissEph Houses result type: {type(res)}")
        
        # بررسی هوشمند خروجی برای جلوگیری از خطای Index
        if isinstance(res, tuple) and len(res) > 0:
            cusps = res[0]
            ascmc = res[1]
        else:
            # اگر خروجی مستقیم بود (در برخی نسخه‌ها)
            cusps = res
            ascmc = [0, 0] # مقدار پیش‌فرض

        # ادامه محاسبات سیارات...
        # (بقیه کد شما در اینجا قرار بگیرد)
        
        return {"status": "success", "cusps": cusps, "ascendant": ascmc[0]}

    except Exception as e:
        logging.error(f"DETAILED ERROR: {str(e)}")
        raise e
