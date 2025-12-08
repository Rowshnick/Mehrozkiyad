# ----------------------------------------------------------------------
# Dockerfile - تغییر نسخه پایتون برای حل مشکل ناسازگاری
# ----------------------------------------------------------------------

# 1. تغییر تصویر پایه به پایتون 3.9 (پایدارتر برای Skyfield)
FROM python:3.9-slim-bullseye

# 2. نصب فقط بسته های سیستمی ضروری
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
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 5. کپی کردن سورس کد برنامه
COPY . .

# 6. دستور اجرای نهایی
CMD ["python", "-m", "uvicorn", "bot_app:app", "--host", "0.0.0.0", "--port", "8080"]
