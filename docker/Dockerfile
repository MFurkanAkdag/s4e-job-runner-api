# ---- Base image ----
FROM python:3.12-slim

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
RUN curl -L https://github.com/projectdiscovery/katana/releases/download/v1.2.1/katana_1.2.1_linux_amd64.zip -o katana.zip \
    && unzip katana.zip -d katana-bin \
    && mv katana-bin/katana /usr/local/bin/katana \
    && rm -rf katana.zip katana-bin

# ---- Proje dosyaları ----
WORKDIR /app
COPY . .

# ---- Python bağımlılıkları ----
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ---- Varsayılan komut ----
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
