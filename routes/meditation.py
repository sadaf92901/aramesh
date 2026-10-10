from utils.garden_helper import give_seed
from flask import Blueprint, request, jsonify, session
from database import db
from database.models.meditation import Meditation
from datetime import datetime, timedelta

meditation_bp = Blueprint('meditation', __name__)

@meditation_bp.route('/api/meditation/stats', methods=['GET'])
def get_stats():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'لطفاً وارد شوید'}), 401

    today = datetime.now().isoformat().split('T')[0]
    week_ago = (datetime.now() - timedelta(days=7)).isoformat().split('T')[0]

    # ===== تمرین‌های امروز =====
    today_all = Meditation.query.filter_by(user_id=user_id, date=today).all()
    today_seconds = sum(m.duration for m in today_all)
    today_completed = len([m for m in today_all if m.completed])

    # ===== تمرین‌های هفته =====
    week_all = Meditation.query.filter(
        Meditation.user_id == user_id,
        Meditation.date >= week_ago
    ).all()
    week_seconds = sum(m.duration for m in week_all)
    week_completed = len([m for m in week_all if m.completed])

    return jsonify({
        'today_minutes': round(today_seconds / 60, 1),
        'week_minutes': round(week_seconds / 60, 1),
        'today_count': len(today_all),
        'week_count': len(week_all),
        'today_completed': today_completed,
        'week_completed': week_completed
    })

@meditation_bp.route('/api/meditation/save', methods=['POST'])
def save_meditation():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'لطفاً وارد شوید'}), 401

    data = request.json
    med_type = data.get('type')
    duration = data.get('duration')
    completed = data.get('completed', True)

    if not med_type or not duration:
        return jsonify({'error': 'داده‌ها ناقص است'}), 400

    today = datetime.now().isoformat().split('T')[0]

    meditation = Meditation(
        user_id=user_id,
        date=today,
        type=med_type,
        duration=duration,
        completed=completed
    )
    db.session.add(meditation)
    db.session.commit()
    give_seed(user_id,'meditation')
    return jsonify({'success': True, 'id': meditation.id})
@meditation_bp.route('/api/meditation/history', methods=['GET'])
def get_history():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'لطفاً وارد شوید'}), 401

    meditations = Meditation.query.filter_by(
        user_id=user_id, completed=True
    ).order_by(Meditation.id.desc()).limit(20).all()

    return jsonify([m.to_dict() for m in meditations])