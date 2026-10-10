from flask import Blueprint, request, jsonify, session
from database import db
from database.models.user import User
from database.models.diagnosis import Diagnosis
from database.models.daily_note import DailyNote
from database.models.breathing import BreathingExercise
from database.models.meditation import Meditation
from datetime import datetime
import bcrypt
import os
import uuid
from werkzeug.utils import secure_filename
from config import get_config

profile_bp = Blueprint('profile', __name__)

AVATAR_FOLDER = get_config().AVATAR_FOLDER
ALLOWED_AVATAR_EXTENSIONS = get_config().ALLOWED_AVATAR_EXTENSIONS
MAX_AVATAR_SIZE = get_config().MAX_AVATAR_SIZE


# ============================================================
# توابع کمکی
# ============================================================

def allowed_avatar(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_AVATAR_EXTENSIONS


# ============================================================
# اطلاعات پروفایل
# ============================================================

@profile_bp.route('/api/profile', methods=['GET'])
def get_profile():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'لاگین نیستید'}), 401

    user = db.session.get(User,user_id)
    if not user:
        return jsonify({'error': 'کاربر یافت نشد'}), 404

    return jsonify(user.to_dict())


@profile_bp.route('/api/profile/stats', methods=['GET'])
def get_profile_stats():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'لاگین نیستید'}), 401

    total_diagnoses = Diagnosis.query.filter_by(user_id=user_id).count()
    total_notes = DailyNote.query.filter_by(user_id=user_id).count()
    total_breaths = BreathingExercise.query.filter_by(user_id=user_id).count()
    total_meditations = Meditation.query.filter_by(user_id=user_id).count()

    # ===== استریک =====
    diagnoses = Diagnosis.query.filter_by(user_id=user_id)\
        .order_by(Diagnosis.created_at.desc()).all()

    dates = sorted(set([d.date for d in diagnoses]), reverse=True)
    streak = 0
    if dates:
        today = datetime.now().isoformat().split('T')[0]
        if dates[0] == today:
            streak = 1
            for i in range(len(dates) - 1):
                prev = datetime.strptime(dates[i], '%Y-%m-%d')
                curr = datetime.strptime(dates[i + 1], '%Y-%m-%d')
                if (prev - curr).days == 1:
                    streak += 1
                else:
                    break

    return jsonify({
        'total_diagnoses': total_diagnoses,
        'total_notes': total_notes,
        'total_breaths': total_breaths,
        'total_meditations': total_meditations,
        'streak': streak
    })


# ============================================================
# ویرایش پروفایل
# ============================================================

@profile_bp.route('/api/profile/update', methods=['PUT'])
def update_profile():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'لاگین نیستید'}), 401

    user =db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'کاربر یافت نشد'}), 404

    data = request.json or {}
    display_name = (data.get('display_name') or '').strip()
    email = (data.get('email') or '').strip()

    # ===== اعتبارسنجی نام نمایشی =====
    if display_name:
        if len(display_name) < 2 or len(display_name) > 50:
            return jsonify({'error': 'نام نمایشی باید بین ۲ تا ۵۰ کاراکتر باشه'}), 400
        user.display_name = display_name

    # ===== اعتبارسنجی ایمیل =====
    if email:
        import re
        if not re.match(r'^[^\s@]+@[^\s@]+\.[a-zA-Z]{2,}$', email):
            return jsonify({'error': 'ایمیل معتبر وارد کنید'}), 400

        # ===== چک تکراری =====
        existing = User.query.filter(
            User.email == email,
            User.id != user_id
        ).first()
        if existing:
            return jsonify({'error': 'این ایمیل قبلاً استفاده شده'}), 400

        user.email = email
    db.session.commit()

    return jsonify({
        'success': True,
        'user': user.to_dict()
    })


# ============================================================
# تغییر رمز عبور
# ============================================================

@profile_bp.route('/api/profile/change-password', methods=['POST'])
def change_password():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'لاگین نیستید'}), 401

    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'کاربر یافت نشد'}), 404

    data = request.json or {}
    current_password = data.get('current_password') or ''
    new_password = data.get('new_password') or ''

    # ===== چک رمز فعلی با bcrypt =====
    try:
        is_valid = bcrypt.checkpw(
            current_password.encode('utf-8'),
            user.password_hash.encode('utf-8')
        )
    except Exception:
        is_valid = False

    if not is_valid:
        return jsonify({'error': 'رمز عبور فعلی اشتباه است'}), 400

    # ===== اعتبارسنجی رمز جدید =====
    import re
    if len(new_password) < 8:
        return jsonify({'error': 'رمز عبور جدید باید حداقل ۸ کاراکتر باشه'}), 400
    if not re.search(r'[A-Z]', new_password):
        return jsonify({'error': 'رمز عبور باید حداقل یه حرف بزرگ داشته باشه'}), 400
    if not re.search(r'[a-z]', new_password):
        return jsonify({'error': 'رمز عبور باید حداقل یه حرف کوچیک داشته باشه'}), 400
    if not re.search(r'[0-9]', new_password):
        return jsonify({'error': 'رمز عبور باید حداقل یه عدد داشته باشه'}), 400

    # ===== ذخیره با bcrypt =====
    user.password_hash = bcrypt.hashpw(
        new_password.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')

    db.session.commit()

    return jsonify({'success': True, 'message': 'رمز عبور تغییر کرد'})
# ============================================================
# آپلود آواتار
# ============================================================

@profile_bp.route('/api/profile/avatar', methods=['POST'])
def upload_avatar():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'لاگین نیستید'}), 401

    if 'avatar' not in request.files:
        return jsonify({'error': 'فایلی ارسال نشده'}), 400

    file = request.files['avatar']
    if not file.filename:
        return jsonify({'error': 'نام فایل خالی است'}), 400

    if not allowed_avatar(file.filename):
        return jsonify({'error': 'فرمت فایل مجاز نیست'}), 400

    # ===== چک حجم =====
    file.seek(0, 2)  # برو به آخر
    size = file.tell()
    file.seek(0)  # برگرد به اول

    if size > MAX_AVATAR_SIZE:
        return jsonify({'error': 'حجم فایل باید کمتر از ۲ مگابایت باشه'}), 400

    # ===== ذخیره =====
    os.makedirs(AVATAR_FOLDER, exist_ok=True)
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"avatar_{user_id}_{uuid.uuid4().hex[:8]}.{ext}"
    filepath = os.path.join(AVATAR_FOLDER, filename)
    file.save(filepath)

    # ===== آپدیت کاربر =====
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'کاربر یافت نشد'}), 404

    user.avatar_url = f"/static/uploads/avatars/{filename}"
    db.session.commit()

    return jsonify({
        'success': True,
        'avatar_url': user.avatar_url
    })


# ============================================================
# حذف حساب
# ============================================================

@profile_bp.route('/api/profile/delete', methods=['DELETE'])
def delete_account():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'لاگین نیستید'}), 401
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'کاربر یافت نشد'}), 404
    # ===== پاک کردن همه‌ی داده‌ها =====
    Diagnosis.query.filter_by(user_id=user_id).delete()
    DailyNote.query.filter_by(user_id=user_id).delete()
    BreathingExercise.query.filter_by(user_id=user_id).delete()
    Meditation.query.filter_by(user_id=user_id).delete()

    # ===== پاک کردن خود کاربر =====
    db.session.delete(user)
    db.session.commit()

    # ===== پاک کردن session =====
    session.clear()

    return jsonify({'success': True, 'message': 'حساب پاک شد'})