from flask import Blueprint, request, jsonify, session
from extensions import limiter
from database import db
from database.models.weekly_plan import WeeklyPlan
from database.models.diagnosis import Diagnosis
from datetime import datetime, timedelta
import json

weekly_plan_bp = Blueprint('weekly_plan', __name__)


@weekly_plan_bp.route('/api/weekly-plan', methods=['GET'])
def get_weekly_plan():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'لطفاً وارد شوید'}), 401

    plan = WeeklyPlan.query.filter_by(user_id=user_id).order_by(WeeklyPlan.id.desc()).first()

    if not plan:
        return jsonify({'plan': None})

    return jsonify({'plan': plan.to_dict()})


@weekly_plan_bp.route('/api/weekly-plan/generate', methods=['POST'])
@limiter.limit("3 per day")
def generate_weekly_plan():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'لطفاً وارد شوید'}), 401

    last_diagnosis = Diagnosis.query.filter_by(user_id=user_id).order_by(Diagnosis.id.desc()).first()
    if not last_diagnosis:
        return jsonify({'error': 'اول تشخیص بده'}), 400

    level = last_diagnosis.prediction

    today = datetime.now()
    week_start = today.isoformat().split('T')[0]
    week_end = (today + timedelta(days=6)).isoformat().split('T')[0]

    plan_data = build_plan_by_level(level)

    existing = WeeklyPlan.query.filter_by(user_id=user_id, week_start=week_start).first()
    if existing:
        existing.plan_data = json.dumps(plan_data)
        existing.level = level
        db.session.commit()
        return jsonify({'success': True, 'plan': existing.to_dict()})

    new_plan = WeeklyPlan(
        user_id=user_id,
        week_start=week_start,
        week_end=week_end,
        level=level,
        plan_data=json.dumps(plan_data)
    )
    db.session.add(new_plan)
    db.session.commit()

    return jsonify({'success': True, 'plan': new_plan.to_dict()})


@weekly_plan_bp.route('/api/weekly-plan/toggle', methods=['POST'])
def toggle_activity():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'لطفاً وارد شوید'}), 401

    data = request.json or {}
    day_index = data.get('day')
    activity_index = data.get('activity')

    # ===== اعتبارسنجی =====
    if not isinstance(day_index, int) or day_index < 0 or day_index > 6:
        return jsonify({'error': 'روز نامعتبر'}), 400
    if not isinstance(activity_index, int) or activity_index < 0:
        return jsonify({'error': 'فعالیت نامعتبر'}), 400

    plan = WeeklyPlan.query.filter_by(user_id=user_id).order_by(WeeklyPlan.id.desc()).first()
    if not plan:
        return jsonify({'error': 'برنامه‌ای یافت نشد'}), 404

    plan_data = json.loads(plan.plan_data)

    # ===== چک وجود روز و فعالیت =====
    if day_index >= len(plan_data.get('days', [])):
        return jsonify({'error': 'روز نامعتبر'}), 400

    activities = plan_data['days'][day_index].get('activities', [])
    if activity_index >= len(activities):
        return jsonify({'error': 'فعالیت نامعتبر'}), 400

    plan_data['days'][day_index]['activities'][activity_index]['done'] = \
        not plan_data['days'][day_index]['activities'][activity_index]['done']

    plan.plan_data = json.dumps(plan_data)
    db.session.commit()

    return jsonify({'success': True, 'plan': plan.to_dict()})


def build_plan_by_level(level):
    if level == 0:
        activities = [
            {'icon': '🧘', 'title': 'تمرین تنفس', 'duration': '۵ دقیقه', 'done': False},
            {'icon': '📝', 'title': 'نوشتن ۳ چیز خوب', 'duration': '۳ خط', 'done': False},
            {'icon': '🚶', 'title': 'پیاده‌روی', 'duration': '۱۰ دقیقه', 'done': False},
        ]
    elif level == 1:
        activities = [
            {'icon': '🧘', 'title': 'تمرین تنفس عمیق', 'duration': '۱۰ دقیقه', 'done': False},
            {'icon': '📝', 'title': 'نوشتن احساسات', 'duration': '۵ خط', 'done': False},
            {'icon': '🚶', 'title': 'پیاده‌روی در طبیعت', 'duration': '۲۰ دقیقه', 'done': False},
            {'icon': '☎️', 'title': 'صحبت با دوست', 'duration': '۱۰ دقیقه', 'done': False},
        ]
    elif level == 2:
        activities = [
            {'icon': '🧘', 'title': 'تمرین تنفس + مدیتیشن', 'duration': '۱۵ دقیقه', 'done': False},
            {'icon': '📝', 'title': 'نوشتن افکار منفی و جایگزینی', 'duration': '۱۰ خط', 'done': False},
            {'icon': '🚶', 'title': 'ورزش سبک', 'duration': '۳۰ دقیقه', 'done': False},
            {'icon': '☎️', 'title': 'جلسه مشاوره', 'duration': '۳۰ دقیقه', 'done': False},
        ]
    else:
        activities = [
            {'icon': '🧘', 'title': 'تمرین تنفس', 'duration': '۱۵ دقیقه', 'done': False},
            {'icon': '📝', 'title': 'نوشتن آزاد احساسات', 'duration': 'بدون محدودیت', 'done': False},
            {'icon': '🚶', 'title': 'ورزش سبک', 'duration': '۱۰ دقیقه', 'done': False},
            {'icon': '☎️', 'title': 'تماس با روانشناس', 'duration': '۳۰ دقیقه', 'done': False},
        ]

    days = []
    day_names = ['شنبه', 'یکشنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنجشنبه', 'جمعه']
    for i, day_name in enumerate(day_names):
        days.append({
            'day': day_name,
            'date_index': i,
            'activities': [dict(a) for a in activities]
        })

    return {'days': days, 'level': level}