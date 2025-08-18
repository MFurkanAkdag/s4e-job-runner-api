# ---- Base image ----
FROM python:3.13-slim

# ---- Ortam değişkenleri ----
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# ---- Sistem paketleri ----
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# ---- Katana binary ----
RUN apt-get update && apt-get install -y unzip \
    && curl -L https://github.com/projectdiscovery/katana/releases/download/v1.1.4/katana_1.1.4_linux_amd64.zip -o katana.zip \
    && unzip katana.zip -d /usr/local/bin/ \
    && rm katana.zip



# ---- Proje dosyaları ----
WORKDIR /app
COPY .. .

# ---- Python bağımlılıkları ----
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ---- Varsayılan komut ----
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

