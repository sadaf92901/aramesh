from flask import Blueprint, request, jsonify, session
from utils.helpers import utcnow
from database import db
from database.models import Garden
from datetime import datetime, timedelta

garden_bp = Blueprint('garden', __name__)


@garden_bp.route('/api/garden', methods=['GET'])
def get_garden():
    """دریافت باغ کاربر"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'لطفاً وارد شوید'}), 401

    all_items = Garden.query.filter_by(user_id=user_id).order_by(Garden.created_at).all()

    seeds = [item for item in all_items if not item.is_planted]
    flowers = [item for item in all_items if item.is_planted]

    # ===== استریک =====
    dates = sorted(set(item.date for item in flowers), reverse=True)
    streak = 0
    if dates:
        today = datetime.now().isoformat().split('T')[0]
        yesterday = (datetime.now() - timedelta(days=1)).isoformat().split('T')[0]

        if dates[0] == today or dates[0] == yesterday:
            streak = 1
            for i in range(len(dates) - 1):
                prev = datetime.strptime(dates[i], '%Y-%m-%d')
                curr = datetime.strptime(dates[i + 1], '%Y-%m-%d')
                if (prev - curr).days == 1:
                    streak += 1
                else:
                    break

    return jsonify({
        'seeds': [s.to_dict() for s in seeds],
        'flowers': [f.to_dict() for f in flowers],
        'stats': {
            'total_flowers': len(flowers),
            'total_seeds': len(seeds),
            'unique_days': len(set(f.date for f in flowers)),
            'streak': streak,
        }
    })

@garden_bp.route('/api/garden/plant', methods=['POST'])
def plant_seed():
    """کاشتن یه دانه"""
    import random

    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'لطفاً وارد شوید'}), 401

    data = request.json or {}
    seed_id = data.get('seed_id')

    if not seed_id:
        return jsonify({'error': 'شناسه دانه لازمه'}), 400

    seed = Garden.query.filter_by(
        id=seed_id,
        user_id=user_id,
        is_planted=False
    ).first()

    if not seed:
        return jsonify({'error': 'دانه پیدا نشد'}), 404

    try:
        seed.is_planted = True
        seed.planted_at = datetime.utcnow()

        # ===== 🆕 ذخیره‌ی موقعیت تصادفی =====
        seed.position_x = random.randint(8, 88)   # بین ۸٪ تا ۸۸٪
        seed.position_y = random.randint(45, 90)  # بین ۴۵٪ تا ۹۰٪

        db.session.commit()

        return jsonify({
            'success': True,
            'flower': seed.to_dict(),
            'message': '🌸 گل کاشته شد!'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500