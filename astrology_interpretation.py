# ----------------------------------------------------------------------
# astrology_interpretation.py - ماژول تفسیر عمیق‌تر چارت تولد
# ----------------------------------------------------------------------

from typing import Dict, Any, Tuple
import math

# --- [ثابت‌ها و تعاریف] ---

ZODIAC_SIGNS = {
    0: "حمل (Aries)", 30: "ثور (Taurus)", 60: "جوزا (Gemini)", 90: "سرطان (Cancer)",
    120: "اسد (Leo)", 150: "سنبله (Virgo)", 180: "میزان (Libra)", 210: "عقرب (Scorpio)",
    240: "قوس (Sagittarius)", 270: "جدی (Capricorn)", 300: "دلو (Aquarius)", 330: "حوت (Pisces)"
}

HOUSE_NAMES = {
    1: "خانه اول (شخصیت و ظاهر)", 2: "خانه دوم (مال و ارزش‌ها)", 
    3: "خانه سوم (ارتباطات و یادگیری)", 4: "خانه چهارم (خانه و خانواده)",
    5: "خانه پنجم (خلاقیت و عشق)", 6: "خانه ششم (سلامت و کار روزمره)",
    7: "خانه هفتم (روابط و ازدواج)", 8: "خانه هشتم (تغییر و منابع مشترک)",
    9: "خانه نهم (سفر و فلسفه)", 10: "خانه دهم (شغل و شهرت)",
    11: "خانه یازدهم (گروه‌ها و آرزوها)", 12: "خانه دوازدهم (خلوت و ناخودآگاه)"
}

# حاکمیت سیارات (برج: (سنتی، مدرن))
RULERSHIP = {
    "حمل (Aries)": ("Mars", "Mars"),
    "ثور (Taurus)": ("Venus", "Venus"),
    "جوزا (Gemini)": ("Mercury", "Mercury"),
    "سرطان (Cancer)": ("Moon", "Moon"),
    "اسد (Leo)": ("Sun", "Sun"),
    "سنبله (Virgo)": ("Mercury", "Mercury"),
    "میزان (Libra)": ("Venus", "Venus"),
    "عقرب (Scorpio)": ("Mars", "Pluto"), # Mars سنتی، Pluto مدرن
    "قوس (Sagittarius)": ("Jupiter", "Jupiter"),
    "جدی (Capricorn)": ("Saturn", "Saturn"),
    "دلو (Aquarius)": ("Saturn", "Uranus"), # Saturn سنتی، Uranus مدرن
    "حوت (Pisces)": ("Jupiter", "Neptune"), # Jupiter سنتی، Neptune مدرن
}

# متن‌های تفسیری کوتاه برای زوایا (بسیار ساده شده برای مثال)
ASPECT_INTERPRETATIONS = {
    "Conjunction": " ادغام قدرت و انرژی، تاکید قوی بر ویژگی‌های مشترک آن‌ها.",
    "Sextile": " فرصت‌های آسان برای همکاری و سازگاری، یک جریان حمایتی ملایم.",
    "Square": " تنش، چالش و اصطکاک. این زاویه نیروی محرک اصلی برای تغییر است.",
    "Trine": " جریان انرژی هارمونیک و بدون زحمت، استعدادهای ذاتی و اقبال خوش.",
    "Opposition": " کشمکش و نیاز به تعادل بین دو بخش متضاد از شخصیت.",
}

# --- [توابع کمکی] ---

def get_sign_and_degree(degree: float) -> str:
    """درجه را به فرمت '15 درجه جوزا' تبدیل می‌کند."""
    
    degree = degree % 360 
    start_degrees = sorted(ZODIAC_SIGNS.keys())
    
    sign_start_degree = 0
    for start_deg in start_degrees:
        if degree >= start_deg:
            sign_start_degree = start_deg
        else:
            break
            
    sign_name = ZODIAC_SIGNS[sign_start_degree]
    degree_in_sign = degree - sign_start_degree
    
    deg_int = int(degree_in_sign)
    min_int = int((degree_in_sign - deg_int) * 60)
    
    return f"{deg_int}° {min_int}' {sign_name}"

def get_house_of_degree(degree: float, cusps: Dict[int, float]) -> str:
    """موقعیت یک درجه مشخص را در چارت خانه‌ها پیدا می‌کند."""
    
    degree = degree % 360
    if len(cusps) < 12:
        return "N/A (Cusps Missing)" 
    
    for i in range(1, 13):
        start_cusp = cusps.get(i, 0.0)
        end_cusp = cusps.get(i % 12 + 1, 0.0) 
        
        if start_cusp < end_cusp:
            if start_cusp <= degree < end_cusp:
                return HOUSE_NAMES[i]
        else:
            if degree >= start_cusp or degree < end_cusp:
                return HOUSE_NAMES[i]
                
    return "N/A (Logic Error)"


def get_chart_ruler_info(ascendant_degree: float) -> Tuple[str, str, str]:
    """تعیین برج آسندانت و حاکمان سنتی و مدرن آن."""
    
    # استخراج برج کامل (مثلاً 'دلو (Aquarius)')
    asc_sign_full = get_sign_and_degree(ascendant_degree).split(maxsplit=2)[-1] 
    
    ruler_info = RULERSHIP.get(asc_sign_full, ("Unknown", "Unknown"))
    
    # نام فارسی برج
    asc_sign_persian = asc_sign_full.split()[0]
    
    return asc_sign_persian, ruler_info[0], ruler_info[1] # Sign, Traditional, Modern

# --- [منطق اصلی تفسیر] ---

def interpret_natal_chart(chart_data: Dict[str, Any]) -> str:
    """تفسیر اصلی چارت را بر اساس سیارات، خانه‌ها و زوایا ایجاد می‌کند."""
    
    houses_data = chart_data.get('houses', {})
    planets = chart_data['planets']
    cusps = houses_data.get('cusps', {})
    
    # 1. مدیریت خطای محاسبه خانه‌ها
    houses_error = houses_data.get('error')
    if houses_error:
        return (
            "❌ **خطای محاسبه:** محاسبات موقعیت خانه‌ها موفقیت‌آمیز نبود.\n"
            f"جزئیات خطا: `{houses_error}`\n"
            "لطفاً با توسعه‌دهنده تماس بگیرید. تفسیر ناقص خواهد بود."
        )

    # 2. اطلاعات اولیه و حاکم چارت
    ascendant_degree = houses_data.get('ascendant', 0.0)
    ascendant_sign = get_sign_and_degree(ascendant_degree)
    
    asc_sign_persian, trad_ruler, mod_ruler = get_chart_ruler_info(ascendant_degree)

    # پیدا کردن موقعیت حاکم چارت
    ruler_placement = "نامشخص"
    ruler_degree = planets.get(trad_ruler.lower(), {}).get('degree')
    
    if ruler_degree is not None:
        ruler_house = get_house_of_degree(ruler_degree, cusps)
        ruler_placement = f"{get_sign_and_degree(ruler_degree).split()[0]} در {ruler_house}"
        
    
    interpretation = [
        "**تفسیر اولیه چارت تولد**",
        "------------------------------------",
        f"⬆️ **آسندانت (شخصیت ظاهری):** {ascendant_sign}",
        f"    *تفسیر کوتاه:* آسندانت در {asc_sign_persian}، تصویری است که شما به جهان ارائه می‌دهید و نشان‌دهنده ظاهر و اولین واکنش شماست.",
        "",
        f"👑 **حاکم چارت (Chart Ruler):** {trad_ruler} (سنتی)",
        f"    *حاکمیت:* {trad_ruler} سیاره حاکم بر برج {asc_sign_persian} است و نماینده هدف اصلی شخصیت شماست.",
        f"    *موقعیت حاکم:* {trad_ruler} در {ruler_placement}",
        f"    *تأثیر:* تمرکز انرژی و هویت شما در حوزه‌ی {ruler_house} قرار دارد، که بر تمامی شخصیت شما حاکم است.",
        "",
        "--- **سیارات اصلی** ---",
        f"🌟 **خورشید (هویت):** {get_sign_and_degree(planets['sun']['degree']).split()[0]} در {get_house_of_degree(planets['sun']['degree'], cusps)}",
        f"🌙 **ماه (احساسات):** {get_sign_and_degree(planets['moon']['degree']).split()[0]} در {get_house_of_degree(planets['moon']['degree'], cusps)}",
        f"🧠 **عطارد (تفکر):** {get_sign_and_degree(planets['mercury']['degree']).split()[0]} در {get_house_of_degree(planets['mercury']['degree'], cusps)}",
        
        "",
        "--- **زوایای اصلی (Aspects)** ---",
    ]
    
    # 3. تفسیر زوایا
    aspects = chart_data.get('aspects', [])
    if aspects:
        interpretation.append("این بخش مهم‌ترین ترکیب‌های انرژی در چارت شما را نشان می‌دهد:")
        for asp in aspects:
            p1 = asp['p1']
            p2 = asp['p2']
            aspect_name = asp['aspect']
            orb = asp['orb']
            
            # پیدا کردن تفسیر مختصر
            interpretation_text = ASPECT_INTERPRETATIONS.get(aspect_name, "")
            
            interpretation.append(
                f"**{p1} {aspect_name} {p2}** ({orb:.2f} Orb):"
                f"*{interpretation_text}*"
            )
    else:
        interpretation.append("زوایای اصلی (Aspects) با Orb تنگ در چارت یافت نشدند.")

    interpretation.append("\n**توجه:** این تفسیر همچنان یک خلاصه است. تحلیل کامل نیاز به بررسی حاکمیت‌های فرعی و نقاط عربی دارد.")
    
    return "\n".join(interpretation)
