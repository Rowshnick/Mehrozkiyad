# ----------------------------------------------------------------------
# Dockerfile - نسخه مقاوم در برابر خطا با ابزارهای کامپایل
# ----------------------------------------------------------------------

# 1. تصویر پایه پایتون 3.9 (تصویر شما)
FROM python:3.9-slim-bullseye 

# 💥💥💥 گام حیاتی: نصب کامپایلرها و وابستگی‌های سیستمی 💥💥💥
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    # ابزارهای کامپایل برای ساخت پکیج‌هایی مثل pyswisseph
    build-essential \
    cmake \
    # وابستگی‌های مورد نیاز matplotlib/numpy
    pkg-config \
    libfreetype6-dev \
    # وابستگی‌های عمومی لینوکس
    locales \
    fonts-noto-extra \
    # تمیزکاری برای کاهش حجم ایمیج
    && echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen en_US.UTF-8 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

# 2. تنظیم متغیرهای محیطی
ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV APP_HOME /usr/src/app
WORKDIR $APP_HOME

# 3. نصب پکیج‌های پایتون (بعد از نصب کامپایلرها)
COPY requirements.txt .
COPY ephe/ /usr/src/app/ephe
RUN pip install --upgrade pip && \
    # ❗️ نصب تمیز با استفاده از کامپایلر تازه نصب شده
    pip install --no-cache-dir -r requirements.txt


# 4. کپی کردن سورس کد برنامه
COPY . .

# 5. دستور اجرای نهایی
CMD ["python", "-m", "uvicorn", "bot_app:app", "--host", "0.0.0.0", "--port", "8080"]
