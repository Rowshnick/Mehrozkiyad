FROM python:3.11-slim

# -----------------------------
# Install system dependencies
# -----------------------------
RUN apt-get update && apt-get install -y \
    build-essential \
    libfreetype6-dev \
    libpng-dev \
    libopenblas-dev \
    liblapack-dev \
    fonts-dejavu \
    fontconfig \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------
# Create app directory
# -----------------------------
WORKDIR /app

# -----------------------------
# Install Python dependencies
# -----------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install aiogram==3.4.1

# -----------------------------
# Copy project files
# -----------------------------
COPY . .

# -----------------------------
# Install Vazirmatn font
# -----------------------------
RUN mkdir -p /usr/share/fonts/truetype/vazirmatn && \
    cp /app/fonts/Vazirmatn-Regular.ttf /usr/share/fonts/truetype/vazirmatn/ && \
    fc-cache -f -v

# -----------------------------
# Expose port for Render
# -----------------------------
EXPOSE 10000

# -----------------------------
# Start FastAPI app
# -----------------------------
CMD ["uvicorn", "bot_app:app", "--host", "0.0.0.0", "--port", "10000"]
