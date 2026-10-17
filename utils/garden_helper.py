# ============================================================
# همراه آرامش — توابع کمکی باغ
# ============================================================

from database import db
from database.models import Garden, User
from datetime import datetime
from utils.logger import logger
FLOWERS = {
    'diagnosis':    '🌸',
    'note':         '🌷',
    'breathing':    '🌿',
    'meditation':   '🪷',
    'daily_status': '🌻',
}


def give_seed(user_id, activity_type):
    """
    دادن دانه به کاربر

    Args:
        user_id: آی‌دی کاربر
        activity_type: نوع فعالیت (diagnosis, note, breathing, meditation, daily_status)

    Returns:
        Garden یا None (اگه خطا یا کاربر نامعتبر)
    """
    # ===== چک ورودی =====
    if not user_id or activity_type not in FLOWERS:
        return None

    # ===== چک وجود کاربر =====
    user = db.session.get(User, user_id)
    if not user:
        return None

    today = datetime.now().isoformat().split('T')[0]

    # ===== چک: قبلاً گرفته؟ =====
    existing = Garden.query.filter_by(
        user_id=user_id,
        activity_type=activity_type,
        date=today
    ).first()

    if existing:
        return existing

    # ===== دادن دانه =====
    try:
        seed = Garden(
            user_id=user_id,
            activity_type=activity_type,
            flower_type=FLOWERS[activity_type],
            date=today,
            is_planted=False
        )
        db.session.add(seed)
        db.session.commit()
        return seed
    except Exception as e:
        db.session.rollback()
        logger.warning(f"⚠️ خطا در دادن دانه: {e}")
        return None
