from utils.garden_helper import give_seed
from flask import Blueprint, request, jsonify, session
from database import db
from database.models.breathing import BreathingExercise
from database.models.daily_status import DailyStatus
from datetime import datetime, timedelta

breathing_bp = Blueprint('breathing', __name__)


@breathing_bp.route('/api/breathing', methods=['GET', 'POST'])
def breathing():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'لاگین نیستید'}), 401

    if request.method == 'GET':
        today = datetime.now().isoformat().split('T')[0]
        week_ago = (datetime.now() - timedelta(days=7)).isoformat().split('T')[0]

        today_count = BreathingExercise.query.filter_by(
            user_id=user_id, date=today
        ).count()

        week_count = BreathingExercise.query.filter(
            BreathingExercise.user_id == user_id,
            BreathingExercise.date >= week_ago
        ).count()

        return jsonify({
            'today_count': today_count,
            'week_count': week_count
        })

    elif request.method == 'POST':
        data = request.json or {}
        duration = data.get('duration', 30)
        today = datetime.now().isoformat().split('T')[0]

        exercise = BreathingExercise(
            user_id=user_id,
            date=today,
            count=1,
            duration=duration
        )
        db.session.add(exercise)
        db.session.commit()
        give_seed(user_id, 'breathing')
        today_count = BreathingExercise.query.filter_by(
            user_id=user_id, date=today
        ).count()

        return jsonify({
            'success': True,
            'today_count': today_count,
            'id': exercise.id
        })


@breathing_bp.route('/api/weekly-progress', methods=['GET'])
def weekly_progress():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'لاگین نیستید'}), 401

    week_ago = (datetime.now() - timedelta(days=7)).isoformat().split('T')[0]

    breath_count = BreathingExercise.query.filter(
        BreathingExercise.user_id == user_id,
        BreathingExercise.date >= week_ago
    ).count()

    daily_count = DailyStatus.query.filter(
        DailyStatus.user_id == user_id,
        DailyStatus.date >= week_ago
    ).count()

    total = breath_count + daily_count
    progress_percent = min(100, (total / 7) * 100)

    return jsonify({
        'breath_count': breath_count,
        'daily_count': daily_count,
        'progress': progress_percent,
        'total': total
    })