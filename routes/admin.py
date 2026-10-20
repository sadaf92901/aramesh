# ============================================================
# routes/admin.py — پنل مدیریت
# ============================================================

from flask import Blueprint, render_template, jsonify, request, session, redirect
from database import db
from database.models import (
    User, Diagnosis, DailyNote, DailyStatus,
    BreathingExercise, Meditation, Garden, WeeklyPlan, Subscription
)
from utils.admin_helpers import admin_required, get_admin_stats
from utils.logger import logger
from sqlalchemy import desc
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# ============================================================
# داشبورد
# ============================================================

@admin_bp.route('/')
@admin_required
def dashboard():
    stats = get_admin_stats()
    recent_users = User.query.order_by(desc(User.created_at)).limit(10).all()
    recent_diagnoses = Diagnosis.query.order_by(desc(Diagnosis.created_at)).limit(10).all()

    return render_template(
        'admin/dashboard.html',
        stats=stats,
        recent_users=recent_users,
        recent_diagnoses=recent_diagnoses
    )


# ============================================================
# مدیریت کاربران
# ============================================================

@admin_bp.route('/users')
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    per_page = 20

    query = User.query
    if search:
        query = query.filter(
            (User.username.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%')) |
            (User.display_name.ilike(f'%{search}%'))
        )

    pagination = query.order_by(desc(User.created_at)).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template(
        'admin/users.html',
        users=pagination.items,
        pagination=pagination,
        search=search
    )


@admin_bp.route('/users/<int:user_id>')
@admin_required
def user_detail(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return render_template('admin/404.html'), 404

    stats = {
        'diagnoses': Diagnosis.query.filter_by(user_id=user_id).count(),
        'notes': DailyNote.query.filter_by(user_id=user_id).count(),
        'breathings': BreathingExercise.query.filter_by(user_id=user_id).count(),
        'meditations': Meditation.query.filter_by(user_id=user_id).count(),
        'flowers': Garden.query.filter_by(user_id=user_id, is_planted=True).count(),
    }

    diagnoses = Diagnosis.query.filter_by(user_id=user_id)\
        .order_by(desc(Diagnosis.created_at)).limit(10).all()

    notes = DailyNote.query.filter_by(user_id=user_id)\
        .order_by(desc(DailyNote.created_at)).limit(10).all()

    return render_template(
        'admin/user_detail.html',
        user=user,
        stats=stats,
        diagnoses=diagnoses,
        notes=notes
    )


# ============================================================
# مدیریت تشخیص‌ها
# ============================================================

@admin_bp.route('/diagnoses')
@admin_required
def diagnoses():
    page = request.args.get('page', 1, type=int)
    per_page = 20

    pagination = Diagnosis.query.order_by(desc(Diagnosis.created_at))\
        .paginate(page=page, per_page=per_page, error_out=False)

    return render_template(
        'admin/diagnoses.html',
        diagnoses=pagination.items,
        pagination=pagination
    )


# ============================================================
# مدیریت یاداشت‌ها
# ============================================================

@admin_bp.route('/notes')
@admin_required
def notes():
    page = request.args.get('page', 1, type=int)
    per_page = 20

    pagination = DailyNote.query.order_by(desc(DailyNote.created_at))\
        .paginate(page=page, per_page=per_page, error_out=False)

    return render_template(
        'admin/notes.html',
        notes=pagination.items,
        pagination=pagination
    )


# ============================================================
# API: آمار
# ============================================================

@admin_bp.route('/api/stats')
@admin_required
def api_stats():
    return jsonify(get_admin_stats())


# ============================================================
# API: تغییر وضعیت ادمین
# ============================================================

@admin_bp.route('/api/users/<int:user_id>/toggle-admin', methods=['POST'])
@admin_required
def toggle_admin(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'کاربر یافت نشد'}), 404

    if user.id == session.get('user_id'):
        return jsonify({'error': 'نمی‌تونی خودت رو از ادمینی دربیاری'}), 400

    user.is_admin = not user.is_admin
    db.session.commit()

    logger.info(f"👤 ادمین {session.get('username')} وضعیت ادمینی {user.username} را به {user.is_admin} تغییر داد")

    return jsonify({'success': True, 'is_admin': user.is_admin})


# ============================================================
# API: حذف کاربر
# ============================================================

@admin_bp.route('/api/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'کاربر یافت نشد'}), 404

    if user.id == session.get('user_id'):
        return jsonify({'error': 'نمی‌تونی خودت رو حذف کنی'}), 400

    Diagnosis.query.filter_by(user_id=user_id).delete()
    DailyNote.query.filter_by(user_id=user_id).delete()
    DailyStatus.query.filter_by(user_id=user_id).delete()
    BreathingExercise.query.filter_by(user_id=user_id).delete()
    Meditation.query.filter_by(user_id=user_id).delete()
    Garden.query.filter_by(user_id=user_id).delete()
    WeeklyPlan.query.filter_by(user_id=user_id).delete()
    Subscription.query.filter_by(user_id=user_id).delete()

    db.session.delete(user)
    db.session.commit()

    logger.info(f"🗑️ ادمین {session.get('username')} کاربر {user.username} را حذف کرد")

    return jsonify({'success': True})
