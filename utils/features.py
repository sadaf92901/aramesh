# ============================================================
# همراه آرامش — Feature Flags
# ============================================================
# مدیریت محدودیت‌های پلن‌ها (رایگان، پریمیوم، سازمانی)
# ============================================================

from datetime import datetime


# ============================================================
# آیا پریمیوم فعاله؟
# ============================================================
# False → همه‌چیز رایگان (حالت فعلی)
# True  → رایگان + پریمیوم (بعداً)

PREMIUM_AVAILABLE = False


# ============================================================
# محدودیت‌های پلن رایگان (کامل)
# ============================================================

FREE_LIMITS = {
    # ===== تشخیص =====
    'diagnosis_per_day': 5,
    'diagnosis_per_month': 50,

    # ===== چت =====
    'chat_per_day': 50,
    'chat_per_month': 500,

    # ===== روزنگار =====
    'notes_per_day': 20,
    'notes_per_month': 200,

    # ===== تاریخچه =====
    'history_days': 365,

    # ===== ویژگی‌ها =====
    'rag_enabled': True,
    'llm_summary': True,
    'pdf_export': True,
    'premium_themes': False,
    'cloud_backup': False,

    # ===== برچسب =====
    'plan_name': 'رایگان',
    'plan_icon': '🆓',
}


# ============================================================
# محدودیت‌های پلن پریمیوم
# ============================================================

PREMIUM_LIMITS = {
    # ===== تشخیص =====
    'diagnosis_per_day': -1,
    'diagnosis_per_month': -1,

    # ===== چت =====
    'chat_per_day': -1,
    'chat_per_month': -1,

    # ===== روزنگار =====
    'notes_per_day': -1,
    'notes_per_month': -1,

    # ===== تاریخچه =====
    'history_days': 365,

    # ===== ویژگی‌ها =====
    'rag_enabled': True,
    'llm_summary': True,
    'pdf_export': True,
    'premium_themes': True,
    'cloud_backup': True,

    # ===== برچسب =====
    'plan_name': 'پریمیوم',
    'plan_icon': '⭐',
}


# ============================================================
# محدودیت‌های پلن سازمانی
# ============================================================

PRO_LIMITS = {
    **PREMIUM_LIMITS,
    'plan_name': 'سازمانی',
    'plan_icon': '🏢',
    'api_access': True,
    'clinic_panel': True,
}


# ============================================================
# گرفتن محدودیت‌های کاربر
# ============================================================

def get_user_limits(user):
    """
    گرفتن محدودیت‌های کاربر بر اساس اشتراک

    Args:
        user: آبجکت User

    Returns:
        dict: محدودیت‌ها
    """
    # ===== اگه پریمیوم فعال نیست → همه رایگان کامل =====
    if not PREMIUM_AVAILABLE:
        return FREE_LIMITS

    # ===== پریمیوم فعاله → چک کن =====
    if not user:
        return FREE_LIMITS

    from database.models import Subscription

    subscription = Subscription.query.filter_by(
        user_id=user.id,
        status='active'
    ).order_by(Subscription.id.desc()).first()

    if subscription and subscription.is_active():
        if subscription.plan == 'pro':
            return PRO_LIMITS
        elif subscription.plan == 'premium':
            return PREMIUM_LIMITS

    return FREE_LIMITS


def is_premium(user):
    """آیا کاربر پریمیوم داره؟"""
    if not PREMIUM_AVAILABLE:
        return False
    limits = get_user_limits(user)
    return limits.get('plan_name') != 'رایگان'


def can_use(user, feature):
    """
    چک کن آیا کاربر می‌تونه از یه ویژگی استفاده کنه

    Args:
        user: آبجکت User
        feature: اسم ویژگی

    Returns:
        bool
    """
    limits = get_user_limits(user)
    return limits.get(feature, False) is True


# ============================================================
# چک محدودیت روزانه
# ============================================================

def check_daily_limit(user, feature, current_count):
    """
    چک کن آیا کاربر به محدودیت روزانه رسیده

    Args:
        user: آبجکت User
        feature: اسم ویژگی (diagnosis_per_day, chat_per_day, notes_per_day)
        current_count: تعداد فعلی امروز

    Returns:
        dict: {'allowed': bool, 'limit': int, 'remaining': int}
    """
    limits = get_user_limits(user)
    limit = limits.get(feature, 0)

    # ===== نامحدود =====
    if limit == -1:
        return {
            'allowed': True,
            'limit': -1,
            'remaining': -1,
            'message': None,
        }

    # ===== محدود =====
    if current_count >= limit:
        return {
            'allowed': False,
            'limit': limit,
            'remaining': 0,
            'message': f'به محدودیت روزانه رسیدی ({limit} بار). فردا دوباره تلاش کن. 🌱',
        }

    return {
        'allowed': True,
        'limit': limit,
        'remaining': limit - current_count,
        'message': None,
    }


def check_monthly_limit(user, feature, current_count):
    """چک محدودیت ماهانه"""
    limits = get_user_limits(user)
    limit = limits.get(feature, 0)

    if limit == -1:
        return {'allowed': True, 'limit': -1, 'remaining': -1, 'message': None}

    if current_count >= limit:
        return {
            'allowed': False,
            'limit': limit,
            'remaining': 0,
            'message': f'به محدودیت ماهانه رسیدی ({limit} بار).',
        }

    return {
        'allowed': True,
        'limit': limit,
        'remaining': limit - current_count,
        'message': None,
    }
