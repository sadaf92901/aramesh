# ============================================================
# extensions.py — Extensionهای مشترک
# ============================================================

import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import session, request
from utils.logger import logger

# ============================================================
# تعیین کلید برای Rate Limiter
# ============================================================

def get_user_or_ip():
    """
    اگه کاربر لاگین باشه → user_id
    وگرنه → IP واقعی (پشت proxy هم درست کار می‌کنه)
    """
    # ===== ۱. اگه کاربر لاگین باشه =====
    user_id = session.get('user_id')
    if user_id:
        return f"user_{user_id}"

    # ===== ۲. تلاش برای خواندن IP واقعی از proxy =====
    # X-Forwarded-For: client, proxy1, proxy2
    # اولین IP → کاربر واقعی
    forwarded_for = request.headers.get('X-Forwarded-For')
    if forwarded_for:
        # اولین IP رو بردار
        client_ip = forwarded_for.split(',')[0].strip()
        if client_ip:
            return client_ip

    # ===== ۳. Cloudflare =====
    cf_ip = request.headers.get('CF-Connecting-IP')
    if cf_ip:
        return cf_ip

    # ===== ۴. fallback =====
    return get_remote_address()


# ============================================================
# تنظیمات Rate Limiter
# ============================================================

is_development = os.environ.get('FLASK_ENV', 'development') == 'development'

if is_development:
    # ===== توی development: محدودیت‌های خیلی بالا =====
    limiter = Limiter(
        key_func=get_user_or_ip,
        default_limits=["10000 per day", "2000 per hour"],
        storage_uri="memory://",
        strategy="fixed-window",
        headers_enabled=True,
    )
    logger.info("🔧 Rate Limiter: Development mode (محدودیت‌های بالا)")
else:
    # ===== توی production: محدودیت‌های واقعی =====
    limiter = Limiter(
        key_func=get_user_or_ip,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://",
        strategy="fixed-window",
        headers_enabled=True,
    )
    logger.info("🔒 Rate Limiter: Production mode (محدودیت‌های واقعی)")