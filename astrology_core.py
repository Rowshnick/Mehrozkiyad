import swisseph as se
import logging
from typing import Dict, Any, Union, Tuple, List
from persiantools import jdatetime
import datetime
import pytz
import math

# تنظیمات Logging
logging.basicConfig(level=logging.INFO)

# ======================================================================
# رفع هشدار Ephemeris: تنظیم مسیر فایل‌های داده نجومی
# ======================================================================
try:
    # فرض می‌کنیم فایل‌های Ephemeris (مانند se1, se2,...) در پوشه 'ephe_data'
    se.set_ephe_path('./ephe_data/') 
    logging.info("Ephemeris path set successfully to './ephe_data/'.")
except Exception as e:
    logging.warning(f"Setup Ephemeris not found or failed, continuing without it. Error: {e}")
    # اگر راه اندازی اپمریس شکست خورد، همچنان ادامه می‌دهیم.


# --- [ثابت‌ها] ---
PLANETS_MAP = {
    "sun": 0, 
    "moon": 1, 
    "mercury": 2, 
    "venus": 3, 
    "mars": 4, 
    "jupiter": 5, 
    "saturn": 6, 
    "uranus": 7, 
    "neptune": 8, 
    "pluto": 9, 
    "true_node": 10 
}

ASPECT_DEGREES = {
    "Conjunction": 0.0,
    "Sextile": 60.0,
    "Square": 90.0,
    "Trine": 120.0,
    "Opposition": 180.0,
}

ASPECT_ORBS = {
    "Conjunction": 3.0,
    "Sextile": 1.5,
    "Square": 2.5,
    "Trine": 2.5,
    "Opposition": 3.0,
}


# --- [توابع کمکی محاسباتی] ---

def get_degree_diff(deg1: float, deg2: float) -> float:
    """محاسبه اختلاف کوچکترین زاویه بین دو درجه."""
    diff = abs(deg1 - deg2)
    return min(diff, 360 - diff)

def get_sign_name_en(degree: float) -> str:
    """محاسبه برج فلکی بر اساس درجه (0-360) و بازگرداندن نام انگلیسی آن (Uppercase)."""
    sign_names_en = ['ARIES', 'TAURUS', 'GEMINI', 'CANCER', 'LEO', 'VIRGO', 'LIBRA', 'SCORPIO', 'SAGITTARIUS', 'CAPRICORN', 'AQUARIUS', 'PISCES']
    sign_index = int(degree // 30) % 12
    return sign_names_en[sign_index]

def calculate_aspects(planets: Dict[str, Any]) -> List[Dict[str, Any]]:
    """محاسبه زوایای اصلی بین سیارات با Orb مشخص."""
    aspects = []
    
    aspect_planets = ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "true_node", "pluto", "neptune", "uranus", "part_of_fortune"]
    planet_items = [(name, data['degree']) for name, data in planets.items() if name in aspect_planets and 'degree' in data and not data.get('error')]
    
    for i in range(len(planet_items)):
        p1_name, p1_deg = planet_items[i]
        for j in range(i + 1, len(planet_items)):
            p2_name, p2_deg = planet_items[j]
            
            for aspect_name, aspect_degree in ASPECT_DEGREES.items():
                
                degree_diff = get_degree_diff(p1_deg, p2_deg)
                orb = abs(degree_diff - aspect_degree)
                max_orb = ASPECT_ORBS.get(aspect_name, 1.0) 
                
                if p1_name in ["true_node", "pluto", "neptune", "uranus", "part_of_fortune"] or p2_name in ["true_node", "pluto", "neptune", "uranus", "part_of_fortune"]:
                    if max_orb > 1.5:
                        max_orb = 1.5
                
                if orb <= max_orb:
                    aspects.append({
                        "p1": p1_name.replace("_", " ").title(),
                        "p2": p2_name.replace("_", " ").title(),
                        "aspect": aspect_name,
                        "orb": orb,
                        "p1_deg": p1_deg,
                        "p2_deg": p2_deg
                    })
                    
    aspects.sort(key=lambda x: x['orb'])
    
    return aspects[:5]


# ----------------------------------------------------------------------
# تابع اصلی: محاسبه چارت تولد (اصلاح خطا در پردازش خانه ها)
# ----------------------------------------------------------------------

def calculate_natal_chart(birth_date_jalali: str, birth_time_str: str, city_name: str, latitude: Union[float, int], longitude: Union[float, int], timezone_str: str) -> Dict[str, Any]:
    """
    محاسبه چارت تولد نجومی شامل موقعیت سیارات و خانه‌ها بر اساس سیستم کوخ (Koch).
    """
    
    # 1. تبدیل تاریخ شمسی به میلادی و محاسبه زمان جولیان (JD) UTC
    try:
        j_date = jdatetime.JalaliDate.strptime(birth_date_jalali, '%Y/%m/%d')
        j_time = datetime.datetime.strptime(birth_time_str, '%H:%M')
        
        dt_gregorian_date = j_date.to_gregorian()
        dt_local = datetime.datetime.combine(dt_gregorian_date, j_time.time())

        local_tz = pytz.timezone(timezone_str)
        dt_local = local_tz.localize(dt_local)
        dt_utc = dt_local.astimezone(pytz.utc)

        jd_utc = se.julday(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0)
        
    except Exception as e:
        logging.error(f"FATAL ERROR: خطا در تبدیل تاریخ و زمان: {e}", exc_info=True)
        return {"error": f"❌ خطای تبدیل زمان: {str(e)}"}

    
    # متغیرهایی برای نگهداری خروجی خام swisseph مورد نیاز
    cusps_raw = []
    ascmc = []
    # استفاده از سیستم خانه Koch (K)
    house_system = b'K' 
    
    chart_data = {
        "birth_date_jalali": birth_date_jalali,
        "birth_time_str": birth_time_str,
        
        "datetime_utc": dt_utc.isoformat(),
        "jd_utc": jd_utc,
        "city_name": city_name,
        "latitude": latitude,
        "longitude": longitude,
        "planets": {},
        "houses": {
             'ascendant': 0.0,
             'midheaven': 0.0,
             'cusps': {i: 0.0 for i in range(1, 13)}, 
             'error': None 
        },
        "aspects": [],
    }

    # 2. محاسبه خانه ها (Houses) - با اصلاحات نهایی
    try:
        # **لاگ عیب‌یابی: ورودی‌های تابع se.houses**
        logging.info(f"DEBUG: Calling se.houses with JD: {jd_utc}, Lat: {float(latitude)}, Lon: {float(longitude)}, System: {house_system.decode('utf-8')}")
        
        raw_cusps, raw_ascmc = se.houses(jd_utc, float(latitude), float(longitude), house_system)
        
        # **لاگ عیب‌یابی: خروجی خام تابع se.houses**
        logging.info(f"DEBUG: se.houses RAW Output - Cusps (first 3): {raw_cusps[:3] if isinstance(raw_cusps, (list, tuple)) else 'Invalid Type'}, Asc/MC: {raw_ascmc[:2] if isinstance(raw_ascmc, (list, tuple)) and len(raw_ascmc) >= 2 else 'Invalid Type/Length'}")
        
        # گام 1: بررسی خطا و طول خروجی Swisseph
        if not isinstance(raw_ascmc, (list, tuple)) or len(raw_ascmc) < 2 or not isinstance(raw_ascmc[0], (int, float)):
             raise ValueError(f"خروجی Asc/MC نامعتبر است. مقدار: {raw_ascmc}")
        
        # FIX: بررسی طول را به حداقل 12 عنصر کاهش می‌دهیم.
        if len(raw_cusps) < 12:
             raise IndexError(f"خروجی cusps ناقص است. طول cusps: {len(raw_cusps)}")

        # گام 2: تخصیص و بررسی نهایی اعتبار (مقدار صفر یا خارج از محدوده)
        cusps_raw = list(raw_cusps)
        ascmc = list(raw_ascmc) 
        
        if ascmc[0] == 0.0 or ascmc[0] >= 360.0:
            raise ValueError(f"مقدار آسندانت غیرمعتبر: {ascmc[0]}")


        chart_data['houses']['ascendant'] = ascmc[0]
        chart_data['houses']['midheaven'] = ascmc[1]
        
        cusps_dict = {}
        # FIX: منطق جدید برای تطابق ایندکس‌های خانه (1 تا 12) با آرایه خام (با طول 12 یا 13)
        # اگر طول 12 باشد (اندیس 0 تا 11)، برای خانه 1 از اندیس 0 استفاده می‌شود (i-1).
        # اگر طول 13 باشد (اندیس 0 تا 12، که اندیس 0 رها شده)، برای خانه 1 از اندیس 1 استفاده می‌شود (i).
        is_12_element_array = len(cusps_raw) == 12
        for i in range(1, 13):
            index_to_use = i - 1 if is_12_element_array else i 
            # بررسی ایمنی: اگر با وجود طول 12 یا 13، باز هم اندیس خارج از محدوده بود.
            if index_to_use >= len(cusps_raw):
                 raise IndexError(f"خطای ایندکس پس از تطبیق: Index {index_to_use} out of bounds for size {len(cusps_raw)}")
                 
            cusps_dict[i] = cusps_raw[index_to_use]

        chart_data['houses']['cusps'] = cusps_dict
        chart_data['houses']['error'] = None 
        
    except Exception as e:
        err_msg = f"FATAL ERROR: خطا در محاسبه خانه‌ها و آسندانت: {e}"
        logging.error(err_msg, exc_info=True)
        chart_data['houses']['error'] = f"❌ خطای محاسبه خانه‌ها: {str(e)}"
        
        # در صورت شکست، متغیرهای مورد نیاز برای محاسبه خانه‌ سیارات را خالی می‌کنیم تا از خطای زنجیره‌ای جلوگیری شود
        chart_data['houses']['ascendant'] = 0.0
        chart_data['houses']['midheaven'] = 0.0
        cusps_raw = []
        ascmc = []


    # 3. محاسبه موقعیت سیارات و تعیین خانه و برج 
    for planet_name, planet_code in PLANETS_MAP.items():
        lon_deg = 0.0
        lat_deg = 0.0
        planet_house = 0
        planet_sign_en = "UNKNOWN"
        error_flag = None

        try:
            res = se.calc_ut(jd_utc, planet_code, 0) 
            lon_deg = res[0][0] 
            lat_deg = res[0][1] 
            
            # --- محاسبه Sign و House ---
            planet_sign_en = get_sign_name_en(lon_deg)
            if cusps_raw and ascmc:
                # محاسبه خانه سیاره با استفاده از خروجی خام و سیستم خانه Koch
                planet_house_pos = se.house_pos(lon_deg, lat_deg, cusps_raw, ascmc, house_system)
                planet_house = int(planet_house_pos[1])
            
        except Exception as e:
            error_flag = f"❌ خطا در محاسبه: {str(e)}"
            logging.error(f"FATAL ERROR: خطا در محاسبه موقعیت سیاره {planet_name}: {e}", exc_info=True)
            
        chart_data['planets'][planet_name] = {
            "degree": lon_deg,
            "sign": planet_sign_en,
            "house": planet_house,
            "status": "N/A (Calculated)" if not error_flag else "Error",
        }
        if error_flag:
            chart_data['planets'][planet_name]['error'] = error_flag
            
    
    # 4. محاسبه نقاط عربی (Part of Fortune) 
    try:
        sun_deg = chart_data['planets'].get('sun', {}).get('degree', 0.0)
        moon_deg = chart_data['planets'].get('moon', {}).get('degree', 0.0)
        asc_deg = chart_data['houses'].get('ascendant', 0.0)
        desc_deg = chart_data['houses']['cusps'].get(7, 0.0) 

        # اگر آسندانت محاسبه شده 0.0 باشد، نشان‌دهنده شکست است.
        if asc_deg == 0.0 or chart_data['planets'].get('sun', {}).get('error') or chart_data['planets'].get('moon', {}).get('error'):
            raise ValueError("اطلاعات آسندانت، خورشید یا ماه نامعتبر است.")
        
        # تعیین تولد روز/شب 
        def get_house_of_degree_simple(degree: float, asc: float, desc: float) -> int:
            asc = asc % 360
            desc = desc % 360
            degree = degree % 360

            if asc > desc: 
                 return 1 if asc >= degree > desc else 7
            else: 
                 return 7 if degree >= asc and degree < desc else 1
        
        sun_house_zone = get_house_of_degree_simple(sun_deg, asc_deg, desc_deg)
        is_day_birth = (sun_house_zone == 7) 
        
        
        if is_day_birth:
            pf_degree = asc_deg + moon_deg - sun_deg
        else:
            pf_degree = asc_deg + sun_deg - moon_deg

        pf_degree = pf_degree % 360

        pf_sign_en = get_sign_name_en(pf_degree)
        pf_house = 0
        if cusps_raw and ascmc:
            pf_house_pos = se.house_pos(pf_degree, 0.0, cusps_raw, ascmc, house_system)
            pf_house = int(pf_house_pos[1])

        chart_data['planets']['part_of_fortune'] = {
            "degree": pf_degree,
            "is_day_birth": is_day_birth,
            "sign": pf_sign_en,
            "house": pf_house,
            "status": "N/A (Calculated)"
        }

    except Exception as e:
         logging.error(f"خطا در محاسبه Part of Fortune: {e}")
         chart_data['planets']['part_of_fortune'] = {
            "error": "❌ خطا در محاسبه سهم سعادت", 
            "degree": 0.0,
            "sign": "UNKNOWN",
            "house": 0,
            "status": "N/A (Error)"
        }
    
    
    # 5. محاسبه زوایا (Aspects)
    chart_data['aspects'] = calculate_aspects(chart_data['planets'])


    return chart_data
