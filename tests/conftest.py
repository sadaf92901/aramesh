

# ============================================================
# تنظیمات مشترک تست‌ها
# ============================================================

import pytest
import os
import sys
import tempfile

# ===== اضافه کردن مسیر پروژه =====
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as flask_app
from database import db


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def app():
    """ساخت اپ برای تست"""
    # ===== دیتابیس موقت =====
    db_fd, db_path = tempfile.mkstemp()

    flask_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key',
        'LLM_ENABLED': False,
        'SPEECH_ENABLED': False,
        'RAG_ENABLED': False,
        'RATELIMIT_ENABLED': False,
    })
    from  extensions import  limiter
    limiter.enabled=False

    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """کلاینت تست"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """CLI runner"""
    return app.test_cli_runner()


# ============================================================
# Helper Functions
# ============================================================

@pytest.fixture
def registered_user(client):
    """ساخت یه کاربر ثبت‌نام‌شده"""
    response = client.post('/api/register', json={
        'username': 'ali_70',
        'display_name': 'علی رضایی',
        'email': 'ali@example.com',
        'password': 'Ali12345'
    })
    return response


@pytest.fixture
def logged_in_client(client, registered_user):
    """کلاینت لاگین‌شده"""
    client.post('/api/login', json={
        'username': 'ali_70',
        'password': 'Ali12345'
    })
    return client


# ============================================================
# Fixtures برای پنل ادمین
# ============================================================

@pytest.fixture
def auth_user(app):
    """ساخت کاربر عادی برای تست"""
    import bcrypt
    from database.models import User

    with app.app_context():
        # پاک کردن کاربر قبلی (اگر وجود داره)
        existing = User.query.filter_by(username='normaluser').first()
        if existing:
            db.session.delete(existing)
            db.session.commit()

        # هش کردن رمز عبور
        password_hash = bcrypt.hashpw('Test1234'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        user = User(
            username='normaluser',
            display_name='کاربر عادی',
            email='normal@test.com',
            password_hash=password_hash,
            is_admin=False
        )
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def auth_admin(app):
    """ساخت کاربر ادمین برای تست"""
    import bcrypt
    from database.models import User

    with app.app_context():
        # پاک کردن ادمین قبلی (اگر وجود داره)
        existing = User.query.filter_by(username='adminuser').first()
        if existing:
            db.session.delete(existing)
            db.session.commit()

        password_hash = bcrypt.hashpw('Test1234'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        admin = User(
            username='adminuser',
            display_name='مدیر سیستم',
            email='admin@test.com',
            password_hash=password_hash,
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        return admin