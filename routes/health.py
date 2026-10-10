# ============================================================
# routes/health.py — Health Check
# ============================================================

from flask import Blueprint, jsonify
from database import db
from sqlalchemy import text
import time


health_bp = Blueprint('health', __name__)


# ============================================================
# /healthz — بررسی سلامت سرور
# ============================================================

@health_bp.route('/healthz', methods=['GET'])
def healthz():
    """
    بررسی سلامت سرور

    Returns:
        JSON:
        {
            "status": "ok" | "degraded" | "down",
            "version": "1.1.0",
            "uptime_seconds": 123.45,
            "checks": {
                "database": "ok",
                "disk": "ok",
                "disk_free_gb": 45.67
            },
            "response_time_ms": 5
        }
    """
    start = time.time()

    checks = {}
    overall_status = 'ok'

    # ===== ۱. چک دیتابیس =====
    try:
        db.session.execute(text('SELECT 1'))
        checks['database'] = 'ok'
    except Exception as e:
        checks['database'] = 'error'
        overall_status = 'down'

    # ===== ۲. چک دیسک =====
    try:
        import shutil
        total, used, free = shutil.disk_usage('/')
        free_gb = free / (1024 ** 3)

        if free_gb < 1:
            checks['disk'] = 'low'
            overall_status = 'degraded'
        else:
            checks['disk'] = 'ok'

        checks['disk_free_gb'] = round(free_gb, 2)
    except Exception:
        checks['disk'] = 'unknown'

    # ===== ۳. Uptime =====
    uptime = 0
    try:
        from app import START_TIME
        uptime = round(time.time() - START_TIME, 2)
    except Exception:
        pass

    # ===== ۴. پاسخ =====
    response_time = round((time.time() - start) * 1000, 2)

    response = {
        'status': overall_status,
        'version': '1.1.0',
        'service': 'aramesh',
        'uptime_seconds': uptime,
        'checks': checks,
        'response_time_ms': response_time,
    }

    # ===== Status Code =====
    status_code = 200 if overall_status == 'ok' else 503

    return jsonify(response), status_code


# ============================================================
# /healthz/ready — آماده‌بودن (Load Balancer)
# ============================================================

@health_bp.route('/healthz/ready', methods=['GET'])
def healthz_ready():
    """بررسی آماده‌ی دریافت ترافیک"""
    try:
        db.session.execute(text('SELECT 1'))
        return jsonify({'ready': True}), 200
    except Exception:
        return jsonify({'ready': False}), 503


# ============================================================
# /healthz/live — زنده‌بودن (Kubernetes)
# ============================================================

@health_bp.route('/healthz/live', methods=['GET'])
def healthz_live():
    """بررسی زنده‌بودن فرآیند"""
    return jsonify({'alive': True}), 200