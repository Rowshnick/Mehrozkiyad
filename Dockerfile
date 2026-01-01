# -----------------------------
# 1) Base image
# -----------------------------
FROM python:3.11-slim

# -----------------------------
# 2) Install system dependencies
# -----------------------------
RUN apt-get update && apt-get install -y \
    build-essential \
    libfreetype6-dev \
    libpng-dev \
    libopenblas-dev \
    liblapack-dev \
    libatlas-base-dev \
    fonts-dejavu \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------
# 3) Create app directory
# -----------------------------
WORKDIR /app

# -----------------------------
# 4) Copy requirements
# -----------------------------
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# -----------------------------
# 5) Copy project files
# -----------------------------
COPY . .

# -----------------------------
# 6) Install Vazirmatn font manually
# -----------------------------
RUN mkdir -p /usr/share/fonts/truetype/vazirmatn && \
    cp /app/fonts/Vazirmatn-Regular.ttf /usr/share/fonts/truetype/vazirmatn/ && \
    fc-cache -f -v

# -----------------------------
# 7) Expose port for Render
# -----------------------------
EXPOSE 10000

# -----------------------------
# 8) Start FastAPI app
# -----------------------------
CMD ["uvicorn", "bot_app:app", "--host", "0.0.0.0", "--port", "10000"]
