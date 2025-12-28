import swisseph as swe
import os
import logging

def calculate_natal_chart(year, month, day, hour, minute, lat, lon, **kwargs):
    """
    محاسبه چارت تولد. 
    **kwargs 
    باعث می‌شود اگر ورودی‌های اضافه‌ای مثل birth_date فرستاده شد، برنامه کرش نکند.
    """
    try:
        import swisseph as swe
        import os
        
        # تنظیم مسیر فایل‌های نجومی
        base_path = os.path.dirname(os.path.abspath(__file__))
        ephe_path = os.path.join(base_path, "ephe")
        swe.set_ephe_path(ephe_path)
        
        jd = swe.julday(year, month, day, hour + minute/60.0)
        
        # محاسبه خانه‌ها با متد Placidus
        res = swe.houses(jd, lat, lon, b'P')
        
        if len(res) < 2:
            return {"status": "error", "message": "دیتابیس نجومی شناسایی نشد"}

        return {
            "status": "success",
            "cusps": list(res[0]),
            "ascendant": res[1][0],
            "sun": swe.calc_ut(jd, swe.SUN)[0]
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
