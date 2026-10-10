# ============================================================
# همراه آرامش — Logging
# ============================================================
# سیستم Logging ساختارمند با:
#   - سطوح مختلف (DEBUG, INFO, WARNING, ERROR, CRITICAL)
#   - ذخیره توی فایل
#   - گردش فایل خودکار (rotation)
#   - خروجی همزمان توی Console
# ============================================================

import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime


# ============================================================
# مسیر فایل‌های لاگ
# ============================================================

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

APP_LOG = os.path.join(LOG_DIR, 'app.log')
ERROR_LOG = os.path.join(LOG_DIR, 'errors.log')


# ============================================================
# فرمت لاگ
# ============================================================

LOG_FORMAT = '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)


# ============================================================
# ساخت Logger
# ============================================================

def setup_logger(name='aramesh', level=logging.INFO):
    """
    ساخت یه Logger با تنظیمات استاندارد

    Args:
        name: اسم logger
        level: سطح لاگ (پیش‌فرض: INFO)

    Returns:
        logging.Logger
    """

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # ===== اگه قبلاً handler اضافه شده، دوباره اضافه نکن =====
    if logger.handlers:
        return logger

    # ============================================================
    # 1. Console Handler (برای development)
    # ============================================================
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # ============================================================
    # 2. File Handler (همه‌ی لاگ‌ها)
    # ============================================================
    # ⚠️ RotatingFileHandler: وقتی فایل به ۱۰ مگابایت رسید، یه فایل جدید می‌سازه
    # و ۵ فایل قدیمی رو نگه می‌داره
    file_handler = RotatingFileHandler(
        APP_LOG,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # ============================================================
    # 3. Error File Handler (فقط خطاها)
    # ============================================================
    error_handler = RotatingFileHandler(
        ERROR_LOG,
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)

    return logger


# ============================================================
# Logger پیش‌فرض
# ============================================================

logger = setup_logger()


# ============================================================
# تابع کمکی: لاگ کردن درخواست‌های HTTP
# ============================================================

def log_request(request, user_id=None):
    """
    لاگ کردن یه درخواست HTTP

    Args:
        request: Flask request object
        user_id: آی‌دی کاربر (اگه لاگین باشه)
    """

    # ===== اطلاعات درخواست =====
    method = request.method
    path = request.path
    ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', 'Unknown')[:100]

    # ===== کاربر =====
    user_info = f"user_id={user_id}" if user_id else "anonymous"

    # ===== لاگ =====
    logger.info(f"{method} {path} | {user_info} | IP={ip} | UA={user_agent}")

# ============================================================
# تابع کمکی: لاگ کردن خطا
# ============================================================

def log_error(error, context=''):
    """
    لاگ کردن یه خطا با context

    Args:
        error: Exception object
        context: توضیح کجای کد خطا داده
    """

    logger.error(f"{context} | {type(error).__name__}: {error}", exc_info=True)

# ============================================================
# صادر کردن
# ============================================================

__all__ = ['logger', 'setup_logger', 'log_request', 'log_error']