# ----------------------------------------------------------------------
# Dockerfile - نسخه مقاوم در برابر خطا با ابزارهای کامپایل
# ----------------------------------------------------------------------
# استفاده از پایتون نسخه سبک
FROM python:3.9-slim-bullseye

# نصب پیش‌نیازهای سیستم‌عامل
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    pkg-config \
    libfreetype6-dev \
    locales \
    fonts-noto-extra \
    && echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen en_US.UTF-8 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# تنظیم پوشه کاری
WORKDIR /usr/src/app

# ۱. کپی کردن فایل نیازمندی‌ها
COPY requirements.txt .

# ۲. نصب کتابخانه‌های پایتون (این خط در فایل شما جا افتاده است)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ۳. کپی کردن پوشه داده‌های نجومی و تنظیم دسترسی
COPY ephe/ /usr/src/app/ephe/
RUN chmod -R 755 /usr/src/app/ephe

# ۴. کپی کردن بقیه فایل‌های پروژه
COPY . .

# تنظیم متغیرهای محیطی برای زبان
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8

# ۵. دستور اجرای برنامه
CMD ["python", "-m", "uvicorn", "bot_app:app", "--host", "0.0.0.0", "--port", "8080"]
