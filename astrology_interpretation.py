# ----------------------------------------------------------------------
# astrology_interpretation.py - ماژول تفسیر عمیق‌تر (V4)
# ----------------------------------------------------------------------

from typing import Dict, Any, Tuple, Union
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
    "عقرب (Scorpio)": ("Mars", "Pluto"),
    "قوس (Sagittarius)": ("Jupiter", "Jupiter"),
    "جدی (Capricorn)": ("Saturn", "Saturn"),
    "دلو (Aquarius)": ("Saturn", "Uranus"),
    "حوت (Pisces)": ("Jupiter", "Neptune"),
}

# متن‌های تفسیری کوتاه برای زوایا
ASPECT_INTERPRETATIONS = {
    "Conjunction": " ادغام قدرت و انرژی، تاکید قوی بر ویژگی‌های مشترک آن‌ها.",
    "Sextile": " فرصت‌های آسان برای همکاری و سازگاری، یک جریان حمایتی ملایم.",
    "Square": " تنش، چالش و اصطکاک. این زاویه نیروی محرک اصلی برای تغییر است.",
    "Trine": " جریان انرژی هارمونیک و بدون زحمت، استعدادهای ذاتی و اقبال خوش.",
    "Opposition": " کشمکش و نیاز به تعادل بین دو بخش متضاد از شخصیت.",
}

# --- [بانک اطلاعاتی تفسیری] ---

PLANET_SIGN_INTERPRETATIONS = {
    "sun": {"اسد": "هویت شما با غرور، رهبری و نیاز به توجه گره خورده است. بسیار خلاق و مرکزگرا هستید."},
    "moon": {"قوس": "امنیت عاطفی از طریق جستجو، فلسفه و آزادی تأمین می‌شود. روحیه ماجراجو دارید."},
    "mercury": {"سنبله": "ذهن بسیار تحلیلی، متمرکز بر جزئیات و خدمات است. نیاز به مفید بودن دارید."},
    "venus": {"جوزا": "ارتباطات و تنوع برای شما در عشق و روابط بسیار مهم است. جذابیت شما از هوش می‌آید."},
    "mars": {"میزان": "انرژی و اقدام شما حول عدالت، تعادل و روابط دیپلماتیک می‌چرخد. از درگیری آشکار دوری می‌کنید."},
    "jupiter": {"سنبله": "رشد و شانس شما از طریق خدمات، سازماندهی و بهبود امور روزمره حاصل می‌شود."},
    "saturn": {"سنبله": "درس‌های کارما و مسئولیت شما در حوزه کار، سلامتی و کمال‌گرایی است. ساختارهای دقیق برای شما مهم است."},
}

PLANET_HOUSE_INTERPRETATIONS = {
    "sun": {7: "انرژی حیاتی شما متمرکز بر روابط یک به یک، شراکت و یافتن هویت از طریق دیگری است."},
    "moon": {10: "نیازهای عاطفی شما علنی است و در حوزه شغل، جاه‌طلبی و شهرت عمومی امنیت پیدا می‌کنید."},
    "mercury": {7: "ذهن و ارتباطات شما دائماً درگیر مسائل شراکتی، مشاوره و تعاملات اجتماعی مهم است."},
    "venus": {7: "ارزش‌ها و نحوه عشق‌ورزی شما از طریق تعاملات و روابط یک به یک تعریف می‌شود."},
    "mars": {8: "انرژی و عمل شما متوجه منابع مشترک، تحولات عمیق، امور پنهان و بحران‌ها است."},
    "saturn": {8: "مسئولیت‌ها و درس‌های سختی در مورد منابع مشترک، بدهی‌ها، و تحولات عمیق و مرگ دارید."},
}

RULER_IN_HOUSE_INTERPRETATIONS = {
    "h7_ruler_in_h8": "حاکم خانه روابط (۷) در خانه تحولات (۸) است. شرکا و روابط شما اغلب باعث تغییرات مالی یا روانی عمیق در زندگی‌تان می‌شوند. ممکن است روابطتان محرمانه یا شدید باشد.",
    "h10_ruler_in_h7": "حاکم خانه شغل (۱۰) در خانه روابط (۷) است. مسیر شغلی یا شهرت عمومی شما به شدت به شریک زندگی، همکاری‌ها یا مشتریان شما وابسته است. شما در کارهای مشارکتی موفق هستید.",
}


# --- [توابع کمکی] ---

def get_sign_and_degree(degree: float) -> str:
    """درجه را به فرمت 'X° Y' برج (Sign)' تبدیل می‌کند."""
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

def get_house_of_degree(degree: float, cusps: Dict[int, float]) -> int:
    """خانه ای که یک درجه مشخص در آن قرار دارد را پیدا می‌کند."""
    degree = degree % 360
    if len(cusps) < 12:
        return 0 
    
    for i in range(1, 13):
        start_cusp = cusps.get(i, 0.0)
        end_cusp = cusps.get(i % 12 + 1, cusps.get(1, 0.0)) # کاپس 13 همان کاپس 1 است
        
        if start_cusp < end_cusp:
            if start_cusp <= degree < end_cusp:
                return i
        else:
            # برای حالتی که کاپس از 360/0 عبور می‌کند
            if degree >= start_cusp or degree < end_cusp:
                return i
                
    return 0

def get_house_name(house_number: int) -> str:
    """شماره خانه را به نام فارسی آن تبدیل می‌کند."""
    return HOUSE_NAMES.get(house_number, "خانه نامشخص")

def get_sign_of_degree(degree: float) -> str:
    """استخراج نام برج فارسی و انگلیسی (مثلاً 'دلو (Aquarius)')"""
    return get_sign_and_degree(degree).split(maxsplit=2)[-1]


def get_chart_ruler_info(ascendant_degree: float) -> Tuple[str, str, str]:
    """اطلاعات حاکم چارت (آسندانت) را برمی‌گرداند."""
    asc_sign_full = get_sign_of_degree(ascendant_degree) 
    ruler_info = RULERSHIP.get(asc_sign_full, ("Unknown", "Unknown"))
    asc_sign_persian = asc_sign_full.split()[0]
    return asc_sign_persian, ruler_info[0], ruler_info[1]


# --- [توابع تفسیر عمیق جدید] ---

def get_house_ruler_placement(house_number: int, cusps: Dict[int, float], planets: Dict[str, Any]) -> Tuple[str, int]:
    """حاکم یک خانه مشخص و خانه ای که در آن قرار گرفته را پیدا می‌کند."""
    
    # 1. پیدا کردن برج کاپس خانه
    cusp_degree = cusps.get(house_number)
    if cusp_degree is None:
        return "Unknown", 0

    cusp_sign_full = get_sign_of_degree(cusp_degree)
    
    # 2. پیدا کردن حاکم سنتی آن برج
    trad_ruler = RULERSHIP.get(cusp_sign_full, ("Unknown", "Unknown"))[0]
    
    if trad_ruler == "Unknown":
        return "Unknown", 0
    
    # 3. پیدا کردن موقعیت حاکم (سیاره) در چارت
    ruler_planet_data = planets.get(trad_ruler.lower())
    if ruler_planet_data and 'degree' in ruler_planet_data:
        ruler_house_num = get_house_of_degree(ruler_planet_data['degree'], cusps)
        return trad_ruler, ruler_house_num
        
    return trad_ruler, 0


def interpret_planet_placement(planet_name: str, degree: float, cusps: Dict[int, float]) -> str:
    """تفسیر مختصر سیاره در برج و خانه."""
    
    planet_key = planet_name.lower()
    sign_full = get_sign_of_degree(degree)
    sign_persian = sign_full.split()[0]
    house_num = get_house_of_degree(degree, cusps)
    house_name = get_house_name(house_num)
    
    # استخراج تفسیرهای از پیش تعریف شده
    sign_interp = PLANET_SIGN_INTERPRETATIONS.get(planet_key, {}).get(sign_persian, "")
    house_interp = PLANET_HOUSE_INTERPRETATIONS.get(planet_key, {}).get(house_num, "")
    
    if not sign_interp and not house_interp:
        return f"**{get_sign_and_degree(degree)}** در {house_name}. تفسیر جامع یافت نشد."

    # ترکیب و بازگشت
    full_interp = f"**{sign_persian}** ({get_sign_and_degree(degree)}) در {house_name}: "
    if sign_interp:
        full_interp += f"*{sign_interp}* "
    if house_interp:
        full_interp += f"*{house_interp}*"
        
    return full_interp


def interpret_part_of_fortune(pf_data: Dict[str, Any], cusps: Dict[int, float]) -> str:
    """تفسیر سهم سعادت (Part of Fortune)"""
    
    if 'error' in pf_data:
        return pf_data['error']
        
    pf_degree = pf_data['degree']
    pf_sign_full = get_sign_of_degree(pf_degree)
    pf_sign_persian = pf_sign_full.split()[0]
    pf_house_num = get_house_of_degree(pf_degree, cusps)
    pf_house_name = get_house_name(pf_house_num)
    pf_sign_and_degree = get_sign_and_degree(pf_degree)
    
    # تفسیر ساده (نیاز به بانک اطلاعاتی جامع‌تر دارد)
    base_interp = f"سهم سعادت (نقطه بخت) شما در **{pf_sign_persian}** در **{pf_house_name}** قرار دارد."
    fortune_interp = "این نقطه نشان‌دهنده جایی است که شما به راحتی جریان انرژی و شانس را تجربه می‌کنید."
    
    if pf_house_num in [1, 10]:
        fortune_interp = "این جایگیری نشان‌دهنده اقبال و موفقیت محسوس در حوزه‌ی خود و شهرت عمومی است."
    elif pf_house_num in [7, 8]:
         fortune_interp = "شادی و موفقیت شما گره‌خورده به روابط مهم و منابع مشترک یا تحولات عمیق است."
    elif pf_house_num in [4, 5]:
        fortune_interp = "شادی و رفاه شما از طریق خانه، خانواده، خلاقیت و فرزندان تأمین می‌شود."
        
    return f"**سهم سعادت:** {pf_sign_and_degree} ({pf_house_name}). {base_interp} {fortune_interp}"
    

# --- [منطق اصلی تفسیر] ---

def interpret_natal_chart(chart_data: Dict[str, Any]) -> str:
    
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

    ruler_degree = planets.get(trad_ruler.lower(), {}).get('degree')
    ruler_house = 0
    ruler_placement_text = "نامشخص"
    
    if ruler_degree is not None:
        ruler_house = get_house_of_degree(ruler_degree, cusps)
        ruler_house_name = get_house_name(ruler_house)
        ruler_placement_text = f"{get_sign_of_degree(ruler_degree).split()[0]} در {ruler_house_name}"
        
    
    interpretation = [
        "✨ **تفسیر عمیق چارت تولد (نسخه V4 - حاکمیت فرعی و سهم سعادت)**",
        "------------------------------------",
        f"⬆️ **آسندانت (شخصیت ظاهری):** {ascendant_sign}",
        f"    *تفسیر کوتاه:* آسندانت در {asc_sign_persian}، تصویری است که شما به جهان ارائه می‌دهید و نشان‌دهنده ظاهر و اولین واکنش شماست.",
        "",
        f"👑 **حاکم چارت (Chart Ruler):** {trad_ruler} (سنتی)",
        f"    *حاکمیت:* {trad_ruler} سیاره حاکم بر برج {asc_sign_persian} است و نماینده هدف اصلی شخصیت شماست.",
        f"    *موقعیت حاکم:* {trad_ruler} در {ruler_placement_text}",
        f"    *تأثیر:* تمرکز انرژی و هویت شما در حوزه‌ی {get_house_name(ruler_house)} قرار دارد، که بر تمامی شخصیت شما حاکم است.",
        "",
        "--- **تفسیر جامع سیارات اصلی (برج + خانه)** ---",
    ]
    
    # 3. تفسیر جامع سیارات اصلی (Sign + House)
    key_planets = ["sun", "moon", "mercury", "venus", "mars"]
    for p_key in key_planets:
        p_data = planets.get(p_key)
        if p_data and 'degree' in p_data:
            p_title = ""
            if p_key == "sun": p_title = "🌟 خورشید (هویت):"
            elif p_key == "moon": p_title = "🌙 ماه (احساسات):"
            elif p_key == "mercury": p_title = "🧠 عطارد (تفکر):"
            elif p_key == "venus": p_title = "💖 زهره (عشق و ارزش):"
            elif p_key == "mars": p_title = "🔥 مریخ (انرژی و عمل):"

            interpretation.append(f"{p_title} {interpret_planet_placement(p_key, p_data['degree'], cusps)}")
    
    interpretation.append("\n--- **حاکمیت فرعی خانه‌ها (Sub-Rulership)** ---")
    
    # 4. تفسیر حاکمیت فرعی خانه‌ها (خانه ۷ و ۱۰)
    
    # حاکم خانه ۷ (روابط)
    h7_ruler, h7_ruler_house = get_house_ruler_placement(7, cusps, planets)
    h7_ruler_house_name = get_house_name(h7_ruler_house)
    h7_interp_key = f"h7_ruler_in_h{h7_ruler_house}"
    h7_interp = RULER_IN_HOUSE_INTERPRETATIONS.get(h7_interp_key, f"حاکم روابط ({h7_ruler}) در {h7_ruler_house_name} است. تفسیر خاصی تعریف نشده است.")

    interpretation.append(f"**حاکم خانه روابط (۷):** {h7_ruler} در {h7_ruler_house_name}")
    interpretation.append(f"    *{h7_interp}*")


    # حاکم خانه ۱۰ (شغل)
    h10_ruler, h10_ruler_house = get_house_ruler_placement(10, cusps, planets)
    h10_ruler_house_name = get_house_name(h10_ruler_house)
    h10_interp_key = f"h10_ruler_in_h{h10_ruler_house}"
    h10_interp = RULER_IN_HOUSE_INTERPRETATIONS.get(h10_interp_key, f"حاکم شغل ({h10_ruler}) در {h10_ruler_house_name} است. تفسیر خاصی تعریف نشده است.")

    interpretation.append(f"**حاکم خانه شغل (۱۰):** {h10_ruler} در {h10_ruler_house_name}")
    interpretation.append(f"    *{h10_interp}*")


    interpretation.append("\n--- **نقاط عربی (Part of Fortune)** ---")
    
    # 5. تفسیر سهم سعادت (Part of Fortune)
    pf_data = chart_data.get('arabic_parts', {}).get('part_of_fortune', {})
    if pf_data:
        interpretation.append(interpret_part_of_fortune(pf_data, cusps))
    else:
        interpretation.append("❌ سهم سعادت در چارت محاسبه یا یافت نشد.")


    interpretation.append("\n--- **زوایای اصلی (Aspects)** ---")
    # 6. زوایا
    aspects = chart_data.get('aspects', [])
    if aspects:
        interpretation.append("این بخش مهم‌ترین ترکیب‌های انرژی در چارت شما را نشان می‌دهد:")
        for asp in aspects:
            p1 = asp['p1']
            p2 = asp['p2']
            aspect_name = asp['aspect']
            orb = asp['orb']
            
            interpretation_text = ASPECT_INTERPRETATIONS.get(aspect_name, "")
            
            interpretation.append(
                f"**{p1} {aspect_name} {p2}** ({orb:.2f} Orb):"
                f"*{interpretation_text}*"
            )
    else:
        interpretation.append("زوایای اصلی (Aspects) با Orb تنگ در چارت یافت نشدند.")

    interpretation.append("\n**توجه:** این تفسیر همچنان یک خلاصه است. تحلیل کامل نیاز به بررسی حاکمیت‌های فرعی و نقاط عربی دارد.")
    
    return "\n".join(interpretation)
