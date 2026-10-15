# 🚀 راهنمای Deploy — همراه آرامش

راهنمای کامل برای انتقال پروژه از localhost به سرور production.

---

## 📋 پیش‌نیازها

### سرور
- **VPS** (اوبونتو ۲۲.۰۴ یا ۲۰.۰۴)
  - پیشنهاد: پارس‌پک، افرانت، لیارا
  - حداقل: ۲ CPU + ۲GB RAM + ۲۰GB دیسک
- **دامنه** (`.ir` یا `.com`)
- **دسترسی SSH** به سرور

### محلی
- **Docker Desktop** (نصب شده)
- **Git**
- **SSH Client**

### خارجی
- **کلید AvalAI** (برای LLM + Speech)
- **یا کلید Gemini** (رایگان)
- **حساب SMTP** (Zoho, Mailgun, ...)

---

## 🎯 مراحل کلی

```
۱. آماده‌سازی سرور (SSH + Firewall)
۲. نصب Docker + Docker Compose
۳. Clone پروژه
۴. تنظیمات .env
۵. Docker Compose (app + db + nginx)
۶. PostgreSQL (خودکار با Docker)
۷. Nginx (Reverse Proxy)
۸. SSL (Let's Encrypt)
۹. Domain + DNS
۱۰. تست
```

---

## 📝 مرحله ۱: آماده‌سازی سرور

### ۱.۱. اتصال SSH
```bash
ssh root@SERVER_IP
```

### ۱.۲. آپدیت سیستم
```bash
apt update && apt upgrade -y
```

### ۱.۳. ساخت کاربر (اختیاری)
```bash
adduser aramesh
usermod -aG sudo aramesh
```

### ۱.۴. تنظیم Firewall
```bash
ufw allow 22
ufw allow 80
ufw allow 443
ufw enable
```

---

## 🐳 مرحله ۲: نصب Docker

```bash
# نصب Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# نصب Docker Compose Plugin
apt install docker-compose-plugin -y

# چک
docker --version
docker compose version
```

**اختیاری:** Docker بدون sudo
```bash
usermod -aG docker $USER
newgrp docker
```

---

## 📦 مرحله ۳: Clone پروژه

```bash
# Clone
cd /home/aramesh
git clone https://github.com/sadaf92901/aramesh.git
cd aramesh
```

---

## ⚙️ مرحله ۴: تنظیمات `.env`

```bash
cp .env.example .env
nano .env
```

**محتوای `.env` برای production:**

```bash
# ============================================================
# Flask
# ============================================================
SECRET_KEY=<رشته ۶۴ کاراکتری>
FLASK_ENV=production

# ============================================================
# Database (PostgreSQL in Docker)
# ============================================================
DATABASE_URL=postgresql://aramesh:aramesh123@db:5432/aramesh
DB_PASSWORD=aramesh123

# ============================================================
# LLM (AvalAI)
# ============================================================
LLM_ENABLED=true
LLM_PROVIDER=openai

OPENAI_API_KEY=aa-...
OPENAI_BASE_URL=https://api.avalai.ir/v1
OPENAI_MODEL=gpt-4o-mini
OPENAI_TRANSCRIBE_MODEL=whisper-1

# ============================================================
# Speech (AvalAI)
# ============================================================
SPEECH_ENABLED=true
SPEECH_PROVIDER=avalai

# ============================================================
# Gemini (اختیاری)
# ============================================================
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash

# ============================================================
# RAG
# ============================================================
RAG_ENABLED=true
RAG_TOP_K=3

# ============================================================
# Email
# ============================================================
EMAIL_ENABLED=true
EMAIL_PROVIDER=smtp
SMTP_HOST=smtp.zoho.com
SMTP_PORT=587
SMTP_USER=noreply@aramesh.app
SMTP_PASSWORD=your-app-password
SMTP_FROM=noreply@aramesh.app

# ============================================================
# Deployment
# ============================================================
PORT=8000
WORKERS=4
```

**ساخت SECRET_KEY:**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

---

## 🐳 مرحله ۵: Docker Compose

### ۵.۱. `Dockerfile`

توی ریشه‌ی پروژه بساز:

```dockerfile
# ============================================================
# Dockerfile — همراه آرامش
# ============================================================

FROM python:3.11-slim

# ===== متغیرها =====
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# ===== پکیج‌های سیستمی =====
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ===== پوشه‌ی کاری =====
WORKDIR /app

# ===== نصب پکیج‌های پایتون =====
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install gunicorn

# ===== کپی پروژه =====
COPY . .

# ===== پوشه‌ها =====
RUN mkdir -p logs uploads static/uploads/avatars instance data

# ===== کاربر غیر-root =====
RUN useradd -m -u 1000 aramesh && \
    chown -R aramesh:aramesh /app
USER aramesh

# ===== EXPOSE =====
EXPOSE 8000

# ===== Health check =====
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/healthz/ready || exit 1

# ===== اجرا =====
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--threads", "2", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "wsgi:app"]
```

### ۵.۲. `docker-compose.yml`

توی ریشه‌ی پروژه بساز:

```yaml
# ============================================================
# docker-compose.yml — همراه آرامش
# ============================================================

version: '3.8'

services:
  # ============================================================
  # اپ Flask
  # ============================================================
  app:
    build: .
    container_name: aramesh_app
    restart: unless-stopped
    env_file: .env
    environment:
      - DATABASE_URL=postgresql://aramesh:${DB_PASSWORD}@db:5432/aramesh
    ports:
      - "8000:8000"
    volumes:
      - ./logs:/app/logs
      - ./uploads:/app/uploads
      - ./data:/app/data
    depends_on:
      db:
        condition: service_healthy
    networks:
      - aramesh_net

  # ============================================================
  # PostgreSQL
  # ============================================================
  db:
    image: postgres:15-alpine
    container_name: aramesh_db
    restart: unless-stopped
    environment:
      POSTGRES_USER: aramesh
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: aramesh
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U aramesh"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - aramesh_net

  # ============================================================
  # Nginx (Reverse Proxy)
  # ============================================================
  nginx:
    image: nginx:alpine
    container_name: aramesh_nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./static:/app/static:ro
      - ./certbot/conf:/etc/letsencrypt:ro
      - ./certbot/www:/var/www/certbot:ro
    depends_on:
      - app
    networks:
      - aramesh_net

volumes:
  postgres_data:

networks:
  aramesh_net:
    driver: bridge
```

### ۵.۳. `nginx.conf`

توی ریشه‌ی پروژه بساز:

```nginx
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # ===== Logging =====
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;

    # ===== Gzip =====
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript
               application/x-javascript application/xml
               application/javascript application/json;

    # ===== Upstream =====
    upstream aramesh {
        server app:8000;
    }

    # ===== HTTP → HTTPS =====
    server {
        listen 80;
        server_name aramesh.app www.aramesh.app;

        # ===== Let's Encrypt =====
        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }

        # ===== Redirect به HTTPS =====
        location / {
            return 301 https://$host$request_uri;
        }
    }

    # ===== HTTPS =====
    server {
        listen 443 ssl http2;
        server_name aramesh.app www.aramesh.app;

        # ===== SSL =====
        ssl_certificate /etc/letsencrypt/live/aramesh.app/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/aramesh.app/privkey.pem;

        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;

        # ===== Security Headers =====
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;

        # ===== Client Max Body =====
        client_max_body_size 20M;

        # ===== Static Files =====
        location /static/ {
            alias /app/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # ===== API =====
        location / {
            proxy_pass http://aramesh;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_read_timeout 120s;
        }
    }
}
```

---

## 🗄 مرحله ۶: PostgreSQL in Docker

### ۶.۱. اجرا
```bash
docker compose up -d db
```

### ۶.۲. تست
```bash
docker compose exec db psql -U aramesh -d aramesh -c "SELECT version();"
```

### ۶.۳. Migration
```bash
docker compose exec app flask db upgrade
```

### ۶.۴. چک جدول‌ها
```bash
docker compose exec db psql -U aramesh -d aramesh -c "\dt"
```

**باید ۹ جدول ببینی.**

---

## 🔐 مرحله ۷: SSL (Let's Encrypt)

### ۷.۱. Certbot
```bash
apt install certbot -y
mkdir -p certbot/conf certbot/www
```

### ۷.۲. دریافت گواهی
```bash
docker compose stop nginx

certbot certonly --standalone \
    -d aramesh.app -d www.aramesh.app \
    --email your-email@example.com \
    --agree-tos \
    --non-interactive
```

### ۷.۳. کپی گواهی
```bash
cp -r /etc/letsencrypt/* ./certbot/conf/
```

### ۷.۴. اجرای مجدد
```bash
docker compose up -d nginx
```

### ۷.۵. تمدید خودکار
```bash
crontab -e

# اضافه کن (هر ۱۲ ساعت):
0 */12 * * * certbot renew --quiet && docker compose restart nginx
```

---

## 🌐 مرحله ۸: Domain + DNS

### ۸.۱. توی پنل دامنه:
```
A Record:    @  → SERVER_IP
A Record:    www → SERVER_IP
```

### ۸.۲. تست DNS
```bash
nslookup aramesh.app
```

---

## 🚀 مرحله ۹: اجرا

```bash
# اجرای همه
docker compose up -d

# چک لاگ‌ها
docker compose logs -f

# چک وضعیت
docker compose ps
```

### تست:
```
https://aramesh.app
```

**باید اپ لود بشه.** ✅

---

## 🧪 مرحله ۱۰: تست نهایی

### ۱۰.۱. Healthcheck
```bash
curl https://aramesh.app/healthz
# باید {"status": "ok"}
```

### ۱۰.۲. صفحات
- [ ] `https://aramesh.app/` → لاگین
- [ ] `https://aramesh.app/garden` → باغ
- [ ] `https://aramesh.app/subscription` → اشتراک
- [ ] `https://aramesh.app/journal` → روزنگار
- [ ] `https://aramesh.app/profile` → پروفایل

### ۱۰.۳. Lighthouse
F12 → Lighthouse → Analyze

**انتظار:**
- Performance: ۹۰+
- Accessibility: ۱۰۰
- Best Practices: ۱۰۰
- SEO: ۹۰+

### ۱۰.۴. تست ثبت‌نام
- یه کاربر جدید بساز
- لاگین کن
- یه تشخیص بده

---

## 🔄 به‌روزرسانی

```bash
# ۱. Pull
cd /home/aramesh/aramesh
git pull origin main

# ۲. Rebuild
docker compose build

# ۳. Restart
docker compose up -d

# ۴. Migration (اگه لازمه)
docker compose exec app flask db upgrade
```

---

## 📊 مانیتورینگ

### لاگ‌ها
```bash
docker compose logs -f app
docker compose logs -f nginx
docker compose logs -f db
```

### منابع
```bash
docker stats
```

### دیسک
```bash
df -h
```

---

## 🚨 Troubleshooting

### مشکل: ۵۰۲ Bad Gateway
```bash
docker compose ps
docker compose logs app
```

### مشکل: Database connection failed
```bash
docker compose exec db psql -U aramesh -d aramesh -c "\dt"
```

### مشکل: SSL کار نمی‌کنه
```bash
ls -la certbot/conf/live/aramesh.app/
docker compose logs nginx
```

### مشکل: کندی
```bash
# تعداد workerها رو زیاد کن
# توی docker-compose.yml: --workers 8
```

---

## 💾 بکاپ

### بکاپ دستی
```bash
# Database
docker compose exec db pg_dump -U aramesh aramesh > backup_$(date +%Y%m%d).sql

# Data
tar -czf data_backup_$(date +%Y%m%d).tar.gz data/

# Uploads
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz uploads/
```

### بکاپ خودکار (Cron)
```bash
crontab -e

# هر روز ساعت ۳ صبح
0 3 * * * cd /home/aramesh/aramesh && docker compose exec -T db pg_dump -U aramesh aramesh > /home/aramesh/backups/db_$(date +\%Y\%m\%d).sql
```

---

## 🔧 تغییر Provider

### تغییر LLM از OpenAI به Gemini
```bash
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIza...
GEMINI_MODEL=gemini-2.5-flash
```

### تغییر LLM از Gemini به Local
```bash
LLM_PROVIDER=local
LOCAL_LLM_MODEL=Qwen/Qwen2.5-1.5B-Instruct
LOCAL_LLM_DEVICE=cpu
```

### تغییر Speech
```bash
SPEECH_PROVIDER=gemini  # یا avalai یا local
```

---

## 📞 پشتیبانی

- 📧 ایمیل: [support@aramesh.app](mailto:support@aramesh.app)
- 🐛 باگ: [bugs@aramesh.app](mailto:bugs@aramesh.app)

---

<div align="center">

**🚀 Deploy موفق باشه! 🚀**

</div>
