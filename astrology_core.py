import swisseph as swe
import os
import logging

def calculate_natal_chart(year, month, day, hour, minute, lat, lon, **kwargs):
    try:
        # تنظیم مسیر فایل‌های ephe
        base_path = os.path.dirname(os.path.abspath(__file__))
        ephe_path = os.path.join(base_path, "ephe")
        swe.set_ephe_path(ephe_path)
        
        # محاسبه Julian Day
        jd = swe.julday(year, month, day, hour + minute/60.0)
        
        # محاسبه خانه‌ها
        res = swe.houses(jd, lat, lon, b'P')
        
        if not res or len(res) < 2:
            return {"status": "error", "message": "دیتابیس نجومی ناقص است"}
            
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
        logging.error(f"Error in core: {str(e)}")
        return {"status": "error", "message": str(e)}
