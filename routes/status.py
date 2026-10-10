from utils.garden_helper import give_seed
from utils.logger import logger
from utils.helpers import sanitize_input
from flask import Blueprint, request, jsonify, session
from database import db
from database.models import DailyStatus
from datetime import datetime

status_bp = Blueprint('status', __name__)


# ============================================================
# مقادیر مجاز (whitelist)
# ============================================================

ALLOWED_MOODS = {'good', 'neutral', 'bad'}
ALLOWED_ENERGY = {'high', 'medium', 'low'}
ALLOWED_SLEEP = {'great', 'good', 'bad'}


# ============================================================
# /api/daily-status
# ============================================================

@status_bp.route('/api/daily-status', methods=['GET', 'POST'])
def daily_status():
    user_id = session.get('user_id')

    # ============================================================
    # GET
    # ============================================================
    if request.method == 'GET':
        if not user_id:
            return jsonify({})

        statuses = DailyStatus.query.filter_by(user_id=user_id).all()
        result = {}
        for s in statuses:
            result[s.date] = {
                'mood': s.mood,
                'energy': s.energy,
                'sleep': s.sleep,
                'user_id': s.user_id
            }
        return jsonify(result)

    # ============================================================
    # POST
    # ============================================================
    elif request.method == 'POST':
        if not user_id:
            return jsonify({'error': 'لطفاً وارد شوید'}), 401

        data = request.json
        if not data:
            return jsonify({'error': 'داده‌ای ارسال نشده'}), 400

        # ===== Sanitize + اعتبارسنجی =====
        mood, err = validate_field(data.get('mood'), ALLOWED_MOODS, 'mood')
        if err:
            return jsonify({'error': err}), 400

        energy, err = validate_field(data.get('energy'), ALLOWED_ENERGY, 'energy')
        if err:
            return jsonify({'error': err}), 400

        sleep, err = validate_field(data.get('sleep'), ALLOWED_SLEEP, 'sleep')
        if err:
            return jsonify({'error': err}), 400

        today = datetime.now().isoformat().split('T')[0]

        try:
            existing = DailyStatus.query.filter_by(
                user_id=user_id, date=today
            ).first()

            if existing:
                existing.mood = mood
                existing.energy = energy
                existing.sleep = sleep
            else:
                new_status = DailyStatus(
                    user_id=user_id,
                    date=today,
                    mood=mood,
                    energy=energy,
                    sleep=sleep
                )
                db.session.add(new_status)

            db.session.commit()
            give_seed(user_id, 'daily_status')

            return jsonify({'success': True, 'date': today})

        except Exception as e:
            logger.error(f"❌ خطا در ذخیره دیتابیس: {e}")
            db.session.rollback()
            return jsonify({'error': str(e)}), 500


# ============================================================
# تابع کمکی: اعتبارسنجی فیلد
# ============================================================

def validate_field(raw_value, allowed_set, field_name):
    """
    اعتبارسنجی یه فیلد

    Returns:
        (value, error_message) — یکی None می‌شه
    """
    # ===== اگه اصلاً فرستاده نشده =====
    if raw_value is None:
        return None, None

    # ===== اگه رشته نیست، تبدیل کن =====
    if not isinstance(raw_value, str):
        raw_value = str(raw_value)

    # ===== Sanitize =====
    sanitized = sanitize_input(raw_value)

    # ===== اگه raw چیزی داشت ولی sanitize خالیش کرد → XSS =====
    if raw_value.strip() and not sanitized:
        return None, f'مقدار {field_name} نامعتبر است'
    # ===== اگه sanitize چیزی رو تغییر داد (XSS تلاش) → خطا =====
    if raw_value.strip() != sanitized:
        return None, f'مقدار {field_name} نامعتبر است'

    # ===== Whitelist =====
    if sanitized and sanitized not in allowed_set:
        return None, f'مقدار {field_name} نامعتبر است'

    # ===== OK =====
    return sanitized or None, None