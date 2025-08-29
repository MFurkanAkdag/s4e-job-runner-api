1. Giriş
Bu proje, Python tabanlı bir backend ve React tabanlı bir frontend bileşeninden oluşan, JSON tabanlı RESTful API’ler ile etkileşim kuran bir “Job Runner” sistemi sunar. Amaç, işletim sistemi komutlarını ve Katana aracıyla web taramalarını asenkron şekilde çalıştırmak, sonuçları veritabanında saklamak ve web arayüzü üzerinden izlenebilir kılmaktır.

2. Mimari Genel Bakış
Sistem üç ana bileşenden oluşur:
API: FastAPI tabanlı servis.
Worker: Celery ile kuyruğa alınan işleri yürütür.
Frontend: React ve Material UI ile hazırlanmış SPA.
RabbitMQ kuyruğu, PostgreSQL veritabanı, Flower izleme servisi ve bu bileşenleri birbirine bağlayan Docker Compose dosyası bir arada çalışır.

3. Kullanılan Teknolojiler
Backend: FastAPI, SQLAlchemy, Alembic, Celery ve Pydantic
Frontend: React, Vite, Material UI, React Query, axios ve React Router Dom
Alt Yapı: Docker, RabbitMQ, PostgreSQL, Flower.

4. Veri Modeli ve Veritabanı
Veri modeli iki ana tablodan oluşur:
job_runs: Her işin durumunu, metriklerini ve idempotency anahtarını saklar
results: İşlere ait çıktı verilerini JSONB formatında tutar
JobRun sınıfı, job_type ve status alanları için enum kullanır; zaman damgaları ve hata özetleri gibi meta verileri içerir. Idempotency desteği için idempotency_key alanı sağlanmıştır.

5. API Tasarımı
API, FastAPI ile oluşturulmuş olup başlıca rotalar:
/jobs/os ve /jobs/katana: İş tetikleme uç noktaları
/job-runs: İş listesi ve detay erişimi; server-side pagination ve filtreleme destekler
/results/{run_id}: Sonuçları döndürür; limit parametresiyle kısıtlama yapılabilir
/health ve /ready: Sağlık kontrolleri

6. Job Kavramı ve İş Akışı
Her “Job”, job_runs tablosunda QUEUED, STARTED, SUCCEEDED, FAILED gibi durumlarla izlenir. API bir iş tetiklediğinde kayıt oluşturur ve Celery aracılığıyla ilgili kuyruğa gönderir. Worker iş başladıktan sonra durum değişikliklerini ve metrikleri günceller; sonuçları results tablosuna yazar.

7. Implement Edilen Job Türleri
OS Komut Job’u: Önceden izin verilen komutları çalıştırır, çıkışları kırpılmış biçimde kaydeder ve çalıştırma süresini metrike ekler. Çalışma dizini kontrolü ve izinli komut listesi ile güvenlik sağlanır
Katana Crawler Job’u: Katana aracını kullanarak bir URL üzerindeki sayfaları tarar, SSRF ve domain filtreleri uygular, örnek URL listesini sonuç olarak kaydeder

8. Asenkron Görev Sistemi
Celery uygulaması, iş türlerine göre ayrı kuyruklar kullanır; varsayılan soft ve hard timeout değerleri, task routing ve prefetch ayarları yapılandırılmıştır. Worker konteyneri, os ve katana kuyruklarını dinler ve ilgili servis fonksiyonlarını çağırır.

9. Frontend Uygulaması
React tabanlı SPA, React Query ile API çağrılarını önbelleğe alır ve MUI bileşenleriyle arayüzü sunar. Temel sayfalar:
JobsPage: OS ve Katana job formları, tüm işlerin listesi.
ResultsPage: Seçilen run’ın sonuçları ve bulunan URL’ler.
Routing ve QueryClient sağlayıcısı main.jsx içerisinde yapılandırılmıştır. Job listesindeki DataGrid bileşeni, sunucu tarafı pagination ve filtreleme yapar; satır tıklandığında sonuç sayfasına yönlendirir.

10. Güvenlik ve Validasyon
API Key: Her istek X-API-Key başlığı ile doğrulanır; yanlış veya eksik anahtar durumunda 401/403 döner
Idempotency: Tekrarlanan iş tetiklemelerini önlemek için Idempotency-Key başlığı desteklenir.
Komut Güvenliği: OS job’ları izinli komut listesi ve çalışma dizini doğrulamasıyla sınırlandırılır
SSRF Önlemleri: Katana job’u, private veya localhost adreslerini engeller; opsiyonel host allow-listi uygulanır

11. Günlükleme ve İzleme
Proje, merkezi logger kullanarak stdout’a yapılandırılmış günlükler üretir; log seviyesi konfigürasyondan gelir. Ayrıca Celery worker logları ve Flower dashboard, işlerin takibini kolaylaştırır.

12. Docker ve Dağıtım
Backend Dockerfile, Python 3.12 tabanlı olup Katana binary’sini indirir ve FastAPI’yi uvicorn ile başlatır. Frontend Dockerfile ise Node 20 ile yapıyı oluşturur ve Nginx üzerinden servis eder. Docker Compose dosyası tüm servisleri orkestre eder, gerekli portları açar ve ortak volume’ları paylaşır.

13. Kurulum ve Çalıştırma Talimatları
Ortam değişkenlerini .env dosyasıyla tanımlayın.
docker-compose build
docker-compose up komutu tüm servisleri ayağa kaldırır.
Backend http://localhost:8000, frontend http://localhost:5173 üzerinden erişilebilir.
Worker konteyneri otomatik olarak Celery kuyruklarını tüketmeye başlar.

14. Test ve Doğrulama Yaklaşımları
Projede pytest ve httpx bağımlılıkları mevcuttur, bu da API entegrasyon ve birim testlerine olanak tanır. Frontend tarafında React Testing Library yer almamakla birlikte, axios tabanlı API çağrıları kolayca mock edilebilir.

15. Sonuç
Proje, asenkron iş çalıştırma ve sonuç izleme konusunda modüler, genişletilebilir bir çözüm sunar. Docker tabanlı altyapı ile hızlı kurulum ve izolasyon sağlanmış, React frontend ile kullanıcı dostu bir arayüz elde edilmiştir. Ek job türleri, yetkilendirme ve izleme gibi alanlarda yapılacak geliştirmeler, sistemi daha da olgunlaştıracaktır.

