# 🌿 همراه آرامش

> **اپلیکیشن سلامت روان با تحلیل هوشمند متن و صوت فارسی**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![Tests](https://img.shields.io/badge/Tests-307%20Passed-success?style=for-the-badge)](tests/)
[![Coverage](https://img.shields.io/badge/Coverage-81%25-green?style=for-the-badge)](tests/)
[![Lighthouse](https://img.shields.io/badge/Lighthouse-100%20A11y-brightgreen?style=for-the-badge)](https://developers.google.com/web/tools/lighthouse)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.1.0-blue?style=for-the-badge)](CHANGELOG.md)

---

## 📖 درباره‌ی پروژه

**همراه آرامش** یه اپلیکیشن وب پیشرو (PWA) برای **سلامت روان** و **خودمراقبتی**ـه که به کاربر کمک می‌کنه:

- 🧠 وضعیت روانی خودش رو **بسنجه**
- 📊 روزانه حالاتش رو **ثبت کنه**
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
- تحلیل با **GPT-4o-mini** + **RAG**
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

### 📝 روزنگار
- نوشتن یاداشت روزانه
- ۷ حال مختلف
- برچسب‌گذاری
- فیلتر و **جستجو**

### 💬 چت‌بات همدل
- پاسخ‌های هوشمند با **GPT-4o-mini**
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
- **Foreign Key** در SQLite
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
| **SQLite** | دیتابیس (قابل تغییر به PostgreSQL) |
| **bcrypt** | هش رمز |
| **Flask-Limiter** | Rate Limiting |
| **jdatetime** | تاریخ شمسی |
| **Flask-Compress** | فشرده‌سازی (اختیاری) |

### AI & ML
| تکنولوژی | کاربرد |
|----------|--------|
| **AvalAI** | واسط LLM و Speech |
| **GPT-4o-mini** | تحلیل متن و چت |
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

---

## 🏗 معماری

### Provider-based (قابل تعویض)

