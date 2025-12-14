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
    # همچنین در صورتی که path ست نشود، از se.calc_ut با پرچم 0 استفاده می‌کنیم.


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
    sign_names_en = ['ARIES', 'TAURUS', 'GEMINI', 'CANCER', 'LEO', 'VIRGO', 'LIBRA', 'SCORPIO', 'SAGITTARIUS', 'CAPRICORN', 'AQUARIUS', 'PISCES']
    sign_index = int(degree // 30) % 12
    return sign_names_en[sign_index]

def calculate_aspects(planets: Dict[str, Any]) -> List[Dict[str, Any]]:
    """محاسبه زوایای اصلی بین سیارات با Orb مشخص."""
    aspects = []
    
    # لیست سیاراتی که باید زوایایشان بررسی شود (شامل Part of Fortune)
    aspect_planets = ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "true_node", "pluto", "neptune", "uranus", "part_of_fortune"]
    
    # فیلتر کردن برای اطمینان از وجود درجه و حذف سیارات مجهول یا خطا دار
    planet_items = [(name, data['degree']) for name, data in planets.items() if name in aspect_planets and 'degree' in data and not data.get('error')]
    
    # از هر سیاره به سیارات بعدی (جلوگیری از تکرار و مقایسه با خود)
    for i in range(len(planet_items)):
        p1_name, p1_deg = planet_items[i]
        for j in range(i + 1, len(planet_items)):
            p2_name, p2_deg = planet_items[j]
            
            for aspect_name, aspect_degree in ASPECT_DEGREES.items():
                
                degree_diff = get_degree_diff(p1_deg, p2_deg)
                orb = abs(degree_diff - aspect_degree)
                max_orb = ASPECT_ORBS.get(aspect_name, 1.0) # پیش‌فرض 1.0 برای احتیاط
                
                # برای گره‌ها، Part of Fortune و سیارات بیرونی Orb را کمی سخت‌گیرانه‌تر می‌کنیم
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
                    
    # مرتب‌سازی بر اساس Orb (تنگ‌ترین زوایا ابتدا)
    aspects.sort(key=lambda x: x['orb'])
    
    # بازگشت تنها 5 زاویه برتر
    return aspects[:5]


# ----------------------------------------------------------------------
# تابع اصلی: محاسبه چارت تولد (به روز شده با تحمل خطای بالا)
# ----------------------------------------------------------------------

def calculate_natal_chart(birth_date_jalali: str, birth_time_str: str, city_name: str, latitude: Union[float, int], longitude: Union[float, int], timezone_str: str) -> Dict[str, Any]:
    """
    محاسبه چارت تولد نجومی شامل موقعیت سیارات و خانه‌ها بر اساس سیستم پلاسی دوس.
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
    house_system = b'P' # Placidus
    
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

    # 2. محاسبه خانه ها (Houses) - باید قبل از سیارات انجام شود
    try:
        # اطمینان از اینکه ورودی‌های se.houses حتماً float باشند.
        cusps_raw, ascmc = se.houses(jd_utc, float(latitude), float(longitude), house_system)
        
        if len(cusps_raw) < 13 or len(ascmc) < 2:
             # اگر خروجی ناقص است، یک خطای مشخص ایجاد می‌کنیم.
             raise IndexError(f"خروجی se.houses ناقص است. طول cusps: {len(cusps_raw)}. آسندانت: {ascmc}")

        # اگر Ascendant صفر باشد (که در برخی خطاها رخ می‌دهد)، آن را خطا در نظر می‌گیریم.
        if ascmc[0] == 0.0 or ascmc[0] >= 360.0:
            raise ValueError(f"مقدار آسندانت غیرمعتبر: {ascmc[0]}")


        chart_data['houses']['ascendant'] = ascmc[0]
        chart_data['houses']['midheaven'] = ascmc[1]
        
        cusps_dict = {}
        # cusps_raw[1] تا cusps_raw[12] کاپس‌های خانه‌های ۱ تا ۱۲ هستند.
        for i in range(1, 13):
            index_to_use = i 
            cusps_dict[i] = cusps_raw[index_to_use]

        chart_data['houses']['cusps'] = cusps_dict
        chart_data['houses']['error'] = None 
        
    except Exception as e:
        err_msg = f"FATAL ERROR: خطا در محاسبه خانه‌ها و آسندانت: {e}"
        logging.error(err_msg, exc_info=True)
        chart_data['houses']['error'] = f"❌ خطای محاسبه خانه‌ها: {str(e)}"
        # تنظیم Ascendant و Midheaven برای جلوگیری از خطای Key در مراحل بعدی
        chart_data['houses']['ascendant'] = 0.0
        chart_data['houses']['midheaven'] = 0.0
        # تنظیم cusps_raw به لیست خالی برای جلوگیری از اجرای se.house_pos در مرحله بعد
        cusps_raw = []
        ascmc = []


    # 3. محاسبه موقعیت سیارات و تعیین خانه و برج (با تحمل خطا)
    for planet_name, planet_code in PLANETS_MAP.items():
        lon_deg = 0.0
        lat_deg = 0.0
        planet_house = 0
        planet_sign_en = "UNKNOWN"
        error_flag = None

        try:
            # استفاده از se.calc_ut. Flag 0 برای استفاده از فایل‌های اپمریس تنظیم شده
            # خروجی: (lon, lat, vel_lon, vel_lat, vel_dist)
            res = se.calc_ut(jd_utc, planet_code, 0) 
            lon_deg = res[0][0] # طول جغرافیایی
            lat_deg = res[0][1] # عرض جغرافیایی 
            
            # --- محاسبه Sign و House ---
            planet_sign_en = get_sign_name_en(lon_deg)
            if cusps_raw and ascmc:
                 # فراخوانی صحیح se.house_pos (با Lon و Lat)
                 # planet_house_pos: (degree, house_number)
                planet_house_pos = se.house_pos(lon_deg, lat_deg, cusps_raw, ascmc, house_system)
                # se.house_pos همیشه یک tuple برمی‌گرداند.
                planet_house = int(planet_house_pos[1])
            
        except Exception as e:
            # اگر محاسبه سیاره شکست خورد، تنها این بخش اجرا می‌شود و error_flag تنظیم می‌گردد
            error_flag = f"❌ خطا در محاسبه: {str(e)}"
            logging.error(f"FATAL ERROR: خطا در محاسبه موقعیت سیاره {planet_name}: {e}", exc_info=True)
            
        # FIX: اطمینان از پر شدن کلیدهای مورد نیاز تفسیر، حتی در صورت خطا
        chart_data['planets'][planet_name] = {
            "degree": lon_deg,
            "sign": planet_sign_en,
            "house": planet_house,
            "status": "N/A (Calculated)" if not error_flag else "Error",
        }
        if error_flag:
            chart_data['planets'][planet_name]['error'] = error_flag
            
    
    # 4. محاسبه نقاط عربی (Part of Fortune) و اضافه کردن آن به سیارات (با تحمل خطا)
    try:
        # استفاده از get() برای دسترسی امن به داده‌های سیارات
        sun_deg = chart_data['planets'].get('sun', {}).get('degree', 0.0)
        moon_deg = chart_data['planets'].get('moon', {}).get('degree', 0.0)
        asc_deg = chart_data['houses'].get('ascendant', 0.0)
        desc_deg = chart_data['houses']['cusps'].get(7, 0.0) 

        if asc_deg == 0.0:
            raise ValueError("آسندانت نامعتبر است.")
        
        # تعیین تولد روز/شب (Day/Night Birth)
        def get_house_of_degree_simple(degree: float, asc: float, desc: float) -> int:
            """تعیین اینکه درجه در نیمکره بالا (7-12) یا پایین (1-6) است."""
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
            # فراخوانی صحیح se.house_pos (استفاده از 0.0 برای عرض جغرافیایی نقطه عربی)
            pf_house_pos = se.house_pos(pf_degree, 0.0, cusps_raw, ascmc, house_system)
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
         # در صورت خطا، کلیدهای لازم برای تفسیر را با مقادیر امن پر می‌کنیم
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
