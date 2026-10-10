from flask import Blueprint, jsonify, session
from database import db
from database.models import User, Subscription
from utils.features import get_user_limits, is_premium
from datetime import datetime

subscription_bp = Blueprint('subscription', __name__)


# ============================================================
# GET /api/subscription/status
# ============================================================

@subscription_bp.route('/api/subscription/status', methods=['GET'])
def get_status():
    """وضعیت اشتراک کاربر"""
    user_id = session.get('user_id')

    # ===== مهمان =====
    if not user_id:
        return jsonify({
            'is_logged_in': False,
            'is_premium': False,
            'plan': 'guest',
            'plan_name': 'مهمان',
            'plan_icon': '👤',
            'limits': {
                'diagnosis_per_day': 1,
                'chat_per_day': 0,
                'notes_per_day': 0,
                'history_days': 0,
            }
        })

    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'کاربر یافت نشد'}), 404

    limits = get_user_limits(user)

    # ===== اطلاعات اشتراک =====
    subscription = Subscription.query.filter_by(
        user_id=user_id,
        status='active'
    ).order_by(Subscription.id.desc()).first()

    subscription_data = None
    if subscription and subscription.is_active():
        subscription_data = {
            'plan': subscription.plan,
            'started_at': subscription.started_at.isoformat() if subscription.started_at else None,
            'expires_at': subscription.expires_at.isoformat() if subscription.expires_at else None,
        }

    return jsonify({
        'is_logged_in': True,
        'is_premium': is_premium(user),
        'plan': limits.get('plan_name', 'رایگان'),
        'plan_name': limits.get('plan_name', 'رایگان'),
        'plan_icon': limits.get('plan_icon', '🆓'),
        'limits': {
            'diagnosis_per_day': limits.get('diagnosis_per_day'),
            'chat_per_day': limits.get('chat_per_day'),
            'notes_per_day': limits.get('notes_per_day'),
            'history_days': limits.get('history_days'),
        },
        'features': {
            'rag_enabled': limits.get('rag_enabled'),
            'llm_summary': limits.get('llm_summary'),
            'pdf_export': limits.get('pdf_export'),
            'premium_themes': limits.get('premium_themes'),
            'cloud_backup': limits.get('cloud_backup'),
        },
        'subscription': subscription_data,
    })
# ============================================================
# GET /api/subscription/usage
# ============================================================

@subscription_bp.route('/api/subscription/usage', methods=['GET'])
def get_usage():
    """استفاده‌ی امروز کاربر"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'لاگین نیستید'}), 401

    from database.models import Diagnosis, DailyNote
    from datetime import datetime

    today = datetime.now().isoformat().split('T')[0]

    # ===== تشخیص =====
    diagnosis_today = Diagnosis.query.filter_by(
        user_id=user_id, date=today
    ).count()

    # ===== یاداشت =====
    notes_today = DailyNote.query.filter_by(
        user_id=user_id, date=today
    ).count()

    # ===== چت (از session) =====
    chat_key = f'chat_count_{today}'
    chat_today = session.get(chat_key, 0)

    return jsonify({
        'date': today,
        'diagnosis_today': diagnosis_today,
        'notes_today': notes_today,
        'chat_today': chat_today,
    })