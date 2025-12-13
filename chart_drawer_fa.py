import matplotlib.font_manager as fm

# سعی می‌کنیم یک فونت فارسی رایج را پیدا و استفاده کنیم
try:
    # این نام‌ها باید با نام فونت نصب شده در محیط شما تطبیق داده شوند.
    # در محیط‌های توسعه، ممکن است نیاز به نصب دستی فونت داشته باشید.
    font_files = fm.findSystemFonts(fontpaths=['/usr/share/fonts/truetype/'])
    vazir_font = next((f for f in font_files if 'Vazirmatn' in f or 'B_Nazanin' in f), None)
    
    if vazir_font:
        font_prop = fm.FontProperties(fname=vazir_font)
        # تنظیم فونت به عنوان فونت پیش‌فرض
        plt.rcParams['font.family'] = font_prop.get_name()
    else:
        # اگر فونت فارسی یافت نشد، از یک فونت عمومی استفاده می‌کنیم (ممکن است حروف از هم جدا شوند)
        plt.rcParams['font.family'] = 'DejaVu Sans'
except Exception as e:
    print(f"Font setup error: {e}")
    plt.rcParams['font.family'] = 'DejaVu Sans'

import numpy as np
import matplotlib.pyplot as plt
import math
from typing import Dict, Any, List, Tuple, Union
import io
import matplotlib.font_manager as fm

# --- تنظیم فونت فارسی (مهم) ---
# برای نمایش صحیح حروف فارسی و جهت‌دهی (RTL) در Matplotlib
try:
    # تلاش برای یافتن فونت فارسی (مثل Vazirmatn یا B Nazanin)
    # توجه: در محیط Docker یا سرور، باید مطمئن شوید که این فونت‌ها نصب شده‌اند.
    font_files = fm.findSystemFonts(fontpaths=['/usr/share/fonts/truetype/'])
    vazir_font = next((f for f in font_files if 'Vazirmatn' in f or 'BNazanin' in f), None)
    
    if vazir_font:
        font_prop = fm.FontProperties(fname=vazir_font)
        plt.rcParams['font.family'] = font_prop.get_name()
    else:
        # اگر فونت فارسی یافت نشد (مثلاً در یک محیط بدون فونت نصب‌شده)،
        # از یک فونت عمومی استفاده می‌کنیم که ممکن است حروف را جدا نمایش دهد.
        print("Warning: Farsi font not found. Using default font.")
        plt.rcParams['font.family'] = 'DejaVu Sans'
        
except Exception as e:
    print(f"Font setup error: {e}. Using default font.")
    plt.rcParams['font.family'] = 'DejaVu Sans'

# --- 1. نمادها و ثابت‌های گرافیکی فارسی ---

# نام و نماد برج‌های فلکی (Zodiac Signs) - نام‌ها برای برچسب‌گذاری
SIGN_NAMES_FA = [
    'حمل ♈', 'ثور ♉', 'جوزا ♊', 'سرطان ♋', 'اسد ♌', 'سنبله ♍', 
    'میزان ♎', 'عقرب ♏', 'قوس ♐', 'جدی ♑', 'دلو ♒', 'حوت ♓'
]

# نمادهای Unicode برای سیارات و نقاط
PLANET_SYMBOLS = {
    'sun': '☉', 'moon': '☽', 'mercury': '☿', 'venus': '♀', 'mars': '♂',
    'jupiter': '♃', 'saturn': '♄', 'uranus': '⛢', 'neptune': '♆', 'pluto': '♇',
    'true_node': '☊', 'part_of_fortune': '⨳'
}

# نام‌های فارسی برای سیارات (برای لیبل‌های بیرونی یا لیست)
PLANET_NAMES_FA = {
    'sun': 'خورشید', 'moon': 'ماه', 'mercury': 'عطارد', 'venus': 'زهره', 'mars': 'مریخ',
    'jupiter': 'مشتری', 'saturn': 'زحل', 'uranus': 'اورانوس', 'neptune': 'نپتون', 'pluto': 'پلوتو',
    'true_node': 'گره شمالی', 'part_of_fortune': 'سهم سعادت'
}

# نام‌های فارسی برای زوایا (Aspects)
ASPECT_NAMES_FA = {
    "Conjunction": 'اتصال',  # 0°
    "Sextile": 'تثلیث کوچک',# 60°
    "Square": 'تربیع',      # 90°
    "Trine": 'تثلیث',       # 120°
    "Opposition": 'مقابله',  # 180°
}

# رنگ‌های استاندارد برای زوایا (Aspects)
ASPECT_COLORS = {
    "Conjunction": 'black', 
    "Sextile": 'blue',      
    "Square": 'red',        
    "Trine": 'green',       
    "Opposition": 'orange', 
}

# --- 2. توابع کمکی ---

def degree_to_radians(degree: float) -> float:
    """تبدیل درجه نجومی (0=حمل) به رادیان برای مختصات قطبی (0=شرق)."""
    return math.radians(90 - degree)

def pol2cart(rho: float, phi_rad: float) -> Tuple[float, float]:
    """تبدیل مختصات قطبی (فاصله، رادیان) به کارتزین (x, y)."""
    x = rho * np.cos(phi_rad)
    y = rho * np.sin(phi_rad)
    return x, y

def get_sign_index(degree: float) -> int:
    """درجه را به ایندکس برج (0 تا 11) تبدیل می‌کند."""
    return int(degree // 30)

def get_degree_in_sign(degree: float) -> str:
    """محاسبه درجه درون برج و بازگرداندن به شکل '25° 30''"""
    deg_in_sign = degree % 30
    minutes = (deg_in_sign - int(deg_in_sign)) * 60
    return f"{int(deg_in_sign)}° {int(minutes)}'"

# --- 3. تابع اصلی ترسیم چارت ---

def draw_chart_wheel_fa(chart_data: Dict[str, Any]) -> io.BytesIO:
    """
    نمودار دایره‌ای چارت تولد را با برچسب‌های فارسی رسم می‌کند.

    بازگشت: یک شیء باینری (BytesIO) حاوی تصویر PNG.
    """
    
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': 'polar'})
    ax.set_theta_zero_location("W")  # 0 درجه در سمت چپ (غرب/آسندانت) قرار می‌گیرد
    ax.set_theta_direction(-1)       # چرخش ساعتگرد (جهت استاندارد نجومی)
    ax.set_xticks(np.deg2rad(np.arange(0, 360, 30))) 
    ax.set_xticklabels([]) 
    ax.set_yticks([]) 
    ax.set_ylim(0, 1.2) 

    # --- متغیرهای شعاعی ---
    R_ZODIAC = 1.0     # شعاع دایره بیرونی (برج‌ها)
    R_HOUSES = 0.8     # شعاع دایره داخلی (خانه‌ها)
    R_PLANETS = 0.6    # شعاع حلقه سیارات
    R_ASPECTS = 0.4    # شعاع داخلی برای رسم زوایا (Aspects)

    # 1. رسم دایره‌های اصلی
    ax.plot(np.linspace(0, 2*np.pi, 100), np.full(100, R_ZODIAC), color='gray', linewidth=1)
    ax.plot(np.linspace(0, 2*np.pi, 100), np.full(100, R_HOUSES), color='black', linewidth=1.5)
    # دایره داخلی برای زوایا
    ax.plot(np.linspace(0, 2*np.pi, 100), np.full(100, R_ASPECTS), color='gray', linestyle='--', linewidth=0.5)


    # 2. رسم و برچسب‌گذاری برج‌ها (Zodiac Signs)
    for i in range(12):
        sign_start_deg = i * 30
        
        # رسم خطوط مرزی برج‌ها
        ax.plot([degree_to_radians(sign_start_deg), degree_to_radians(sign_start_deg)], [R_HOUSES, R_ZODIAC], color='gray', linestyle='-', linewidth=0.5)
        
        # قرار دادن نام و نماد فارسی برج در مرکز آن سگمنت
        sign_center_deg = sign_start_deg + 15
        sign_center_rad = degree_to_radians(sign_center_deg)
        ax.text(sign_center_rad, R_ZODIAC + 0.1, SIGN_NAMES_FA[i], 
                ha='center', va='center', fontsize=12, fontweight='bold')


    # 3. رسم خانه‌ها (Houses Cusps)
    cusps = chart_data['houses']['cusps']
    
    # آسندانت و دایسندانت (خانه 1 و 7)
    asc_deg = chart_data['houses']['ascendant']
    if asc_deg:
        asc_rad = degree_to_radians(asc_deg)
        ax.plot([asc_rad, asc_rad], [0, R_ZODIAC], color='red', linewidth=1.5, linestyle='-')
        # برچسب Asc/Dsc
        ax.text(asc_rad, R_HOUSES - 0.05, 'طالع', ha='center', va='center', fontsize=10, color='red')
        # Descendant (مقابله Ascendant)
        dsc_rad = degree_to_radians((asc_deg + 180) % 360)
        ax.plot([dsc_rad, dsc_rad], [0, R_ZODIAC], color='red', linewidth=1.5, linestyle='--')
        ax.text(dsc_rad, R_HOUSES - 0.05, 'غروب', ha='center', va='center', fontsize=10, color='red')
        
    # مدهاون و ایموم کوئلی (خانه 10 و 4)
    mc_deg = chart_data['houses']['midheaven']
    if mc_deg:
        mc_rad = degree_to_radians(mc_deg)
        ax.plot([mc_rad, mc_rad], [0, R_ZODIAC], color='red', linewidth=1.5, linestyle='-')
        ax.text(mc_rad, R_HOUSES - 0.05, 'وسط آسمان', ha='center', va='center', fontsize=10, color='red')
        # Imum Coeli (مقابله MC)
        ic_rad = degree_to_radians((mc_deg + 180) % 360)
        ax.plot([ic_rad, ic_rad], [0, R_ZODIAC], color='red', linewidth=1.5, linestyle='--')
        ax.text(ic_rad, R_HOUSES - 0.05, 'قاع آسمان', ha='center', va='center', fontsize=10, color='red')
        
    # رسم سایر کاپس‌ها (2، 3، 5، 6، 8، 9، 11، 12)
    for house_num, degree in cusps.items():
        if house_num not in [1, 4, 7, 10] and degree is not None and 1 <= house_num <= 12:
            house_rad = degree_to_radians(degree)
            # خطوط کاپس را بین دایره‌های خانه‌ها و برج‌ها می‌کشیم
            ax.plot([house_rad, house_rad], [R_HOUSES, R_ZODIAC], color='black', linewidth=0.8, linestyle='--')
            
            # قرار دادن شماره خانه در داخل چارت
            # برای برچسب‌گذاری خانه، موقعیت خانه بعدی را پیدا کرده و وسط آن رسم می‌کنیم
            next_house_deg = cusps.get(house_num % 12 + 1, cusps[1]) # خانه بعدی
            
            # محاسبه مرکز سگمنت خانه
            center_deg = (degree + next_house_deg) / 2
            if next_house_deg < degree: # اگر از 360 رد شده باشد
                center_deg = (degree + next_house_deg + 360) / 2
                center_deg %= 360
                
            center_rad = degree_to_radians(center_deg)
            
            # رسم عدد فارسی خانه
            ax.text(center_rad, R_HOUSES - 0.05, f"خانه {str(house_num).translate(str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹'))}",
                    ha='center', va='center', fontsize=9, color='black', fontweight='bold')


    # 4. رسم سیارات و نقاط (Planets and Points)
    planets = chart_data['planets']
    if 'part_of_fortune' in chart_data['arabic_parts']:
        planets['part_of_fortune'] = chart_data['arabic_parts']['part_of_fortune']
        
    # برای جلوگیری از تداخل، موقعیت شعاعی هر سیاره را کمی تغییر می‌دهیم
    planet_positions: Dict[str, float] = {}
    for name, data in planets.items():
        if 'degree' in data:
            planet_positions[name] = data['degree']

    # مرتب‌سازی سیارات بر اساس درجه برای تصمیم‌گیری بهتر در مورد آفست
    sorted_planets = sorted(planet_positions.items(), key=lambda item: item[1])

    # منطق ساده آفست برای جلوگیری از هم‌پوشانی
    current_offset_level = 0
    previous_degree = -100

    for planet_name, degree in sorted_planets:
        rad = degree_to_radians(degree)
        symbol = PLANET_SYMBOLS.get(planet_name, '?')
        
        # اگر سیاره جدید نزدیک سیاره قبلی است (مثلاً در 5 درجه):
        if abs(degree - previous_degree) < 5:
            current_offset_level += 0.03
        else:
            current_offset_level = 0
        
        offset_rad = R_PLANETS + current_offset_level
        previous_degree = degree
        
        # رسم نماد سیاره
        ax.text(rad, offset_rad, symbol, 
                ha='center', va='center', fontsize=16, color='darkblue', fontweight='bold')
        
        # درج درجه درون برج (اختیاری، کمی پیچیده است)
        # degree_text = get_degree_in_sign(degree)
        # ax.text(rad, offset_rad + 0.02, degree_text, 
        #         ha='center', va='center', fontsize=7, color='black')


    # 5. رسم زوایا (Aspects) در مرکز چارت
    aspects = chart_data.get('aspects', [])
    
    # برای جلوگیری از هم‌پوشانی خطوط زوایا، شعاع شروع را کمی برای هر خط تغییر می‌دهیم
    aspect_r_start = R_ASPECTS
    
    # برای هر زاویه یک خط از سیاره 1 به سیاره 2 در دایره داخلی رسم کنید
    for i, aspect in enumerate(aspects):
        p1_name = aspect['p1'].lower().replace(" ", "_")
        p2_name = aspect['p2'].lower().replace(" ", "_")
        
        p1_deg = planet_positions.get(p1_name)
        p2_deg = planet_positions.get(p2_name)
        
        if p1_deg is not None and p2_deg is not None:
            p1_rad = degree_to_radians(p1_deg)
            p2_rad = degree_to_radians(p2_deg)
            
            color = ASPECT_COLORS.get(aspect['aspect'], 'gray')
            
            # محاسبه شعاع خط فعلی (هرچه نزدیک‌تر به مرکز، خط بعدی)
            r_current = aspect_r_start - (i * 0.005) # آفست 0.005 برای هر خط
            
            # رسم خطوط شعاعی که زوایا را نشان می‌دهند
            # این خطوط صاف نیستند و در داخل محیط polar به صورت منحنی نمایش داده می‌شوند
            ax.plot([p1_rad, p2_rad], [r_current, r_current], color=color, linewidth=0.7, alpha=0.8)
            
            # برچسب فارسی زاویه در مرکز خط (برای زوایای مهم‌تر)
            if aspect['aspect'] in ["Square", "Trine", "Opposition"]:
                mid_rad = (p1_rad + p2_rad) / 2
                
                # برای مقابله (180 درجه)، باید میانگین را درست محاسبه کرد
                if abs(p1_deg - p2_deg) > 180:
                    mid_rad = (p1_rad + p2_rad + 2*np.pi) / 2
                    
                ax.text(mid_rad, r_current + 0.01, ASPECT_NAMES_FA[aspect['aspect']], 
                        ha='center', va='center', fontsize=6, color=color)

    # 6. عنوان چارت در مرکز
    title_text = f"چارت تولد: {chart_data['city_name']}\n{chart_data['date_time_jalali']} {chart_data['time_str']}"
    ax.text(0, 0, title_text, ha='center', va='center', fontsize=12, color='darkred', fontweight='bold')
    
    # 7. ذخیره تصویر
    plt.tight_layout()
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', transparent=True, dpi=150) # dpi بالاتر برای کیفیت بهتر
    plt.close(fig)
    buffer.seek(0)
    
    return buffer

# --- نحوه استفاده (مثال) ---

def example_usage_fa(chart_data: Dict[str, Any]):
    """مثال: یک تابع نمونه برای فراخوانی تابع ترسیم فارسی."""
    
    try:
        image_buffer = draw_chart_wheel_fa(chart_data)
        
        print("✅ تصویر چارت فارسی با موفقیت تولید و در حافظه ذخیره شد.")
        
        # برای تست محلی
        # with open("natal_chart_fa.png", "wb") as f:
        #     f.write(image_buffer.read())

    except Exception as e:
        print(f"❌ خطای ترسیم چارت فارسی: {e}")

