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

# 💥 [کد حیاتی برای رفع خطای "geometry_of" - نصب اجباری در زمان اجرای اولیه]
# این کد، Skyfield را مجبور می‌کند که حتی در صورت وجود کش، خود را دوباره نصب کند.

try:
    import subprocess
    import sys
    
    # دستور نصب اجباری Skyfield (فقط در زمان Deploy/شروع برنامه)
    # توجه: از subprocess.run استفاده شده تا خطای زمان اجرا در Railway را نادیده نگیرد
    
    # این دستور اگر موفقیت‌آمیز باشد، تضمین می‌کند که ورژن صحیح بارگذاری شود.
    result = subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "--force-reinstall", "skyfield"], 
                            capture_output=True, text=True, check=False)
    
    # اگر نصب موفقیت‌آمیز بود (کد بازگشتی 0)، یک پیغام در لاگ‌ها ثبت شود
    if result.returncode == 0:
        print("✅ Skyfield successfully re-installed and upgraded at runtime.")
    else:
        # در صورت شکست (مثلاً عدم دسترسی به شبکه)، خطا را ثبت کنید اما برنامه ادامه دهد
        print(f"❌ Failed to force-reinstall Skyfield at runtime. Error: {result.stderr}")
        
except Exception as e:
    # در صورت شکست در اجرای subprocess، پیام خطا ثبت می‌شود
    print(f"Error during runtime Skyfield check: {e}")

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
    # Skyfield داده de421.bsp را به صورت پیش‌فرض از اینترنت دانلود می‌کند
    EPHEMERIS = load('de421.bsp')
except Exception as e:
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
        return {"error": "منابع نجومی (Ephemeris) بارگذاری نشده‌اند. لطفاً اتصال شبکه را بررسی کنید."}
        
    try:
        ts = load.timescale()
        
        # ۱. آماده‌سازی ناظر و زمان
        localized_dt = tz.localize(birth_time_gregorian.replace(tzinfo=None))
        t: Time = ts.from_datetime(localized_dt) 
        
        observer: Topos = EPHEMERIS['earth'] + Topos(latitude_degrees=lat, longitude_degrees=lon)
        
        chart_data: Dict[str, Any] = {}
        
        # ۲. حلقه محاسبات برای هر سیاره
        for planet_name in PLANETS:
            try:
                # فچ کردن سیاره
                planet_ephem = EPHEMERIS[planet_name]
                position = observer.at(t).observe(planet_ephem)
                
                # 💡 [خط اصلاح شده برای Skyfield جدید (>=1.43)]: این خط حلال خطای 'Astrometric' object has no attribute 'geometry_of' است.
                lon_rad, _, _ = position.geometry_of(t).ecliptic_lonlat(epoch=t) 
                lon_deg = lon_rad.degrees
                
                sign_name, degree_str = get_zodiac_position(lon_deg)
                
                # ذخیره داده‌ها
                chart_data[planet_name] = {
                    "name_fa": PLANET_SYMBOLS_FA.get(planet_name, planet_name),
                    "sign_fa": sign_name,
                    "position_str": degree_str,
                    "longitude_deg": round(lon_deg, 4),
                }
            
            except Exception as e:
                # اگر محاسبه یک سیاره خاص شکست بخورد، متن خطا را در دیکشنری ذخیره کنید.
                chart_data[planet_name] = {"error": str(e)}
                
        
        # ۴. محاسبه Ascendant و Houses (PLACEHOLDER - نیاز به پیاده‌سازی)
        
        return chart_data
    
    except Exception as general_e:
        # در صورت بروز هر خطای پیش‌بینی نشده در فرآیند محاسبات
        print(f"General Calculation Error: {general_e}")
        return {"error": f"خطای کلی در هسته محاسبات: {general_e}"}

# ======================================================================
# توابع فرمت‌دهی (برای نمایش به کاربر) 
# ======================================================================

def format_chart_summary(chart_data: Dict[str, Any], jdate: JalaliDateTime, city_name: str) -> str:
    """تولید خلاصه متنی چارت تولد."""
    
    if chart_data.get('error'):
        return utils.escape_markdown_v2(f"❌ خطای محاسباتی: {chart_data['error']}\n\n لطفاً دوباره امتحان کنید.")
        
    sun_info = chart_data.get('sun', {})
    moon_info = chart_data.get('moon', {})
    
    # خورشید
    if sun_info.get('error'):
        sun_error_text = sun_info['error'].replace('\n', ' ')
        sun_line = f"**خورشید (Sun)**: ❌ *خطا در محاسبه*: `{utils.escape_code_block(sun_error_text)}`"
    else:
        sun_pos_str = sun_info.get('position_str', 'نامعلوم')
        sun_line = f"**خورشید (Sun)**: {sun_info.get('sign_fa', 'نامعلوم')} در درجه {sun_pos_str}"
        
    # ماه
    if moon_info.get('error'):
        moon_error_text = moon_info['error'].replace('\n', ' ')
        moon_line = f"**ماه (Moon)**: ❌ *خطا در محاسبه*: `{utils.escape_code_block(moon_error_text)}`"
    else:
        moon_pos_str = moon_info.get('position_str', 'نامعلوم')
        moon_line = f"**ماه (Moon)**: {moon_info.get('sign_fa', 'نامعلوم')} در درجه {moon_pos_str}"
        
    
    summary = (
        f"🌟 *خلاصه چارت تولد شما* 🌟\n\n"
        f"**تاریخ تولد (شمسی)**: `{jdate.strftime('%Y/%m/%d')}`\n"
        f"**شهر تولد**: {city_name}\n"
        f"--- \n"
        f"{sun_line}\n"
        f"{moon_line}\n"
        f"--- \n"
        f"جهت مشاهده جزئیات بیشتر از دکمه‌های زیر استفاده کنید."
    )
    return utils.escape_markdown_v2(summary)


def format_planet_positions(chart_data: Dict[str, Any]) -> str:
    """تولید لیست موقعیت سیارات."""
    
    if not chart_data or chart_data.get('error'):
        return utils.escape_markdown_v2(f"❌ اطلاعات چارت موجود نیست: {chart_data.get('error', 'داده خالی')}")
        
    header = "🪐 *موقعیت سیارات در زمان تولد* 🪐\n\n"
    positions = []
    
    for planet_name in PLANETS:
        data = chart_data.get(planet_name, {})
        
        if data.get('error'):
            # نمایش خطای سیاره خاص
            error_text = data['error'].replace('\n', ' ')
            positions.append(f"• **{PLANET_SYMBOLS_FA.get(planet_name, planet_name)}**: ❌ (خطا: `{utils.escape_code_block(error_text)}`)")
            continue
            
        pos_line = (
            f"• **{data['name_fa']}**: "
            f"`{data['sign_fa']}` در درجه `{data['position_str']}`"
        )
        positions.append(pos_line)
        
    return utils.escape_markdown_v2(header + "\n".join(positions))
