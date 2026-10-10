from utils.logger import logger
from flask import Blueprint, request, jsonify, session
from database import db
from database.models.diagnosis import Diagnosis
from database.models.daily_note import DailyNote
from database.models.meditation import Meditation
from database.models.breathing import BreathingExercise
from database.models.weekly_plan import WeeklyPlan
from datetime import datetime, timedelta
import json

history_bp = Blueprint('history', __name__)


@history_bp.route('/api/history/timeline', methods=['GET'])
def get_timeline():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'لاگین نیستید'}), 401

    # ===== فیلتر =====
    types_param = request.args.get('types', '')
    types = types_param.split(',') if types_param else [
        'diagnosis', 'note', 'meditation', 'breathing', 'weekly_plan'
    ]

    days = int(request.args.get('days', 30))
    from_date = (datetime.now() - timedelta(days=days)).isoformat().split('T')[0]

    items = []

    # ===== تشخیص‌ها =====
    if 'diagnosis' in types:
        diagnoses = Diagnosis.query.filter(
            Diagnosis.user_id == user_id,
            Diagnosis.date >= from_date
        ).all()
        for d in diagnoses:
            items.append({
                'type': 'diagnosis',
                'date': d.date,
                'timestamp': d.created_at.isoformat() if d.created_at else d.date,
                'data': {
                    'id': d.id,
                    'prediction': d.prediction,
                    'score': d.final_score,
                    'mcq_score': d.mcq_score,
                    'llm_score': d.llm_score,
                    'treatment': d.treatment
                }
            })

    # ===== یاداشت‌ها =====
    if 'note' in types:
        notes = DailyNote.query.filter(
            DailyNote.user_id == user_id,
            DailyNote.date >= from_date
        ).all()
        for n in notes:
            items.append({
                'type': 'note',
                'date': n.date,
                'timestamp': n.created_at.isoformat() if n.created_at else n.date,
                'data': {
                    'id': n.id,
                    'title': n.title or '',
                    'content': n.content,
                    'mood': n.mood or '',
                    'tags': n.tags.split(',') if n.tags else []
                }
            })

    # ===== مدیتیشن‌ها =====
    if 'meditation' in types:
        meditations = Meditation.query.filter(
            Meditation.user_id == user_id,
            Meditation.date >= from_date
        ).all()
        for m in meditations:
            items.append({
                'type': 'meditation',
                'date': m.date,
                'timestamp': m.created_at.isoformat() if m.created_at else m.date,
                'data': {
                    'id': m.id,
                    'type': m.type,
                    'duration': m.duration,
                    'completed': m.completed
                }
            })

    # ===== تمرین تنفس =====
    if 'breathing' in types:
        breaths = BreathingExercise.query.filter(
            BreathingExercise.user_id == user_id,
            BreathingExercise.date >= from_date
        ).all()
        for b in breaths:
            items.append({
                'type': 'breathing',
                'date': b.date,
                'timestamp': b.timestamp.isoformat() if b.timestamp else b.date,
                'data': {
                    'id': b.id,
                    'duration': b.duration,
                    'count': b.count
                }
            })

    # ===== برنامه هفتگی =====
    if 'weekly_plan' in types:
        plans = WeeklyPlan.query.filter(
            WeeklyPlan.user_id == user_id,
            WeeklyPlan.week_start >= from_date
        ).all()
        for p in plans:
            items.append({
                'type': 'weekly_plan',
                'date': p.week_start,
                'timestamp': p.created_at.isoformat() if p.created_at else p.week_start,
                'data': {
                    'id': p.id,
                    'week_start': p.week_start,
                    'week_end': p.week_end,
                    'level': p.level
                }
            })

    # ===== مرتب‌سازی (جدید به قدیم) =====
    items.sort(key=lambda x: x['timestamp'], reverse=True)

    return jsonify({'items': items})


@history_bp.route('/api/history/stats', methods=['GET'])
def get_stats():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'لاگین نیستید'}), 401

    # ===== کل تشخیص‌ها =====
    total_diagnoses = Diagnosis.query.filter_by(user_id=user_id).count()

    # ===== میانگین امتیاز =====
    diagnoses = Diagnosis.query.filter_by(user_id=user_id).all()
    avg_score = sum(d.final_score for d in diagnoses) / len(diagnoses) if diagnoses else 0

    # ===== کل یاداشت‌ها =====
    total_notes = DailyNote.query.filter_by(user_id=user_id).count()

    # ===== کل تمرین‌ها =====
    total_breaths = BreathingExercise.query.filter_by(user_id=user_id).count()

    return jsonify({
        'total_diagnoses': total_diagnoses,
        'avg_score': round(avg_score, 1),
        'total_notes': total_notes,
        'total_breaths': total_breaths
    })
@history_bp.route('/api/history/weekly-summary', methods=['GET'])
def get_weekly_summary():
    """گزارش هفتگی — بر اساس فعالیت‌های ۷ روز گذشته"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'لاگین نیستید'}), 401

    week_ago = (datetime.now() - timedelta(days=7)).isoformat().split('T')[0]
    today = datetime.now().isoformat().split('T')[0]

    # ===== جمع‌آوری داده‌ها =====
    diagnoses = Diagnosis.query.filter(
        Diagnosis.user_id == user_id,
        Diagnosis.date >= week_ago
    ).all()

    notes = DailyNote.query.filter(
        DailyNote.user_id == user_id,
        DailyNote.date >= week_ago
    ).all()

    breathings = BreathingExercise.query.filter(
        BreathingExercise.user_id == user_id,
        BreathingExercise.date >= week_ago
    ).all()

    meditations = Meditation.query.filter(
        Meditation.user_id == user_id,
        Meditation.date >= week_ago
    ).all()

    # ===== محاسبه‌ی آمار =====
    total_diagnoses = len(diagnoses)
    total_notes = len(notes)
    total_breathings = len(breathings)
    total_meditations = len(meditations)
    total_activities = total_notes + total_breathings + total_meditations

    # ===== میانگین امتیاز تشخیص =====
    if diagnoses:
        avg_score = sum(d.final_score for d in diagnoses) / len(diagnoses)
        avg_score = round(avg_score, 1)
    else:
        avg_score = 0

    # ===== روند (بهتر/بدتر/ثابت) =====
    trend = 'نامشخص'
    if len(diagnoses) >= 2:
        sorted_diagnoses = sorted(diagnoses, key=lambda d: d.created_at)
        first_score = sorted_diagnoses[0].final_score
        last_score = sorted_diagnoses[-1].final_score
        diff = last_score - first_score

        if diff > 5:
            trend = 'improving'  # رو به بهبود
        elif diff < -5:
            trend = 'declining'  # رو به کاهش
        else:
            trend = 'stable'  # پایدار

    # ===== تلاش برای گرفتن گزارش از LLM =====
    llm_summary = None
    try:
        from utils.llm.service import get_llm_service
        llm_service = get_llm_service()

        if llm_service.is_available():
            summary_data = {
                'diagnoses': f'{total_diagnoses} تشخیص (میانگین {avg_score}%)',
                'notes': f'{total_notes} یاداشت',
                'breathings': f'{total_breathings} تمرین تنفس',
                'meditations': f'{total_meditations} مدیتیشن',
            }
            llm_summary = llm_service.weekly_summary(summary_data)
    except Exception as e:
        logger.warning(f"⚠️ خطا در LLM summary: {e}")

    # ===== پیام پیش‌فرض =====
    if not llm_summary:
        if total_activities == 0 and total_diagnoses == 0:
            llm_summary = (
                "این هفته فعالیتی ثبت نشده. "
                "بیا هفته‌ی بعد با یه تشخیص کوچیک یا یه تمرین تنفس شروع کنیم. 💚"
            )
        elif total_activities < 5:
            llm_summary = (
                f"این هفته {total_activities} فعالیت داشتی. "
                "شروع خوبیه! سعی کن هفته‌ی بعد چند تا بیشتر اضافه کنی. 🌱"
            )
        elif total_activities < 15:
            llm_summary = (
                f"این هفته {total_activities} فعالیت داشتی. "
                "خیلی خوبه! داری به خودت اهمیت می‌دی. 💚"
            )
        else:
            llm_summary = (
                f"این هفته {total_activities} فعالیت داشتی. "
                "فوق‌العاده‌ست! این مسیر رو ادامه بده. 🌟"
            )

    return jsonify({
        'week_start': week_ago,
        'week_end': today,
        'stats': {
            'total_diagnoses': total_diagnoses,
            'total_notes': total_notes,
            'total_breathings': total_breathings,
            'total_meditations': total_meditations,
            'total_activities': total_activities,
            'avg_score': avg_score,
            'trend': trend,
        },
        'summary': llm_summary,
        'llm_used': bool(llm_summary and llm_service and llm_service.is_available()) if 'llm_service' in dir() else False
    })
@history_bp.route('/api/history/compare', methods=['GET'])
def compare_diagnoses():
    """مقایسه‌ی آخرین تشخیص با تشخیص قبلی"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'لاگین نیستید'}), 401

    # ===== ۲ تا تشخیص آخر =====
    diagnoses = Diagnosis.query.filter_by(user_id=user_id)\
        .order_by(Diagnosis.created_at.desc())\
        .limit(2).all()

    if len(diagnoses) < 2:
        return jsonify({
            'has_comparison': False,
            'message': 'برای مقایسه، حداقل ۲ تشخیص لازمه'
        })

    latest = diagnoses[0]
    previous = diagnoses[1]

    # ===== محاسبه‌ی تغییر =====
    diff = latest.final_score - previous.final_score
    diff_percent = round(diff, 1)

    # ===== تعیین روند =====
    if diff > 5:
        trend = 'improving'
        trend_text = 'رو به بهبود'
        trend_icon = '📈'
    elif diff < -5:
        trend = 'declining'
        trend_text = 'رو به کاهش'
        trend_icon = '📉'
    else:
        trend = 'stable'
        trend_text = 'تقریباً پایدار'
        trend_icon = '➖'

    return jsonify({
        'has_comparison': True,
        'latest': {
            'date': latest.date,
            'score': latest.final_score,
            'prediction': latest.prediction,
            'mcq_score': latest.mcq_score,
            'llm_score': latest.llm_score
        },
        'previous': {
            'date': previous.date,
            'score': previous.final_score,
            'prediction': previous.prediction
        },
        'diff': diff_percent,
        'trend': trend,
        'trend_text': trend_text,
        'trend_icon': trend_icon
    })