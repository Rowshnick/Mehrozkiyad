import logging
from typing import Dict, Optional, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ----------------------------------------------------------------------
# پایگاه داده محلی شهرهای پرتکرار ایران (Cache)
# ----------------------------------------------------------------------

# 💥 توجه: شما می‌توانید شهرهای بیشتری را به این لیست اضافه کنید.
LOCAL_CITY_DB: Dict[str, Dict[str, Any]] = {
    # کلیدها باید به حروف کوچک و بدون فاصله تبدیل شوند برای جستجوی مقاوم
    "تهران": {"latitude": 35.6892, "longitude": 51.3890, "timezone": "Asia/Tehran"},
    "مشهد": {"latitude": 36.2605, "longitude": 59.6168, "timezone": "Asia/Tehran"},
    "اصفهان": {"latitude": 32.6546, "longitude": 51.6679, "timezone": "Asia/Tehran"},
    "تبریز": {"latitude": 38.0806, "longitude": 46.2919, "timezone": "Asia/Tehran"},
    "شیراز": {"latitude": 29.6037, "longitude": 52.5332, "timezone": "Asia/Tehran"},
    "اهواز": {"latitude": 31.3168, "longitude": 48.6749, "timezone": "Asia/Tehran"},
    "کرج": {"latitude": 35.8423, "longitude": 50.9770, "timezone": "Asia/Tehran"},
    "قم": {"latitude": 34.6418, "longitude": 50.8752, "timezone": "Asia/Tehran"},
    "اراک": {"latitude": 34.0863, "longitude": 49.6894, "timezone": "Asia/Tehran"},
    "کرمان": {"latitude": 30.2832, "longitude": 57.0620, "timezone": "Asia/Tehran"},
    "رشت": {"latitude": 37.2801, "longitude": 49.5888, "timezone": "Asia/Tehran"},
    "زنجان": {"latitude": 36.6746, "longitude": 48.4900, "timezone": "Asia/Tehran"},
    "همدان": {"latitude": 34.8066, "longitude": 48.5160, "timezone": "Asia/Tehran"},
    "یزد": {"latitude": 31.8973, "longitude": 54.3686, "timezone": "Asia/Tehran"},
    "ساری": {"latitude": 36.5658, "longitude": 53.0560, "timezone": "Asia/Tehran"},
}


# ----------------------------------------------------------------------
# تابع اصلی جستجوی مختصات (با اولویت محلی)
# ----------------------------------------------------------------------

def get_coordinates_from_city(city_name: str) -> Optional[Dict[str, Any]]:
    """
    مختصات جغرافیایی یک شهر را جستجو می‌کند.
    ابتدا دیتابیس محلی را بررسی کرده، سپس از سرویس Geocoding خارجی استفاده می‌کند.
    """
    
    # برای مقاوم‌سازی در برابر فواصل، کاراکترهای اضافی و حروف کوچک/بزرگ
    normalized_city_name = city_name.strip()
    
    # 1. جستجوی محلی (سریع و قابل اطمینان)
    if normalized_city_name in LOCAL_CITY_DB:
        logging.info(f"✅ شهر {city_name} از دیتابیس محلی یافت شد.")
        # اضافه کردن خود نام شهر به خروجی برای استفاده بعدی
        result = LOCAL_CITY_DB[normalized_city_name].copy()
        result['city_name'] = normalized_city_name
        return result

    # 2. جستجوی خارجی (در صورت عدم موفقیت در جستجوی محلی)
    logging.warning(f"❌ شهر {city_name} در دیتابیس محلی یافت نشد. تلاش برای استفاده از سرویس خارجی...")
    
    try:
        # 💥 جایگزینی با کد API خارجی شما
        
        # --- [مثال کد سرویس خارجی - لطفا کد فعلی خود را جایگزین کنید] ---
        #
        # response = external_geocoding_api(normalized_city_name, API_KEY)
        # if response and response.status_code == 200:
        #     # کد پردازش پاسخ API و استخراج مختصات
        #     lat = response['results'][0]['lat']
        #     lon = response['results'][0]['lon']
        #     tz = 'Asia/Tehran' # فرض بر این است که برای شهرهای ایران همین منطقه زمانی است
        #
        #     # در صورت موفقیت، می‌توانید آن را به دیتابیس محلی نیز اضافه کنید (اختیاری)
        #     LOCAL_CITY_DB[normalized_city_name] = {"latitude": lat, "longitude": lon, "timezone": tz}
        #     
        #     logging.info(f"✅ شهر {city_name} با موفقیت از API خارجی یافت شد.")
        #     return {"latitude": lat, "longitude": lon, "timezone": tz, "city_name": normalized_city_name}
        #
        # --- [پایان مثال کد سرویس خارجی] ---
        
        # اگر در حالت تست هستید، می‌توانید این بخش را کامنت کنید تا فقط دیتابیس محلی کار کند
        return None 
        
    except Exception as e:
        # ثبت خطای Timeout یا Connection
        logging.error(f"❌ خطای سرویس خارجی Geocoding برای {city_name}: {e}", exc_info=True)
        return None

# ----------------------------------------------------------------------
# نحوه فراخوانی (در ماژول اصلی ربات شما)
# ----------------------------------------------------------------------

# # فرض کنید نام شهر از کاربر دریافت شده است
# city_name_from_user = "اراک" 

# # فراخوانی تابع جدید
# city_data = get_coordinates_from_city(city_name_from_user)

# if city_data:
#     # داده‌ها با موفقیت یافت شده‌اند، اکنون می‌توانید محاسبه چارت را آغاز کنید
#     latitude = city_data['latitude']
#     longitude = city_data['longitude']
#     timezone = city_data['timezone']
#     # ... ادامه محاسبات چارت تولد
# else:
#     # ارسال پیام خطا به کاربر
#     print("❌ شهر مورد نظر پیدا نشد. لطفاً نام شهر را دقیق‌تر وارد کنید.")
