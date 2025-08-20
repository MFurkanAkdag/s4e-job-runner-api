# Node.js resmi imajını kullan
FROM node:20-alpine AS build

# Çalışma dizini
WORKDIR /app

# Bağımlılıkları yükle
COPY package*.json ./
RUN npm install

# Uygulama dosyalarını kopyala
COPY . .

# Build et (production için)
RUN npm run build

# ---------------------------
# Servis aşaması
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html

# Varsayılan Nginx portu
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
