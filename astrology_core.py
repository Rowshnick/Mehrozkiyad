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
    # در کنار فایل‌های سورس قرار دارند (که توسط Dockerfile به /usr/src/app کپی شده‌اند).
    # نقطه (./) به معنی مسیر WORKDIR یا همان /usr/src/app است.
    se.set_ephe_path('./ephe_data/') 
    logging.info("Ephemeris path set successfully to './ephe_data/'.")
except Exception as e:
    # این هشدار اصلی را در صورتی که مسیر درست نباشد یا فایل‌ها نباشند، تولید می‌کند.
    logging.warning(f"Setup Ephemeris not found or failed, continuing without it. Error: {e}")
    # همچنین در صورتی که path ست نشود، از se.calc_ut با پرچم 0 استفاده می‌کنیم (Flag 0)
    # که در خط 144 کد شما وجود دارد و از داده‌های پیش‌فرض استفاده می‌کند (اما دقت پایین است).
    # رفع کامل منوط به وجود پوشه ephe_data است.


# --- [ثابت‌ها] ---
PLANETS_MAP = {
    "sun": 0, # معادل se.SE_SUN
    "moon": 1, # معادل se.SE_MOON
    "mercury": 2, # معادل se.SE_MERCURY
    "venus": 3, # معادل se.SE_VENUS
    "mars": 4, # معادل se.SE_MARS
    "jupiter": 5, # معادل se.SE_JUPITER
    "saturn": 6, # معادل se.SE_SATURN
    "uranus": 7, # معادل se.SE_URANUS
    "neptune": 8, # معادل se.SE_NEPTUNE
    "pluto": 9, # معادل se.SE_PLUTO
    "true_node": 10 # معادل se.SE_TRUE_NODE (گره شمالی حقیقی)
}

ASPECT_DEGREES = {
    "Conjunction": 0.0,
    "Sextile": 60.0,
    "Square": 90.0,
    "Trine": 120.0,
    "Opposition": 180.0,
}

# Orb های نسبتاً تنگ برای نمایش مهم‌ترین زوایا
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
    # The order corresponds to 0-29.99 = ARIES, 30-59.99 = TAURUS, etc.
    sign_names_en = ['ARIES', 'TAURUS', 'GEMINI', 'CANCER', 'LEO', 'VIRGO', 'LIBRA', 'SCORPIO', 'SAGITTARIUS', 'CAPRICORN', 'AQUARIUS', 'PISCES']
    sign_index = int(degree // 30) % 12
    return sign_names_en[sign_index]

def calculate_aspects(planets: Dict[str, Any]) -> List[Dict[str, Any]]:
    """محاسبه زوایای اصلی بین سیارات با Orb مشخص."""
    aspects = []
    
    # لیست سیاراتی که باید زوایایشان بررسی شود (مثلاً سیارات شخصی و اجتماعی)
    aspect_planets = ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "true_node", "pluto", "neptune", "uranus"]
    
    # فیلتر کردن برای اطمینان از وجود درجه و حذف سیارات مجهول
    planet_items = [(name, data['degree']) for name, data in planets.items() if name in aspect_planets and 'degree' in data]
    
    # از هر سیاره به سیارات بعدی (جلوگیری از تکرار و مقایسه با خود)
    for i in range(len(planet_items)):
        p1_name, p1_deg = planet_items[i]
        for j in range(i + 1, len(planet_items)):
            p2_name, p2_deg = planet_items[j]
            
            for aspect_name, aspect_degree in ASPECT_DEGREES.items():
                
                degree_diff = get_degree_diff(p1_deg, p2_deg)
                orb = abs(degree_diff - aspect_degree)
                max_orb = ASPECT_ORBS.get(aspect_name, 1.0) # پیش‌فرض 1.0 برای احتیاط
                
                # برای گره‌ها و سیارات بیرونی Orb را کمی سخت‌گیرانه‌تر می‌کنیم
                if p1_name in ["true_node", "pluto", "neptune", "uranus"] or p2_name in ["true_node", "pluto", "neptune", "uranus"]:
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
                    
    # مرتب‌سازی بر اساس Orb (تنگ‌ترین زوایا ابتدا)
    aspects.sort(key=lambda x: x['orb'])
    
    # بازگشت تنها 5 زاویه برتر
    return aspects[:5]


# ----------------------------------------------------------------------
# تابع اصلی: محاسبه چارت تولد (به روز شده با Part of Fortune و Sign/House)
# ----------------------------------------------------------------------

def calculate_natal_chart(birth_date_jalali: str, birth_time_str: str, city_name: str, latitude: Union[float, int], longitude: Union[float, int], timezone_str: str) -> Dict[str, Any]:
    """
    محاسبه چارت تولد نجومی شامل موقعیت سیارات و خانه‌ها بر اساس سیستم پلاسی دوس.
    """
    
    # 1. تبدیل تاریخ شمسی به میلادی و محاسبه زمان جولیان (JD) UTC
    try:
        j_date = jdatetime.JalaliDate.strptime(birth_date_jalali, '%Y/%m/%d')
        j_time = datetime.datetime.strptime(birth_time_str, '%H:%M')
        
        # FIX: ترکیب تاریخ میلادی با زمان محلی
        dt_gregorian_date = j_date.to_gregorian()
        dt_local = datetime.datetime.combine(dt_gregorian_date, j_time.time())

        # اعمال منطقه زمانی
        local_tz = pytz.timezone(timezone_str)
        dt_local = local_tz.localize(dt_local)
        dt_utc = dt_local.astimezone(pytz.utc)

        # محاسبه JD UTC
        jd_utc = se.julday(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0)
        
    except Exception as e:
        logging.error(f"FATAL ERROR: خطا در تبدیل تاریخ و زمان: {e}", exc_info=True)
        return {"error": f"❌ خطای تبدیل زمان: {str(e)}"}

    
    # متغیرهایی برای نگهداری خروجی خام swisseph مورد نیاز در سراسر محاسبه
    # تعریف متغیرها پیش از بلوک try/except برای در دسترس بودن در بخش‌های بعدی
    cusps_raw = []
    ascmc = []
    house_system = b'P' # Placidus
    
    chart_data = {
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
        # "arabic_parts": {} # حذف شد: Part of Fortune به planets اضافه می‌شود
    }

    # 2. محاسبه خانه ها (Houses) - باید قبل از سیارات انجام شود
    try:
        # se.houses برای محاسبه cusps و ascmc (ascendant و midheaven)
        cusps_raw, ascmc = se.houses(jd_utc, latitude, longitude, house_system)
        
        if len(cusps_raw) < 12 or len(ascmc) < 2:
             raise IndexError(f"خروجی se.houses ناقص است. طول cusps: {len(cusps_raw)}")

        # FIX: اصلاح نامگذاری آسندانت برای هماهنگی با فایل تفسیر (استفاده از ascmc[0] به عنوان منبع اصلی)
        chart_data['houses']['ascendant'] = ascmc[0]
        chart_data['houses']['midheaven'] = ascmc[1]
        
        # ایندکس گذاری امن برای cusps
        cusps_dict = {}
        for i in range(1, 13):
            # برای Placidus، کاپس‌ها از خانه 1 شروع می‌شوند و از عنصر cusps_raw[1] استفاده می‌کنند
            index_to_use = i 
            if index_to_use >= 0 and index_to_use < len(cusps_raw):
                cusps_dict[i] = cusps_raw[index_to_use]
            else:
                cusps_dict[i] = 0.0 

        chart_data['houses']['cusps'] = cusps_dict
        chart_data['houses']['error'] = None 
        
    except Exception as e:
        err_msg = f"FATAL ERROR: خطا در محاسبه خانه‌ها و آسندانت: {e}"
        logging.error(err_msg, exc_info=True)
        chart_data['houses']['error'] = f"❌ خطای محاسبه خانه‌ها: {str(e)}"

    # 3. محاسبه موقعیت سیارات و تعیین خانه و برج
    for planet_name, planet_code in PLANETS_MAP.items():
        try:
            # استفاده از se.calc_ut. Flag 0 برای استفاده از فایل‌های اپمریس تنظیم شده
            res = se.calc_ut(jd_utc, planet_code, 0) 
            lon_deg = res[0][0]
            
            # --- محاسبه Sign و House ---
            planet_sign_en = get_sign_name_en(lon_deg)
            planet_house = 0
            if cusps_raw and ascmc:
                 # استفاده از swisseph.house_pos برای تعیین خانه دقیق
                 # house_pos عنصر دومش شماره خانه (House number) است.
                planet_house_pos = se.house_pos(lon_deg, cusps_raw, ascmc, house_system)
                planet_house = int(planet_house_pos[1])
            # --------------------------
            
            chart_data['planets'][planet_name] = {
                "degree": lon_deg,
                "status": "N/A (Calculated)",
                "sign": planet_sign_en,  # FIX: اضافه کردن Sign
                "house": planet_house,   # FIX: اضافه کردن House
            }
        except Exception as e:
            logging.error(f"FATAL ERROR: خطا در محاسبه موقعیت سیاره {planet_name}: {e}", exc_info=True)
            chart_data['planets'][planet_name] = {"error": f"❌ خطا در محاسبه: {str(e)}"}
            
    
    # 4. محاسبه نقاط عربی (Part of Fortune) و اضافه کردن آن به سیارات
    try:
        sun_deg = chart_data['planets']['sun']['degree']
        moon_deg = chart_data['planets']['moon']['degree']
        asc_deg = chart_data['houses']['ascendant']
        desc_deg = chart_data['houses']['cusps'].get(7, 0.0) # درجه کاپس خانه 7
        
        # تعیین تولد روز/شب (Day/Night Birth)
        def get_house_of_degree_simple(degree: float, asc: float, desc: float) -> int:
            """تعیین اینکه درجه در نیمکره بالا (7-12) یا پایین (1-6) است."""
            # نرمال سازی
            asc = asc % 360
            desc = desc % 360
            degree = degree % 360

            if asc > desc: # محور افق در 360/0 قطع نشده است
                 if asc >= degree > desc:
                     return 1 # خانه های 1 تا 6 (زیر افق)
                 else:
                     return 7 # خانه های 7 تا 12 (بالای افق)
            else: # محور افق از 360/0 عبور کرده است
                if degree >= asc and degree < desc:
                     return 7 # خانه های 7 تا 12 (بالای افق)
                else:
                     return 1 # خانه های 1 تا 6 (زیر افق)
        
        sun_house_zone = get_house_of_degree_simple(sun_deg, asc_deg, desc_deg)
        
        # اگر خورشید در نیمکره بالای افق (خانه 7 تا 12) باشد، روز است.
        is_day_birth = (sun_house_zone == 7) 
        
        
        if is_day_birth:
            # فرمول روز: Ascendant + Moon - Sun
            pf_degree = asc_deg + moon_deg - sun_deg
        else:
            # فرمول شب: Ascendant + Sun - Moon
            pf_degree = asc_deg + sun_deg - moon_deg

        # نرمال سازی درجه به محدوده 0 تا 360
        pf_degree = pf_degree % 360

        # تعیین برج و خانه برای Part of Fortune
        pf_sign_en = get_sign_name_en(pf_degree)
        pf_house = 0
        if cusps_raw and ascmc:
            pf_house_pos = se.house_pos(pf_degree, cusps_raw, ascmc, house_system)
            pf_house = int(pf_house_pos[1])

        # اضافه کردن Part of Fortune به دیکشنری planets
        chart_data['planets']['part_of_fortune'] = {
            "degree": pf_degree,
            "is_day_birth": is_day_birth,
            "sign": pf_sign_en,
            "house": pf_house,
            "status": "N/A (Calculated)"
        }

    except Exception as e:
         logging.error(f"خطا در محاسبه Part of Fortune: {e}")
         chart_data['planets']['part_of_fortune'] = {"error": "❌ خطا در محاسبه سهم سعادت"}
    
    
    # 5. محاسبه زوایا (Aspects)
    # این بخش باید بعد از محاسبه تمام سیارات (شامل Part of Fortune) باشد.
    chart_data['aspects'] = calculate_aspects(chart_data['planets'])


    return chart_data
