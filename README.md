# 🌿 همراه آرامش

> **اپلیکیشن سلامت روان با تحلیل هوشمند متن و صوت فارسی**

[![Tests](https://github.com/sadaf92901/aramesh/actions/workflows/test.yml/badge.svg)](https://github.com/sadaf92901/aramesh/actions/workflows/test.yml)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![Tests Count](https://img.shields.io/badge/Tests-327%20Passed-success?style=for-the-badge)](tests/)
[![Coverage](https://img.shields.io/badge/Coverage-80%25-green?style=for-the-badge)](tests/)
[![Lighthouse](https://img.shields.io/badge/Lighthouse-100%20A11y-brightgreen?style=for-the-badge)](https://developers.google.com/web/tools/lighthouse)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.2.0-blue?style=for-the-badge)](CHANGELOG.md)

---

## 📸 تصاویر

<div align="center">

### 🔑 ورود به اپ

![ورود](docs/screenshots/01-login.png)

### 🏠 داشبورد

![داشبورد](docs/screenshots/02-dashboard.png)

### 🌸 باغ آرامش

![باغ آرامش](docs/screenshots/05-garden.png)

### 🧠 تشخیص هوشمند

![پرسشنامه](docs/screenshots/03-questionnaire.png)

### 📊 نتیجه‌ی تحلیل

![نتیجه](docs/screenshots/04-result.png)

### 💬 چت‌بات همدل

![چت](docs/screenshots/06-chat.png)

### ⭐ اشتراک

![اشتراک](docs/screenshots/07-subscription.png)

### 👤 پروفایل کاربر

![پروفایل](docs/screenshots/08-profile.png)

</div>

---

## 📖 درباره‌ی پروژه

**همراه آرامش** یه اپلیکیشن وب پیشرو (PWA) برای **سلامت روان** و **خودمراقبتی**ـه که به کاربر کمک می‌کنه:

- 🧠 وضعیت روانی خودش رو **بسنجه**
- 📊 روزانه حالاتش رو **ثبت کنه**
- 🎤 به جای تایپ، **صدا ضبط کنه** و به متن تبدیل بشه
- 🌬️ با تمرین‌های **آرامش‌بخش** استرسش رو کم کنه
- 💬 با یه **چت‌بات همدل** حرف بزنه
- 📜 روند بهبودش رو **پیگیری کنه**
- 📋 یه **برنامه‌ی درمانی شخصی‌سازی شده** بگیره
- 🌸 توی **باغ آرامش** گل بکاره
- ⭐ از **اشتراک** خودش مطلع بشه
- 🎨 تم اپ رو به **سلیقه‌ی خودش** تغییر بده

> ⚠️ **هشدار پزشکی:** این اپلیکیشن یه ابزار غربالگری اولیه‌ست و جایگزین تشخیص روانپزشک یا روانشناس نیست. برای تشخیص دقیق، حتماً با یه متخصص مشورت کنید.

---

## ✨ ویژگی‌ها

### 🧠 تشخیص هوشمند
- پرسشنامه‌ی ۲۰ سوالی بر اساس **DSM-5** و **GAD-7**
- ۳ سوال باز برای تحلیل عمیق‌تر
- پشتیبانی از **پاسخ متنی** و **صوتی**
- تحلیل با **GPT-4o-mini** / **Gemini** + **RAG**
- وزن‌دهی علمی به سوالات
- سطح‌بندی: سالم / خفیف / متوسط / شدید

### 📊 وضعیت روزانه
- ثبت خلق، انرژی، خواب
- محاسبه‌ی **استریک**
- سیستم **سطح**

### 🌬️ تمرین تنفس
- تمرین ۴-۴-۴
- راهنمای زنده
- آمار روزانه و هفتگی

### 🧘 مدیتیشن هدایت‌شده
- ۳ سناریو: صبحگاهی، تنفس عمیق، شبانه
- متن‌های آرام‌بخش
- تایمر + نوار پیشرفت

### 📝 روزنگار (با ضبط صدا) 🆕
- نوشتن یاداشت روزانه
- ۷ حال مختلف
- برچسب‌گذاری
- فیلتر و **جستجو**
- **🎤 ضبط صدا → تبدیل به متن** (Whisper/Gemini)
- **ویرایش متن** بعد از تبدیل
- **صدا بعد از تبدیل پاک می‌شه** (حریم خصوصی)

### 💬 چت‌بات همدل
- پاسخ‌های هوشمند با **GPT-4o-mini** / **Gemini**
- تشخیص احساسات از پیام
- Fallback برای حالت آفلاین
- **پروتکل بحران** (شماره‌های اورژانس)

### 📋 برنامه‌ی درمانی هفتگی
- برنامه‌ی ۷ روزه
- شخصی‌سازی بر اساس سطح
- پیگیری پیشرفت

### 📜 تاریخچه‌ی کامل
- خط زمانی همه‌ی فعالیت‌ها
- فیلتر بر اساس نوع
- **نمودار پیشرفت**
- گزارش هفتگی LLM

### 🌸 باغ آرامش (Gamification)
- **۵ نوع گل** برای فعالیت‌های مختلف
- **کیف دانه** — هر فعالیت = یه دانه (روزانه)
- **کاشتن دستی** — کاربر خودش می‌کاره
- **ادغام هوشمند**: ۱۰ گل = بوته، ۱۰۰ گل = باغچه
- **۹ سطح باغ** (از تازه‌کار تا خدای باغ)
- **۱۱ دستاورد** (گل، استریک، ...)
- **انیمیشن** + صدا + ذرات نور + کانفتی
- **Toggle صدا** (روشن/خاموش)
- **Cache** در localStorage (سرعت بالا)
- **موقعیت ثابت** گل‌ها (ذخیره در DB)

### ⭐ صفحه‌ی اشتراک
- **پلن فعلی** (رایگان)
- **وضعیت استفاده‌ی روزانه** (تشخیص، چت، یاداشت)
- **ویژگی‌های فعال** (RAG، گزارش، PDF، ...)
- **کارت پریمیوم** (به‌زودی) با دکمه‌ی اطلاع‌رسانی
- **FAQ** (۵ سؤال متداول)
- **کاملاً تم‌پذیر**

### 👤 پروفایل کاربر
- مدیریت اطلاعات
- آواتار (ذخیره در سرور)
- آمار شخصی
- **تغییر رمز با bcrypt**
- **Toggle صدا**
- **دانلود داده‌ها** (JSON)
- **حذف حساب**

### ⚙️ پنل مدیریت (Admin Panel) 🆕
- داشبورد آمار (کاربران، تشخیص‌ها، گل‌ها و...)
- مدیریت کاربران (جستجو، صفحه‌بندی، حذف کاربر)
- تغییر سطح دسترسی (ارتقا به ادمین)
- مشاهده تشخیص‌ها و یادداشت‌ها کاربران
- نمودار فعالیت هفتگی (با Chart.js)
- دسترسی امن (فقط برای کاربرانی که is_admin=True دارند)
- کاملاً جدا از اپ موبایل (در templates/admin/، نه در static/)

### 🎨 تم پیشرفته
- **۶ تم رنگی**: بنفش، آبی، سبز، صورتی، نارنجی، خاکستری
- **۲ حالت نمایش**: روشن، تیره
- ذخیره‌ی خودکار انتخاب کاربر
- **CSS Variables** برای همه‌ی رنگ‌ها

### 🔐 امنیت
- **bcrypt** برای هش رمز
- اعتبارسنجی سه‌لایه
- بازیابی رمز عبور (SMTP + Mock)
- **Rate Limiting** (Flask-Limiter)
- **تأخیر تدریجی** روی ورود ناموفق
- **Security Headers** (X-Frame-Options, ...)
- **XSS Protection** (sanitize + whitelist)
- **CSRF Protection**
- **Foreign Key** در SQLite + PostgreSQL
- `SECRET_KEY` توی `.env`
- **پاک کردن فایل صوتی** بعد از transcribe

### 📝 Logging
- سطوح مختلف (DEBUG, INFO, WARNING, ERROR)
- ذخیره توی فایل
- گردش خودکار (10MB × 5)
- جدا کردن خطاها

### ♿ Accessibility
- **Lighthouse: ۱۰۰** 🏆
- `aria-label` روی همه‌ی عناصر
- `role` مناسب
- `aria-modal` روی مودال‌ها
- **Keyboard navigation**
- **Screen reader friendly**

### 🔍 SEO
- **Lighthouse: ۹۰** ✅
- Meta tags کامل
- **Open Graph** (Facebook, Telegram, ...)
- **Twitter Card**
- عنوان معنادار
- `lang="fa"` و `dir="rtl"`

### 🏥 Healthcheck
- `/healthz` — بررسی سلامت سرور
- `/healthz/ready` — آماده‌بودن (Load Balancer)
- `/healthz/live` — زنده‌بودن (Kubernetes)
- چک دیتابیس + دیسک + uptime

### 🔄 CI/CD
- **GitHub Actions** خودکار
- اجرای تست‌ها روی هر push
- Badge سبز توی README

### 🎨 UI/UX
- **RTL** کامل
- **تم دارک**
- **ریسپانسیو**
- **Onboarding** برای کاربر جدید
- **Loading States**
- **Empty States**
- **Error Handling**
- **Design System** (CSS Variables)
- **Cache** در localStorage

---

## 🛠 تکنولوژی

### Backend
| تکنولوژی | کاربرد |
|----------|--------|
| **Flask 2.3** | وب فریمورک |
| **SQLAlchemy 2.0** | ORM |
| **Flask-Migrate** | Migration |
| **PostgreSQL 18** | دیتابیس production |
| **SQLite** | دیتابیس development |
| **bcrypt** | هش رمز |
| **Flask-Limiter** | Rate Limiting |
| **jdatetime** | تاریخ شمسی |
| **psycopg2** | درایور PostgreSQL |

### AI & ML
| تکنولوژی | کاربرد |
|----------|--------|
| **AvalAI** | واسط LLM و Speech |
| **OpenAI GPT-4o-mini** | تحلیل متن و چت |
| **Google Gemini 2.5** | جایگزین LLM |
| **Whisper-1** | صوت → متن |
| **sentence-transformers** | embedding برای RAG |

### Frontend
| تکنولوژی | کاربرد |
|----------|--------|
| **HTML5** | ساختار |
| **CSS3** | استایل (Design System) |
| **JavaScript (ES6+)** | منطق |
| **IndexedDB** | ذخیره‌ی آفلاین |
| **MediaRecorder API** | ضبط صدا |
| **Web Audio API** | صداهای باغ |
| **localStorage** | تنظیمات + cache |

### DevOps
| تکنولوژی | کاربرد |
|----------|--------|
| **Git** | نسخه‌بندی |
| **GitHub** | مخزن + CI/CD |
| **GitHub Actions** | تست خودکار |
| **GitHub Codespaces** | محیط توسعه‌ی آنلاین |
| **Docker** | (در حال راه‌اندازی) |

---

## 🏗 معماری

### Provider-based (قابل تعویض)

```
routes/*.py  →  utils/*/service.py  →  providers/*.py
              (ثابت)                  (قابل تعویض)
```

**مثال:** LLM

```python
# routes/diagnosis.py (ثابت)
llm = get_llm_service()
result = llm.analyze_text(texts)

# utils/llm/service.py (interface ثابت)
class LLMService:
    def analyze_text(self, texts):
        return self.provider.analyze_text(texts)

# utils/llm/providers/openai.py
class OpenAIProvider(LLMProvider):
    def analyze_text(self, texts):
        # فراخوانی OpenAI
        ...

# utils/llm/providers/gemini.py
class GeminiProvider(LLMProvider):
    def analyze_text(self, texts):
        # فراخوانی Gemini
        ...
```

**مزیت:** می‌تونی `OpenAI` رو با `Gemini` یا `Local` عوض کنی **بدون تغییر route**.

**پشتیبانی:**
- **LLM:** OpenAI, Gemini, Local
- **Speech:** AvalAI (Whisper), Gemini, Local

---

## 📁 ساختار پروژه

```
├── app.py                  # نقطه ورود
├── config.py               # تنظیمات
├── extensions.py           # Rate Limiter
├── startup.py              # preload services
├── wsgi.py                 # production entry
│
├── database/
│   ├── db.py
│   └── models/            # ۹ مدل
│
├── routes/                # ۱۵ Blueprint
│   ├── admin.py           # 🆕 پنل مدیریت
│   ├── auth.py, chat.py, diagnosis.py
│   ├── breathing.py, meditation.py, weekly_plan.py
│   ├── garden.py, subscription.py, health.py
│   ├── notes.py (با ضبط صدا)
│   └── ...
│
├── utils/
│   ├── helpers.py, logger.py, errors.py
│   ├── features.py (اشتراک)
│   ├── garden_helper.py
│   ├── admin_helpers.py   # 🆕 توابع کمکی پنل ادمین
│   ├── llm/               # Provider pattern
│   ├── speech/            # Provider pattern
│   └── rag/               # RAG
│
├── templates/             # ۲۵+ HTML
│   ├── admin/             # 🆕 قالب‌های پنل مدیریت
│   │   ├── base.html, dashboard.html, users.html
│   │   └── user_detail.html, diagnoses.html, notes.html
│   └── ...
│
├── static/
│   ├── css/               # Design System + ۶ تم
│   │   └── admin.css      # 🆕 استایل پنل مدیریت
│   ├── js/                # ماژولار
│   └── images/
│
├── migrations/            # Alembic
├── data/                  # دیتاست + cache
├── logs/                  # app.log, errors.log
├── docs/
│   └── screenshots/       # ۸ تصویر
└── tests/                 # ۳۲۷ تست
├── test_admin.py      # 🆕 تست‌های پنل مدیریت
├── test_meditation.py # تست‌های مدیتیشن
└── ...```

---

## 🚀 نصب و راه‌اندازی

### پیش‌نیازها
- Python 3.10+
- pip
- Git
- PostgreSQL 15+ (اختیاری — برای production)

### نصب

```bash
# ۱. کلون
git clone https://github.com/sadaf92901/aramesh.git
cd aramesh

# ۲. Virtual Environment
python -m venv venv

# ویندوز
venv\Scripts\activate

# لینوکس/مک
source venv/bin/activate

# ۳. نصب پکیج‌ها
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### تنظیمات

```bash
# کپی فایل نمونه
copy .env.example .env   # ویندوز
cp .env.example .env     # لینوکس/مک
```

**محتوای `.env`:**

```bash
SECRET_KEY=<رشته ۶۴ کاراکتری>
FLASK_ENV=development

# Database (SQLite برای dev)
DATABASE_URL=sqlite:///aramesh.db

# یا PostgreSQL
# DATABASE_URL=postgresql://aramesh:aramesh123@localhost:5432/aramesh

# LLM + Speech (AvalAI)
LLM_PROVIDER=openai
OPENAI_API_KEY=aa-...
OPENAI_BASE_URL=https://api.avalai.ir/v1
OPENAI_MODEL=gpt-4o-mini

SPEECH_PROVIDER=avalai
```

**برای ساخت SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### دیتابیس

#### گزینه ۱: SQLite (ساده — برای development)

```bash
DATABASE_URL=sqlite:///aramesh.db
python app.py
```

#### گزینه ۲: PostgreSQL (production)

**نصب PostgreSQL:**
- [Windows](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads)
- [Ubuntu](https://www.postgresql.org/download/linux/ubuntu/)

**ساخت Database:**

```sql
CREATE DATABASE aramesh;
CREATE USER aramesh WITH PASSWORD 'aramesh123';
GRANT ALL PRIVILEGES ON DATABASE aramesh TO aramesh;
ALTER DATABASE aramesh OWNER TO aramesh;
```

**Migration:**

```bash
flask db upgrade
```

### اجرا

```bash
python app.py
```

**باز کن:** `http://localhost:5000`

### Healthcheck

```bash
curl http://localhost:5000/healthz
curl http://localhost:5000/healthz/ready
curl http://localhost:5000/healthz/live
```

---

## 🧪 تست

```bash
# همه‌ی تست‌ها
pytest tests/ -v

# با Coverage
pytest tests/ --cov=. --cov-report=term-missing

# فقط باغ
pytest tests/test_garden.py -v

# فقط امنیت
pytest tests/test_security.py -v
```

**آمار:**
- **۳۲۷ تست**
- **Coverage: ۸۰٪**
- **زمان: ~۲ دقیقه**

---

## 📊 Lighthouse

| بخش | نمره |
|-----|------|
| **Accessibility** | **۱۰۰** 🏆 |
| **Best Practices** | **۱۰۰** 🏆 |
| **SEO** | **۹۰** ✅ |
| **Performance** | ۶۶ (localhost — در production بهتر) |

**چطور تست کنی:**
1. F12 → Lighthouse
2. انتخاب: Accessibility + SEO + Best Practices
3. Analyze page load

---

## 🎨 تم‌ها

۶ تم رنگی + ۲ حالت:

| تم | رنگ |
|-----|------|
| 🟣 بنفش | #8B5CF6 (پیش‌فرض) |
| 🔵 آبی | #3B82F6 |
| 🟢 سبز | #10B981 |
| 🩷 صورتی | #EC4899 |
| 🟠 نارنجی | #F59E0B |
| ⚫ خاکستری | #64748B |

**تغییر تم:** از دکمه‌ی 🎨 توی سایدبار یا bottom-nav.

---

## 📝 مستندات

- [README.md](README.md) — این فایل
- [CHANGELOG.md](CHANGELOG.md) — تاریخچه تغییرات
- [CONTRIBUTING.md](CONTRIBUTING.md) — راهنمای مشارکت
- [SECURITY.md](SECURITY.md) — سیاست امنیتی
- [DEPLOYMENT.md](DEPLOYMENT.md) — راهنمای Deploy
- [.env.example](.env.example) — نمونه تنظیمات

---

## 🗺 نقشه‌ی راه

### ✅ انجام شده
- [x] ...
- [x] پنل مدیریت (Admin Panel) 🆕
- [x] تست‌های پنل ادمین و مدیتیشن 🆕
- [x] رفع باگ‌های UI (آواتار، خروج، تم‌ها) 🆕
- [x] ۳۲۷ تست + Coverage ۸۰٪

### 🟡 در حال انجام
- [ ] Docker + docker-compose
- [ ] Deploy روی VPS (لیارا)
- [ ] Capacitor (APK)
- [ ] مجوز وزارت بهداشت

### 🔴 آینده
- [ ] Sentry integration
- [ ] Push Notifications
- [ ] درگاه پرداخت (Zarinpal)
- [ ] Analytics
- [ ] Community---

## 🤝 مشارکت

از اینکه می‌خوای کمک کنی، ممنون! 💚

راهنمای کامل توی [CONTRIBUTING.md](CONTRIBUTING.md) هست.

**خلاصه:**
1. Fork کن
2. Branch بساز (`git checkout -b feature/amazing`)
3. Commit کن (`git commit -m 'feat: add amazing'`)
4. Push کن (`git push origin feature/amazing`)
5. Pull Request باز کن

---

## 🔒 امنیت

اگه آسیب‌پذیری پیدا کردی، **عمومی نکن**. به [SECURITY.md](SECURITY.md) مراجعه کن.

📧 **security@aramesh.app**

---

## 📜 مجوز

این پروژه تحت [MIT License](LICENSE) منتشر شده.

---

## 🙏 تشکر

- [Vazirmatn](https://github.com/rastikerdar/vazirmatn) — فونت فارسی
- [Lucide](https://lucide.dev) — آیکون‌ها
- [AvalAI](https://avalai.ir) — LLM + Speech
- [OpenAI](https://openai.com) — GPT + Whisper
- [Google Gemini](https://ai.google.dev) — LLM + Speech
- [sentence-transformers](https://www.sbert.net) — Embedding

---

## 📞 تماس

- 📧 ایمیل: [support@aramesh.app](mailto:support@aramesh.app)
- 🐛 باگ: [bugs@aramesh.app](mailto:bugs@aramesh.app)
- 🔒 امنیت: [security@aramesh.app](mailto:security@aramesh.app)

---

<div align="center">

**🌿 همراه آرامش — هر قدم کوچک، یک تغییر بزرگ 🌿**

**ساخته شده با 💚**

</div>
