# 📝 تاریخچه تغییرات — همراه آرامش

تمام تغییرات مهم این پروژه توی این فایل ثبت می‌شه.

فرمت بر اساس [Keep a Changelog](https://keepachangelog.com/fa/1.1.0/) هست
و پروژه از [Semantic Versioning](https://semver.org/lang/fa/) پیروی می‌کنه.

---

## [Unreleased]
## [1.2.0] — 1405/07/24

### ✨ اضافه شده

#### 🎤 ضبط صدا در روزنگار
- کاربر می‌تونه به جای تایپ، صدا ضبط کنه
- تبدیل خودکار صدا به متن (Whisper/Gemini)
- امکان ویرایش متن بعد از تبدیل
- فایل صوتی بعد از تبدیل پاک می‌شه (حریم خصوصی)
- حداکثر ۵ دقیقه / ۵ مگابایت
- UI زیبا با timer + waveform

#### 🗄️ مهاجرت به PostgreSQL
- مهاجرت کامل از SQLite به PostgreSQL 18
- افزودن psycopg2-binary
- پشتیبانی از هر دو دیتابیس (SQLite + PostgreSQL)
- Migration کامل با Alembic
- ۹ جدول در PostgreSQL
- راهنمای Migration

#### 🤖 Gemini Provider
- افزودن GeminiProvider برای LLM
- افزودن GeminiSpeechProvider برای Speech
- پشتیبانی از gemini-2.5-flash
- Provider قابل تعویض (Gemini ↔ OpenAI ↔ Local)

### 🔄 تغییر یافته

- **config.py** → LLM_PROVIDER و SPEECH_PROVIDER از .env می‌خونن
- **utils/speech/service.py** → پشتیبانی از Gemini + Local
- **utils/llm/service.py** → پشتیبانی از Gemini
- **database/db.py** → چک SQLite/Postgapp.py FK
- **app.py** → ensure_database_ready فقط برای SQLite

##sanitize_inputsanitize_input** → حذف null bytes (\x00) برای PostgreSQL
- **speech/service.py** → رفع IndentationError در else
- **config.py** → LLM_PROVIDER از .env می‌خونه
- **PostgreSQL** → سازگاری کامل با SQLAفایل صوتی روزنگارنیت

- **فایل صوتی روزنگارsanitize_inputک می‌شه
- **sanitize_input** → حذف \x00 (Rate Limitingjection)
- **Rate Limiting** برای /api/notes/transcribe

### 🧪 تCoverage: ۸۰٪ت**تست‌های جدید:erage: ۸۰٪**
- **تست‌های جدید:**
  - test_notes/transcribe (ضبط صدا)
  - PostgreSQL compatibility

### 📊 Lighthouse

| بخش | نمره |
|۱۰۰-----|
| Accessibility | ۱۰۰ 🏆 |
| Best P۹۰es | **۱۰۰** 🏆 |
| SEO CHANGELOG.md# 📄 مستندات

- **CHANGELOG.md** آپدیت شد
- **README.md** آپدیت ش.env.exampleGemini + ضبط صدا)
- **.env.example** آپدیت شد
- **DEPLOYMENT.md** آپدیت شد

---
### 🎯 در حال توسعه

- 🐝 افزودن زنبور و عناصر زنده به باغ
- 💧 قطره‌های شبنم روی گل‌ها
- 🌈 رنگین‌کمون
- 🐳 Docker setup
- 🔄 PostgreSQL support
- 📊 Sentry integration
- 💰 درگاه پرداخت (Zarinpal)
- 👥 پنل ادمین
- 📱 Capacitor (APK برای کافه بازار)
- 🔔 Push Notifications


## [1.1.0] — 1405/07/18

### ✨ اضافه شده

#### 🎨 صفحه‌ی اشتراک جدید
- **صفحه‌ی مستقل `/subscription`** (جدا از مودال قدیمی)
- **پلن فعلی** با نمایش وضعیت استفاده
- **نوارهای پیشرفت** برای تشخیص، چت، یاداشت
- **ویژگی‌های فعال** در گرید دو ستونه
- **کارت پریمیوم** (به‌زودی) با دکمه‌ی اطلاع‌رسانی
- **FAQ** با ۵ سؤال متداول (accordion)
- **کاملاً تم‌پذیر** با CSS Variables
- **لینک از سایدبار + پروفایل**

#### 🌸 بهبود UX باغ آرامش
- **Toggle صدا** (روشن/خاموش) در هدر باغ + پروفایل
- **ذخیره در localStorage** (تنظیمات باقی می‌مونه)
- **Empty state** برای باغ خالی با ۴ دکمه‌ی شروع سریع
- **ذخیره‌ی position_x/y** گل‌ها در دیتابیس (موقعیت ثابت)
- **Cache در localStorage** برای `/api/garden` (TTL ۳۰ ثانیه)
- **Fallback** برای گل‌های قدیمی (بدون position)

#### 🔍 SEO
- **Meta tags کامل**: description, keywords, author, robots
- **Open Graph** برای شبکه‌های اجتماعی
- **Twitter Card**
- **عنوان معنادار**: "همراه آرامش — همراه سلامت روان شما"
- **`lang="fa"` و `dir="rtl"`**
- **`og-image.png`** (۱۲۰۰×۶۳۰)

#### ♿ Accessibility
- **`aria-label`** روی همه‌ی دکمه‌ها و لینک‌ها
- **`role`** مناسب: `button`, `dialog`, `region`, `main`, `banner`, `navigation`
- **`tabindex`** روی عناصر تعاملی
- **`aria-hidden`** روی آیکون‌های تزئینی
- **`aria-modal`** + **`aria-labelledby`** روی مودال‌ها
- **`aria-current`** برای صفحه‌ی فعال
- **ساختار semantic**: `header`, `main`, `aside`, `nav`
- **نمره‌ی Lighthouse: ۱۰۰** 🏆

### 🔄 تغییر یافته

- **مودال اشتراک قدیمی حذف شد** → به صفحه‌ی جدید منتقل شد
- **`profile.js`** فقط در صفحه‌ی پروفایل لود می‌شه (نه همه‌جا)
- **موقعیت گل‌ها** از DB خونده می‌شه (به‌جای تصادفی هر بار)
- **باغ** از cache استفاده می‌کنه (سریع‌تر)
- **`main.js`** دیگه `loadTheme()` رو صدا نمی‌زنه (theme.js خودش انجام می‌ده)
- **`ui.js`** دیگه `toggleTheme` نداره (فقط theme.js)

### 🐛 رفع شده

#### 🔴 P0 (Critical)
- **`type(error).name`** → **`type(error).__name__`** در `logger.py`
- **پاک کردن فایل صوتی** بعد از transcribe (حریم خصوصی)
- **`ensure_database_ready`** فقط در development
- **rename** `routes/garand.py` → `routes/garden.py`

#### 🟠 P1 (Important)
- **`db.session.get()`** جایگزین `User.query.get()` (SQLAlchemy 2.0)
- **`utcnow` helper** جایگزین `datetime.utcnow` (deprecated)
- **Cache Vector Store** برای RAG (startup سریع‌تر از ۱۰s به <۱s)
- **Rate Limiter** با پشتیبانی از `X-Forwarded-For` و `CF-Connecting-IP`
- **XSS protection** در `routes/status.py` با whitelist

#### 🟡 P2 (Improvement)
- **SMTP واقعی** برای ارسال ایمیل (به‌جای Mock)
- **Service Worker** فقط در production (نه development)
- **حذف تداخل** `toggleTheme` بین `ui.js` و `theme.js`
- **Foreign Key** در SQLite فعال شد
- **`profile.js`** توی صفحات دیگه خطا نمی‌ده

### 🔒 امنیت

- **XSS** در `routes/status.py` رفع شد (whitelist + sanitize)
- **Foreign Key constraint** در SQLite فعال شد
- **فایل صوتی** بعد از استفاده پاک می‌شه
- **`user_id` نامعتبر** در `give_seed` چک می‌شه

### 🧪 تست‌ها

- **۳۰۷ تست** (از ۱۷۲)
- **Coverage: ۸۱٪** (از ۷۳٪)
- **تست‌های جدید:**
  - `test_garden.py` (۲۰ تست)
  - `test_garden_edge_cases.py` (۱۲ تست)
  - `test_subscription.py` (۱۵ تست)
  - `test_daily_status_extended.py` (۱۱ تست)
  - `test_features.py` (۲۴ تست)
  - `test_llm_parser.py` (۱۴ تست)
  - `test_rag_mock.py` (۱۵ تست)
  - `test_anonymized_samples.py` (۴ تست)
  - `test_rate_limiting.py` (۵ تست)

### 📊 Lighthouse

| بخش | نمره |
|-----|------|
| Accessibility | **۱۰۰** 🏆 |
| Best Practices | **۱۰۰** 🏆 |
| SEO | **۹۰** ✅ |
| Performance | ۶۶ (localhost — در production بهتر می‌شه) |

### 📄 مستندات

- **`CHANGELOG.md`** آپدیت شد
- **`README.md`** آپدیت شد
- **`DEPLOYMENT.md`** اضافه شد
- **`.env.example`** آپدیت شد


## [1.0.2] — 1405/07/11

### ✨ اضافه شده

#### 🌸 باغ آرامش
- **باغ تعاملی** با ۵ نوع گل
  - 🌸 تشخیص
  - 🌷 یاداشت
  - 🌿 تمرین تنفس
  - 🪷 مدیتیشن
  - 🌻 وضعیت روزانه
- **کیف دانه** — هر فعالیت → یه دانه (روزانه ۱ بار از هر نوع)
- **کاشتن دستی** — کاربر خودش می‌کاره
- **صحنه‌ی باغ با عکس واقعی**
  - پس‌زمینه‌ی تصویری (`garden-bg.jpg`)
  - ۳ پروانه با مسیرهای طبیعی
  - ذرات نور موقع کاشتن
  - کانفتی (جشن) موقع ساخت بوته‌ی جدید
- **ادغام هوشمند گل‌ها**
  - **هر ۱۰ گل هم‌نوع** → **🌳 بوته‌ی `×۱۰`**
  - **هر ۱۰۰ گل هم‌نوع** → **🏞️ باغچه‌ی `×۱۰۰`**
  - **گل‌های تکی** (کمتر از ۱۰) → **باقی می‌مونن**
- **۹ سطح باغ**
  - 🌱 تازه‌کار (۰-۱۰)
  - 🌿 باغبون (۱۰-۳۵)
  - 🌳 باغبون ماهر (۳۵-۷۰)
  - 🌲 استاد باغبون (۷۰-۱۵۰)
  - 🏆 باغ‌بهشت (۱۵۰-۳۰۰)
  - 👑 باغبون افسانه‌ای (۳۰۰-۶۰۰)
  - 💎 باغبون جاودانه (۶۰۰-۱۰۰۰)
  - 🌟 اسطوره‌ی باغ (۱۰۰۰-۲۰۰۰)
  - 🌌 خدای باغ (۲۰۰۰+)
- **۱۱ دستاورد**
- **مودال پیشرفت باغ** (سطح + نمودار + دستاوردها)
- **نمودار رشد** (۵ نوع گل با میله‌های رنگی)
- **مودال حرفه‌ای گل** (توضیح + جمله‌ی الهام‌بخش)
- **صدا** (کاشتن + جشن) با Web Audio API
- **ذرات نور** موقع کاشتن
- **کانفتی** موقع ساخت بوته‌ی جدید
- **Badge** روی کارت باغ (تعداد دانه‌ها)

### 🔄 تغییر یافته

- **کارت باغ** توی صفحه‌ی اصلی، بعد از «امروز چطوری»
- **گل‌ها** به جای آیکون‌های فعالیت، شکل واقعی گل دارن
- **مودال گل** با اطلاعات کامل‌تر (تاریخ + توضیح + جمله)


## [1.0.1] — 1405/07/11

### ✨ اضافه شده

#### 🔐 امنیت
- **تست‌های امنیتی** (۲۴ تست)
  - XSS Protection
  - SQL Injection
  - Input Validation
  - Authorization
  - Session Security
  - Rate Limiting
  - Security Headers
  - File Upload
- **Security Headers** کامل
  - `X-Frame-Options: SAMEORIGIN`
  - `X-Content-Type-Options: nosniff`
  - `X-XSS-Protection: 1; mode=block`
  - `Referrer-Policy: strict-origin-when-cross-origin`
  - `Permissions-Policy: geolocation=(), microphone=(self), camera=()`
- **Rate Limiting گسترده** (Flask-Limiter)
  - `/api/login` → ۵/دقیقه + ۲۰/ساعت
  - `/api/register` → ۳/ساعت
  - `/api/chat` → ۵۰/روز
  - `/api/predict` → ۳/روز
  - `/api/upload-audio` → ۹/روز
  - همه‌ی APIها → ۲۰۰/روز + ۵۰/ساعت (Prod) / ۱۰۰۰۰/روز (Dev)
- **تأخیر تدریجی** روی ورود ناموفق (۵s → ۱۵s → ۳۰s → ۱m → ۲m → ۵m)
- **شمارنده‌ی پیام** توی چت‌بات (۵۰/روز)
- **بنر تشخیص** توی صفحه‌ی اصلی (۳/روز)

#### 📝 Logging
- **سیستم Logging ساختارمند**
  - `logs/app.log` (همه‌ی لاگ‌ها)
  - `logs/errors.log` (فقط خطاها)
  - گردش خودکار (10MB × 5 فایل)
- **تبدیل همه‌ی `print`ها به `logger`** توی routeها

#### 🗄️ دیتابیس
- **Migration** با Flask-Migrate + Alembic
  - پوشه‌ی `migrations/`
  - ۷ جدول ساخته شد
  - آماده برای تغییرات آینده

#### 🎨 UI/UX
- **Design System** کامل
  - `design-system.css` با CSS Variables
  - رنگ، فاصله، فونت، سایه، Transition
- **تم پیشرفته**
  - `themes.css` با ۶ رنگ
  - `theme-modal.css` برای مودال
  - `theme-override.css` برای override
  - `theme.js` برای مدیریت
- **۶ تم رنگی**: بنفش، آبی، سبز، صورتی، نارنجی، خاکستری
- **۲ حالت نمایش**: روشن، تیره
- **دکمه‌ی تم** توی نوار پایین (موبایل) + سایدبار (دسکتاپ)

### 🔄 تغییر یافته

- **`extensions.py`** برای رفع Circular Import
- **`startup.py`** برای جدا کردن `preload_services`
- **`utils/logger.py`** جایگزین `print`
- **`Query.get()`** → `db.session.get()` (SQLAlchemy 2.0)
- **`app.py`** → `ensure_database_ready()` برای ساخت خودکار جدول‌ها

### 🐛 رفع شده

- **Warningهای SQLAlchemy** (LegacyAPIWarning)
- **XSS توی `routes/notes.py`** → `sanitize_input` اضافه شد
- **Typo `peer` → `per`** توی Rate Limiting
- **Circular Import** بین `app.py` و `routes/`
- **`alembic_version` ناهماهنگ** → `ensure_database_ready` حلش کرد

### 🧪 تست‌ها

- **۱۷۲ تست** (از ۱۴۹)
- **Coverage: ۷۳٪** (از ۶۸٪)
- **۰ Warning**
- **۰ `print`** توی routeها

### 📄 مستندات

- **`README.md`** کامل بازنویسی شد
- **`CONTRIBUTING.md`** اضافه شد
- **`SECURITY.md`** اضافه شد
- **`CHANGELOG.md`** اضافه شد
- **`.env.example`** کامل آپدیت شد


## [1.0.0] — 1405/07/10

### ✨ اضافه شده

#### 🧠 هوش مصنوعی
- تشخیص هوشمند بر اساس **DSM-5** و **GAD-7**
- ترکیب **MCQ** (۲۰ سوال) + **LLM** (۳ سوال باز)
- **RAG** با ۳۱۲ نمونه از دیتاست روانشناسی فارسی
- **Speech-to-Text** با AvalAI (Whisper)
- **Chatbot** همدل با GPT-4o-mini
- **Fallback** خودکار وقتی LLM در دسترس نیست
- **پروتکل بحران** با تشخیص کلمات کلیدی

#### 🎨 UI/UX
- **Design System** کامل با CSS Variables
- **۶ تم رنگی** (بنفش، آبی، سبز، صورتی، نارنجی، خاکستری)
- **۲ حالت نمایش** (روشن، تیره)
- **ذخیره خودکار** انتخاب کاربر
- **Onboarding** ۵ مرحله‌ای
- **Dark Mode** کامل
- **RTL** حرفه‌ای
- **Responsive** (موبایل، تبلت، دسکتاپ)
- **Loading States**
- **Empty States**
- **Error Handling**

#### 🔐 امنیت
- **bcrypt** برای هش رمز
- **Rate Limiting** با Flask-Limiter
- **تأخیر تدریجی** روی ورود ناموفق
- **Security Headers**
- **Session Security**
- **Input Sanitization**
- **File Upload Validation**

#### 🗄️ دیتابیس
- **Flask-Migrate + Alembic** برای migration
- **۷ مدل** (User, Diagnosis, DailyStatus, DailyNote, BreathingExercise, WeeklyPlan, Meditation)
- **Foreign Key Constraints**
- **Cascade Delete** برای داده‌های کاربر

#### 📝 Logging
- **سیستم Logging** ساختارمند
- **سطوح مختلف** (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **ذخیره توی فایل** (`logs/app.log` و `logs/errors.log`)
- **گردش خودکار** (10MB × 5 فایل)

#### 🧪 تست
- **۱۴۹ تست** با pytest
- **Coverage ۶۸٪**
- **Unit Tests** برای توابع کمکی
- **Integration Tests** برای APIها
- **Mock Tests** برای LLM و Speech

#### 📄 مستندات
- **README.md** کامل (فارسی)
- **CONTRIBUTING.md** راهنمای مشارکت
- **SECURITY.md** سیاست امنیتی
- **CHANGELOG.md** تاریخچه تغییرات
- **.env.example** نمونه تنظیمات
- **LICENSE** (MIT)

### 🔄 تغییر یافته

- **معماری** از تابعی به **Provider-based**
- **سرویس‌ها** به Singleton pattern
- **Frontend** به ES Modules
- **تست‌ها** به pytest (از unittest)
- **لاگ‌ها** از print به logging

### 🐛 رفع شده

- Circular Import بین `app.py` و `routes/`
- مشکل `0 || 300` توی JavaScript
- Service Worker cache قدیمی
- Rate Limiting UI بعد از ۵ خطا
- `NotImplementedErrorv` typo

### ❌ حذف شده

- فایل‌های تست قدیمی (`bb.html`, `tt.html`, `tttttt.html`)
- `create_db.py` (جایگزین با SQLAlchemy)
- `database.py` روت (جایگزین با `database/`)
- `data.json` قدیمی
- `pycache/` اشتباه


---

## 🏷 نسخه‌های آینده

### [1.2.0] — برنامه‌ریزی‌شده
- 🐝 زنبور و عناصر زنده به باغ
- 💧 قطره‌های شبنم
- 🌈 رنگین‌کمون
- 🐳 Docker + docker-compose
- 🗄️ PostgreSQL migration
- 📊 Matomo Analytics

### [1.3.0] — برنامه‌ریزی‌شده
- 💰 درگاه پرداخت
- 👥 پنل ادمین
- 📧 SMTP واقعی
- 🌐 SEO
- 📱 Capacitor (APK)

### [2.0.0] — برنامه‌ریزی‌شده
- 📱 اپ موبایل (Capacitor)
- 🔔 Push Notifications
- 👨‍⚕️ مشاوره آنلاین
- 🏢 B2B (کلینیک‌ها)


---

## 📖 راهنمای نسخه‌گذاری

**Semantic Versioning:**

| نوع | مثال | تغییر |
|-----|------|-------|
| **MAJOR** | 1.0.0 → 2.0.0 | تغییر ناسازگار |
| **MINOR** | 1.0.0 → 1.1.0 | فیچر جدید |
| **PATCH** | 1.0.0 → 1.0.1 | باگ‌فیکس |


---

## 📝 انواع تغییرات

| نماد | نوع | توضیح |
|------|-----|-------|
| ✨ | **اضافه شده** | فیچر جدید |
| 🔄 | **تغییر یافته** | تغییر در فیچر موجود |
| ⚠️ | **منسوخ** | فیچر قدیمی که حذف می‌شه |
| ❌ | **حذف شده** | فیچر حذف‌شده |
| 🐛 | **رفع شده** | باگ‌فیکس |
| 🔒 | **امنیت** | رفع آسیب‌پذیری |


---

<div align="center">

**📖 برای دیدن تغییرات، این فایل رو دنبال کن 📖**

</div>
