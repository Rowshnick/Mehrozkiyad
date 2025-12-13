import numpy as np
import matplotlib.pyplot as plt
import math
from typing import Dict, Any, List, Tuple, Union
import io
import matplotlib.font_manager as fm
import logging

logging.basicConfig(level=logging.INFO)

# 💥💥💥 تغییر حیاتی: ساده‌سازی تنظیم فونت برای جلوگیری از کرش در زمان Import 💥💥💥
try:
    # 1. تلاش برای استفاده از فونت 'sans-serif' که معمولاً در تصاویر Docker بیس وجود دارد.
    # این کار احتمال کرش ناشی از fm.findSystemFonts را از بین می‌برد.
    plt.rcParams['font.family'] = 'sans-serif'
    
    # 2. تنظیم فونت جایگزین برای Matplotlib (که حروف یونیکد و نمادها را بهتر نمایش دهد)
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Tahoma', 'Arial', 'sans-serif']
    
    # 3. برای اطمینان از نمایش نمادهای نجومی:
    plt.rcParams['mathtext.fontset'] = 'custom'
    
except Exception as e:
    logging.error(f"Font setup error: {e}. Using default fallback.")
    plt.rcParams['font.family'] = 'DejaVu Sans' 
# ------------------------------------


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


    # 2. رسم و بر
