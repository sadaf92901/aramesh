from utils.logger import logger
from utils.helpers import utcnow
from flask import Blueprint, request, jsonify, session
from database import db
from database.models import User
from datetime import datetime
import bcrypt
import re
from extensions import limiter

auth_bp = Blueprint('auth', __name__)


# ============================================================
# توابع کمکی
# ============================================================

def hash_password(password):
    """هش کردن رمز عبور"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def check_password(password, password_hash):
    """چک کردن رمز عبور"""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except Exception:
        return False


def validate_username(username):
    return bool(re.match(r'^[a-zA-Z][a-zA-Z0-9_]{2,19}$', username))


def validate_email(email):
    return bool(re.match(r'^[^\s@]+@[^\s@]+\.[a-zA-Z]{2,}$', email))


def validate_password(password):
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    return True


# ============================================================
# ثبت‌نام — محدودیت: ۳ بار در ساعت
# ============================================================

@auth_bp.route('/api/register', methods=['POST'])
@limiter.limit("3 per hour")
def register():
    try:
        data = request.json
        username = (data.get('username') or '').strip()
        display_name = (data.get('display_name') or '').strip()
        email = (data.get('email') or '').strip()
        password = data.get('password') or ''

        if not username or not email or not password:
            return jsonify({'error': 'تمام فیلدها را پر کنید'}), 400

        if not validate_username(username):
            return jsonify({'error': 'نام کاربری باید ۳ تا ۲۰ کاراکتر، با حرف انگلیسی شروع شه'}), 400

        if not validate_email(email):
            return jsonify({'error': 'ایمیل معتبر وارد کنید'}), 400

        if not validate_password(password):
            return jsonify({'error': 'رمز عبور باید حداقل ۸ کاراکتر، شامل حرف بزرگ، کوچک و عدد باشه'}), 400

        if not display_name:
            display_name = username

        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            return jsonify({'error': 'نام کاربری یا ایمیل قبلاً ثبت شده'}), 400

        password_hash = hash_password(password)

        new_user = User(
            username=username,
            display_name=display_name,
            email=email,
            password_hash=password_hash,
            created_at=utcnow()
        )

        db.session.add(new_user)
        db.session.commit()

        session['user_id'] = new_user.id
        session['username'] = new_user.username

        return jsonify({
            'success': True,
            'user_id': new_user.id,
            'username': new_user.username,
            'display_name': new_user.display_name
        })

    except Exception as e:
        logger.error(f"❌ خطا در ثبت‌نام: {e}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============================================================
# ورود — محدودیت: ۵ بار در دقیقه
# ============================================================

@auth_bp.route('/api/login', methods=['POST'])
@limiter.limit("20 per hour")  # ← محدودیت کلی: ۲۰ بار در ساعت
@limiter.limit("5 per minute")  # ← محدودیت لحظه‌ای: ۵ بار در دقیقه
def login():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'error': 'نام کاربری و رمز عبور را وارد کنید'}), 400

        user = User.query.filter_by(username=username).first()

        if not user:
            return jsonify({'error': 'کاربری با این نام کاربری وجود ندارد'}), 401

        if not check_password(password, user.password_hash):
            return jsonify({'error': 'رمز عبور اشتباه است'}), 401

        session['user_id'] = user.id
        session['username'] = user.username

        return jsonify({
            'success': True,
            'user_id': user.id,
            'username': user.username,
            'display_name': user.display_name or user.username,
            'email': user.email
        })

    except Exception as e:
        logger.error(f"❌ خطا در ورود: {e}")
        return jsonify({'error': 'خطای داخلی سرور'}), 500


# ============================================================
# کاربر فعلی — محدودیت: ۳۰ بار در دقیقه
# ============================================================

@auth_bp.route('/api/me', methods=['GET'])
@limiter.limit("30 per minute")
def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'لاگین نیستید'}), 401

    user = db.session.get(User,user_id)
    if not user:
        return jsonify({'error': 'کاربر یافت نشد'}), 404

    return jsonify({
        'id': user.id,
        'username': user.username,
        'display_name': user.display_name or user.username,
        'email': user.email
    })


# ============================================================
# خروج
# ============================================================

@auth_bp.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True, 'message': 'با موفقیت خارج شدید'})


# ============================================================
# مهمان — محدودیت: ۱۰ بار در ساعت
# ============================================================

@auth_bp.route('/api/guest-login', methods=['POST'])
@limiter.limit("10 per hour")
def guest_login():
    session['is_guest'] = True
    return jsonify({'success': True})


# ============================================================
# فراموشی رمز — محدودیت: ۳ بار در ساعت
# ============================================================

@auth_bp.route('/api/forgot-password', methods=['POST'])
@limiter.limit("3 per hour")
def forgot_password():
    try:
        data = request.json or {}
        email = (data.get('email') or '').strip()

        if not email:
            return jsonify({'error': 'ایمیل رو وارد کنید'}), 400

        user = User.query.filter_by(email=email).first()

        if not user:
            return jsonify({
                'success': True,
                'message': 'اگه این ایمیل توی سیستم باشه، لینک بازیابی ارسال میشه'
            })

        import secrets
        from datetime import timedelta
        token = secrets.token_urlsafe(32)
        expires =utcnow() + timedelta(hours=1)

        user.reset_token = token
        user.reset_expires = expires
        db.session.commit()

        reset_link = f"{request.host_url}reset-password?token={token}"

        from utils.email_service import get_email_service
        email_service = get_email_service()
        email_service.send_password_reset(
            to_email=user.email,
            username=user.display_name or user.username,
            reset_link=reset_link
        )

        response = {
            'success': True,
            'message': 'اگه این ایمیل توی سیستم باشه، لینک بازیابی ارسال میشه'
        }

        import os
        if os.environ.get('FLASK_ENV') == 'development':
            response['debug_token'] = token
            response['debug_link'] = reset_link

        return jsonify(response)

    except Exception as e:
        logger.error(f"❌ خطا در forgot-password: {e}")
        return jsonify({'error': 'خطای داخلی سرور'}), 500


# ============================================================
# تغییر رمز — محدودیت: ۵ بار در ساعت
# ============================================================

@auth_bp.route('/api/reset-password', methods=['POST'])
@limiter.limit("5 per hour")
def reset_password():
    try:
        data = request.json or {}
        token = (data.get('token') or '').strip()
        new_password = data.get('password') or ''

        if not token or not new_password:
            return jsonify({'error': 'توکن و رمز جدید لازمه'}), 400

        if not validate_password(new_password):
            return jsonify({'error': 'رمز باید حداقل ۸ کاراکتر، شامل حرف بزرگ، کوچک و عدد باشه'}), 400

        user = User.query.filter_by(reset_token=token).first()

        if not user:
            return jsonify({'error': 'توکن نامعتبره'}), 400

        if not user.reset_expires or user.reset_expires <utcnow():
            return jsonify({'error': 'توکن منقضی شده'}), 400

        user.password_hash = hash_password(new_password)
        user.reset_token = None
        user.reset_expires = None
        db.session.commit()

        return jsonify({'success': True, 'message': 'رمز با موفقیت تغییر کرد'})

    except Exception as e:
        logger.error(f"❌ خطا در reset-password: {e}")
        return jsonify({'error': 'خطای داخلی سرور'}), 500
