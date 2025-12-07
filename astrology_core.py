# ----------------------------------------------------------------------
# ماژول اصلی محاسبات آسترولوژی
# ----------------------------------------------------------------------

import datetime
from skyfield.api import load, Topos
from skyfield.timelib import Time
from typing import Dict, Any, Tuple
from persiantools.jdatetime import JalaliDateTime
import utils 
import pytz 

# ثابت‌ها
PLANETS = ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune', 'pluto'] 
DEGREES_PER_SIGN = 30
ZODIAC_SIGNS_FA = ["حمل", "ثور", "جوزا", "سرطان", "اسد", "سنبله", 
                    "میزان", "عقرب", "قوس", "جدی", "دلو", "حوت"]
PLANET_SYMBOLS_FA = {
    'sun': "خورشید ☉",
    'moon': "ماه ☽",
    'mercury': "عطارد ☿",
    'venus': "زهره ♀",
    'mars': "مریخ ♂",
    'jupiter': "مشتری ♃",
    'saturn': "زحل ♄",
    'uranus': "اورانوس ⛢",
    'neptune': "نپتون ♆",
    'pluto': "پلوتو ♇",
}

# داده‌های نجومی را بارگذاری کنید 
try:
    # Skyfield به‌طور خودکار فایل را دانلود یا از کش استفاده می‌کند.
    EPHEMERIS = load('de421.bsp')
except Exception as e:
    # 💡 [تقویت خطاگیری]: اگر بارگذاری Ephemeris شکست بخورد، این خطا چاپ می‌شود.
    print(f"Error loading ephemeris: {e}. Skyfield calculations will fail.")
    EPHEMERIS = None

def get_zodiac_position(lon: float) -> Tuple[str, str]:
    """تبدیل طول جغرافیایی (Ecliptic Longitude) به علامت زودیاک و درجه/دقیقه آن."""
    
    if lon < 0:
        lon += 360 
    if lon >= 360:
        lon %= 360

    sign_index = int(lon // DEGREES_PER_SIGN)
    degree_in_sign = lon % DEGREES_PER_SIGN
    
    sign_name = ZODIAC_SIGNS_FA[sign_index % 12]
    
    degrees = int(degree_in_sign)
    minutes = int((degree_in_sign - degrees) * 60)
    seconds = int(((degree_in_sign - degrees) * 60 - minutes) * 60)
    
    degree_str = f"{degrees}° {minutes:02d}' {seconds:02d}\""
    
    return sign_name, degree_str

def calculate_natal_chart(birth_time_gregorian: datetime.datetime, lat: float, lon: float, tz: pytz.BaseTzInfo) -> Dict[str, Any]:
    """محاسبه موقعیت اجرام آسمانی برای زمان و مکان تولد."""
    
    if EPHEMERIS is None:
        return {"error": "منابع نجومی (Ephemeris) بارگذاری نشده‌اند. لطفاً اتصال شبکه را بررسی کنید یا مطمئن شوید فایل de421.bsp در دسترس است."}
        
    try:
        ts = load.timescale()
        
        # اعمال منطقه زمانی دریافتی (tz) به datetime
        localized_dt = tz.localize(birth_time_gregorian.replace(tzinfo=None))
        t: Time = ts.from_datetime(localized_dt) 
        
        observer: Topos = EPHEMERIS['earth'] + Topos(latitude_degrees=lat, longitude_degrees=lon)
        
        chart_data: Dict[str, Any] = {}
        
        for planet_name in PLANETS:
            try:
                planet_ephem = EPHEMERIS[planet_name]
                position = observer.at(t).observe(planet_ephem)
                # استفاده از epoch=t برای مختصات دایرةالبروج حقیقی (True Ecliptic)
                lon_rad, _, _ = position.ecliptic_lonlat(epoch=t) 
                
                lon_deg = lon_rad.degrees
                
                sign_name, degree_str = get_zodiac_position(lon_deg)
                
                chart_data[planet_name] = {
                    "name_fa": PLANET_SYMBOLS_FA.get(planet_name, planet_name),
                    "sign_fa": sign_name,
                    "position_str": degree_str,
                    "longitude_deg": round(lon_deg, 4),
                }
            
            except Exception as e:
                # 💡 اگر محاسبه یک سیاره خاص شکست بخورد
                chart_data[planet_name] = {"error": f"Error calculating {planet_name}: {e}"}
                
        
        # ۴. محاسبه Ascendant و Houses (PLACEHOLDER)
        
        return chart_data
    
    except Exception as general_e:
        # 💡 [جدید]: در صورت بروز هر خطای پیش‌بینی نشده در فرآیند محاسبات
        print(f"General Calculation Error: {general_e}")
        return {"error": f"خطای کلی در هسته محاسبات: {general_e}"}

# ======================================================================
# توابع فرمت‌دهی (برای نمایش به کاربر) 
# ======================================================================

def format_chart_summary(chart_data: Dict[str, Any], jdate: JalaliDateTime, city_name: str) -> str:
    """تولید خلاصه متنی چارت تولد."""
    
    # 💡 [اطمینان]: اگر خطایی در داده‌ها وجود داشت، آن را در خلاصه نمایش دهید.
    if chart_data.get('error'):
        return utils.escape_markdown_v2(f"❌ خطای محاسباتی\\: {chart_data['error']}\\n\\n لطفاً دوباره امتحان کنید یا با پشتیبانی تماس بگیرید\\.")
        
    sun_info = chart_data.get('sun', {})
    moon_info = chart_data.get('moon', {})
    
    summary = (
        f"🌟 *خلاصه چارت تولد شما* 🌟\n\n"
        f"**تاریخ تولد \\(شمسی\\)**\\: `{jdate.strftime('%Y/%m/%d')}`\n"
        f"**شهر تولد**\\: {utils.escape_markdown_v2(city_name)}\n"
        f"--- \n"
        f"**خورشید \\(Sun\\)**\\: {sun_info.get('sign_fa', 'نامعلوم')} در درجه {sun_info.get('position_str', 'نامعلوم')}\n"
        f"**ماه \\(Moon\\)**\\: {moon_info.get('sign_fa', 'نامعلوم')} در درجه {moon_info.get('position_str', 'نامعلوم')}\n"
        f"--- \n"
        f"جهت مشاهده جزئیات بیشتر از دکمه‌های زیر استفاده کنید\\."
    )
    return utils.escape_markdown_v2(summary)


def format_planet_positions(chart_data: Dict[str, Any]) -> str:
    """تولید لیست موقعیت سیارات."""
    
    if not chart_data:
        return utils.escape_markdown_v2("❌ اطلاعات چارت موجود نیست\\.")
    
    # 💡 [اطمینان]: اگر خطای کلی در داده‌ها وجود داشت، آن را نمایش دهید.
    if chart_data.get('error'):
        return utils.escape_markdown_v2(f"❌ خطای محاسباتی\\: {chart_data['error']}")
        
    header = "🪐 *موقعیت سیارات در زمان تولد* 🪐\n\n"
    positions = []
    
    for planet_name in PLANETS:
        data = chart_data.get(planet_name, {})
        
        # نمایش خطای سیاره خاص
        if data.get('error'):
            positions.append(f"• {PLANET_SYMBOLS_FA.get(planet_name, planet_name)}\\: \\(خطا در محاسبه\\: {data['error']}\\)")
            continue
            
        pos_line = (
            f"• **{data['name_fa']}**\\: "
            f"`{data['sign_fa']}` در درجه `{data['position_str']}`"
        )
        positions.append(pos_line)
        
    return utils.escape_markdown_v2(header + "\n".join(positions))
