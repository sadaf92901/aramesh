# ============================================================
# utils/admin_helpers.py — توابع کمکی پنل ادمین
# ============================================================

from functools import wraps
from flask import session, jsonify, redirect, request
from database import db
from database.models import User


def is_admin():
    """آیا کاربر فعلی ادمینه؟"""
    user_id = session.get('user_id')
    if not user_id:
        return False
    user = db.session.get(User, user_id)
    return bool(user and user.is_admin)


def admin_required(f):
    """
    دکوراتور: فقط ادمین‌ها دسترسی دارن.
    - برای API → 403 JSON
    - برای صفحه → redirect به /
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_admin():
            if request.path.startswith('/admin/api/'):
                return jsonify({'error': 'دسترسی غیرمجاز'}), 403
            return redirect('/')
        return f(*args, **kwargs)
    return decorated_function


def get_admin_stats():
    """آمار کلی برای داشبورد"""
    from database.models import (
        Diagnosis, DailyNote, BreathingExercise, Meditation, Garden
    )
    from datetime import datetime, timedelta

    today = datetime.now().isoformat().split('T')[0]
    week_ago = (datetime.now() - timedelta(days=7)).isoformat().split('T')[0]
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    return {
        'total_users': User.query.count(),
        'total_diagnoses': Diagnosis.query.count(),
        'total_notes': DailyNote.query.count(),
        'total_breathings': BreathingExercise.query.count(),
        'total_meditations': Meditation.query.count(),
        'total_flowers': Garden.query.filter_by(is_planted=True).count(),

        'users_today': User.query.filter(User.created_at >= today_start).count(),
        'diagnoses_today': Diagnosis.query.filter_by(date=today).count(),
        'notes_today': DailyNote.query.filter_by(date=today).count(),

        'diagnoses_week': Diagnosis.query.filter(Diagnosis.date >= week_ago).count(),
        'notes_week': DailyNote.query.filter(DailyNote.date >= week_ago).count(),
    }