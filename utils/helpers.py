# ============================================================
# توابع کمکی
# ============================================================

import re
import json
from datetime import datetime, timedelta, timezone
import jdatetime


# ============================================================
# UTC Now (جایگزین datetime.utcnow)
# ============================================================

def utcnow():
    """
    زمان UTC بدون timezone (برای ذخیره در SQLite)

    چرا این تابع؟
    - datetime.utcnow() توی Python 3.12+ deprecated شده
    - datetime.now(timezone.utc) timezone-aware برمی‌گردونه
    - SQLite نمی‌تونه timezone-aware رو مستقیم ذخیره کنه

    Returns:
        datetime: زمان UTC بدون timezone
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)


def get_persian_date(date=None):
    """تبدیل تاریخ میلادی به شمسی"""
    if date is None:
        date = datetime.now()

    # تبدیل به تاریخ شمسی
    persian_date = jdatetime.datetime.fromgregorian(datetime=date)

    # نام ماه‌ها
    month_names = {
        1: 'فروردین', 2: 'اردیبهشت', 3: 'خرداد',
        4: 'تیر', 5: 'مرداد', 6: 'شهریور',
        7: 'مهر', 8: 'آبان', 9: 'آذر',
        10: 'دی', 11: 'بهمن', 12: 'اسفند'
    }

    return {
        'year': persian_date.year,
        'month': persian_date.month,
        'month_name': month_names.get(persian_date.month, ''),
        'day': persian_date.day,
        'weekday': persian_date.weekday(),
        'weekday_name': get_persian_weekday(persian_date.weekday()),
        'full': f"{persian_date.year} {month_names.get(persian_date.month, '')} {persian_date.day}"
    }


def get_persian_weekday(weekday):
    """دریافت نام روز هفته به فارسی"""
    weekdays = {
        0: 'شنبه',
        1: 'یکشنبه',
        2: 'دوشنبه',
        3: 'سه‌شنبه',
        4: 'چهارشنبه',
        5: 'پنجشنبه',
        6: 'جمعه'
    }
    return weekdays.get(weekday, '')


def get_persian_weekday_short(weekday):
    """دریافت نام کوتاه روز هفته به فارسی"""
    weekdays = {
        0: 'ش',
        1: 'ی',
        2: 'د',
        3: 'س',
        4: 'چ',
        5: 'پ',
        6: 'ج'
    }
    return weekdays.get(weekday, '')


def sanitize_input(text):
    """پاک‌سازی ورودی کاربر"""
    if not text:
        return ''

    # حذف تگ‌های HTML
    text = re.sub(r'<[^>]*>', '', text)

    # حذف کاراکترهای خطرناک
    text = re.sub(r'[<>{}()\[\]]', '', text)

    # محدودیت طول
    if len(text) > 1000:
        text = text[:1000]

    return text.strip()


def validate_email(email):
    """اعتبارسنجی ایمیل"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone):
    """اعتبارسنجی شماره موبایل ایران"""
    pattern = r'^09[0-9]{9}$'
    return re.match(pattern, phone) is not None


def calculate_age(birth_date):
    """محاسبه سن بر اساس تاریخ تولد"""
    today = datetime.now().date()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))


def format_file_size(size_in_bytes):
    """فرمت کردن حجم فایل"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.1f} {unit}"
        size_in_bytes /= 1024.0
    return f"{size_in_bytes:.1f} TB"


def is_allowed_file(filename, allowed_extensions):
    """بررسی مجاز بودن پسوند فایل"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def load_json_file(filepath):
    """بارگذاری فایل JSON"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def save_json_file(filepath, data):
    """ذخیره فایل JSON"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


def get_week_moods(moods_data):
    """گرفتن خلقیات هفته از دیتا"""
    week_days = []
    today = datetime.now().date()

    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        date_str = date.isoformat()

        mood = moods_data.get(date_str)

        if mood is not None and 0 <= mood <= 3:
            emojis = ['😊', '🙂', '😐', '😢']
            week_days.append({
                'day': get_persian_weekday_short(date.weekday()),
                'full_day': get_persian_weekday(date.weekday()),
                'icon': emojis[mood],
                'date': date_str,
                'value': mood,
                'has_data': True
            })
        else:
            week_days.append({
                'day': get_persian_weekday_short(date.weekday()),
                'full_day': get_persian_weekday(date.weekday()),
                'icon': '❓',
                'date': date_str,
                'value': None,
                'has_data': False
            })

    return week_days


def calculate_stats(moods_data):
    """محاسبه آمار خلقیات"""
    values = [v for v in moods_data.values() if isinstance(v, int) and 0 <= v <= 3]

    if not values:
        return {
            'total': 0,
            'average': 0,
            'healthy': 0,
            'mild': 0,
            'moderate': 0,
            'severe': 0
        }

    stats = {
        'total': len(values),
        'average': sum(values) / len(values),
        'healthy': values.count(0),
        'mild': values.count(1),
        'moderate': values.count(2),
        'severe': values.count(3)
    }

    return stats
