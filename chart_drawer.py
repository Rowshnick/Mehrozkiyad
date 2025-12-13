import httpx
import os
from typing import Dict, Any

# فرض کنید متغیرهای API_KEY و API_ENDPOINT در .env یا به صورت ثابت تعریف شده‌اند
API_KEY = "YOUR_API_KEY_HERE"  # کلید API شما
API_ENDPOINT = "https://api.astrology.com/v1/chart/generate"  # مثال فرضی

async def generate_chart_image(chart_data: Dict[str, Any]) -> Union[bytes, str]:
    """
    درخواست به API برای تولید تصویر چارت و بازگرداندن داده‌های باینری تصویر.
    """
    try:
        # ساختن payload (بار داده‌ای) بر اساس نیازهای API
        # این ساختار بر اساس API که انتخاب می‌کنید تغییر خواهد کرد.
        payload = {
            "datetime_utc": chart_data['datetime_utc'],
            "latitude": chart_data['latitude'],
            "longitude": chart_data['longitude'],
            "house_system": "Placidus",
            "image_format": "png" # یا "svg"
        }
        
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 1. ارسال درخواست POST
            response = await client.post(
                API_ENDPOINT,
                json=payload,
                headers=headers
            )
            
            # 2. بررسی پاسخ
            response.raise_for_status()  # خطاها را کنترل می‌کند
            
            # 3. فرض می‌کنیم API تصویر را به صورت باینری (فایل) برمی‌گرداند
            if 'image/' in response.headers.get('content-type', ''):
                return response.content  # محتوای باینری تصویر
            else:
                # اگر API لینک یا JSON برگرداند
                # باید محتوای JSON را تجزیه کنید و لینک تصویر را دانلود کنید.
                return "API response is not direct image data, needs further processing." 
                
    except httpx.HTTPStatusError as e:
        return f"❌ خطای API (HTTP): {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"❌ خطای اتصال یا پردازش: {str(e)}"

# نکته: اگر API شما از نوعی باشد که لینک تصویر را برمی‌گرداند، 
# شما نیاز به یک گام اضافی برای دانلود آن لینک خواهید داشت.
