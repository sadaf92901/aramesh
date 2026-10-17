# ============================================================
# app.py — نقطه‌ی ورود اپلیکیشن
# ============================================================

import os
import time
from flask import Flask, render_template, request, jsonify, session
from flask_migrate import Migrate
from flask_cors import CORS

from database import db
from config import get_config
from utils.errors import register_error_handlers
from utils.logger import logger, log_request
from startup import preload_services


# ============================================================
# زمان شروع (برای health check)
# ============================================================

START_TIME = time.time()


# ============================================================
# ساخت اپ
# ============================================================

app = Flask(__name__)
app.config.from_object(get_config())

# ===== چک SECRET_KEY =====
if not app.config.get('SECRET_KEY'):
    raise ValueError("⚠️ SECRET_KEY توی .env تنظیم نشده!")


# ============================================================
# تنظیمات امنیتی Session
# ============================================================

app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'


# ============================================================
# CORS + Error Handlers
# ============================================================

CORS(app, origins=app.config.get('CORS_ORIGINS', ['*']))
register_error_handlers(app)


# ============================================================
# Rate Limiter
# ============================================================

from extensions import limiter
limiter.init_app(app)


# ============================================================
# Error Handler برای Rate Limit
# ============================================================

@app.errorhandler(429)
def ratelimit_handler(e):
    """پاسخ وقتی کاربر از حد مجاز عبور کرد"""
    if request.path.startswith('/api/'):
        logger.warning(f"⚠️ Rate Limit: {request.path} | IP={request.remote_addr}")
        return jsonify({
            'error': 'تعداد درخواست‌ها زیاد است. لطفاً کمی صبر کنید.',
            'status': 'error',
            'retry_after': str(e.description),
        }), 429
    return render_template('404.html'), 429


# ============================================================
# دیتابیس + Migration
# ============================================================

db.init_app(app)
migrate = Migrate(app, db)


# ============================================================
# ثبت Blueprintها
# ============================================================

from routes.pages import pages_bp
app.register_blueprint(pages_bp)

from routes.auth import auth_bp
app.register_blueprint(auth_bp)

from routes.status import status_bp
app.register_blueprint(status_bp)

from routes.notes import notes_bp
app.register_blueprint(notes_bp)

from routes.chat import chat_bp
app.register_blueprint(chat_bp)

from routes.diagnosis import diagnosis_bp
app.register_blueprint(diagnosis_bp)

from routes.breathing import breathing_bp
app.register_blueprint(breathing_bp)

from routes.weekly_plan import weekly_plan_bp
app.register_blueprint(weekly_plan_bp)

from routes.meditation import meditation_bp
app.register_blueprint(meditation_bp)

from routes.history import history_bp
app.register_blueprint(history_bp)

from routes.profile import profile_bp
app.register_blueprint(profile_bp)

from routes.garden import garden_bp
app.register_blueprint(garden_bp)

from routes.subscription import subscription_bp
app.register_blueprint(subscription_bp)

from routes.health import health_bp
app.register_blueprint(health_bp)


# ============================================================
# Security Headers
# ============================================================

@app.after_request
def add_security_headers(response):
    """اضافه کردن Security Headers به همه‌ی پاسخ‌ها"""
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(self), camera=()'

    return response


# ============================================================
# لاگ کردن درخواست‌ها
# ============================================================

@app.before_request
def log_request_info():
    """لاگ درخواست‌های API"""
    if request.path.startswith('/api/'):
        user_id = session.get('user_id')
        log_request(request, user_id)


# ============================================================
# پوشه‌ها
# ============================================================

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.static_folder, 'audio'), exist_ok=True)
os.makedirs(app.config['AVATAR_FOLDER'], exist_ok=True)

# ============================================================
# اجرا
# ============================================================

if __name__ == '__main__':
    # ===== لود سرویس‌ها =====
    preload_services()

    port = int(os.environ.get('PORT', 5000))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        use_reloader=False
    )