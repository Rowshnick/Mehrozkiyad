# ----------------------------------------------------------------------
# Dockerfile - نسخه نهایی و عملی (اصلاح شده)
# ----------------------------------------------------------------------

# 1. تصویر پایه پایتون (سبک)
FROM python:3.11-slim-bullseye

# 💥 [CACHE BUSTER - کلید حل مشکل کش Railway]
# این متغیر برای شکستن کش لایه‌های Docker اضافه شده است.
# **حتماً** برای هر بار تلاش دپلوی مجدد، مقدار (مثلاً _V2) را تغییر دهید.
ENV CACHE_BREAKER 20251208_V2 

# 2. نصب فقط بسته های سیستمی ضروری (مانند Locale)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    locales \
    && echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen en_US.UTF-8 && \
    rm -rf /var/lib/apt/lists/*

# 3. تنظیم متغیرهای محیطی
ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV APP_HOME /usr/src/app
WORKDIR $APP_HOME

# 4. کپی و نصب وابستگی‌ها
# تغییر در ENV CACHE_BREAKER در بالا، این لایه را مجبور به اجرای مجدد می‌کند.
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 5. کپی کردن سورس کد برنامه
COPY . .

# 💡 دستور اجرای نهایی
# پورت 8080 پورت پیش‌فرض Railway است.
CMD ["python", "-m", "uvicorn", "bot_app:app", "--host", "0.0.0.0", "--port", "8080"]
