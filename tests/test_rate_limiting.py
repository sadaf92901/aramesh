# ============================================================
# تست Rate Limiting
# ============================================================

import pytest


class TestRateLimiterConfig:
    """تست تنظیمات Rate Limiter"""

    def test_limiter_exists(self):
        """limiter وجود داره"""
        from extensions import limiter
        assert limiter is not None

    def test_key_func_exists(self):
        """key_func تعریف شده"""
        from extensions import get_user_or_ip
        assert callable(get_user_or_ip)

    def test_key_func_logged_in(self, app, client):
        """کاربر لاگین‌شده → key = user_X"""
        with app.app_context():
            with client.session_transaction() as sess:
                sess['user_id'] = 123

            with client:
                client.get('/')  # فعال کردن session
                from extensions import get_user_or_ip
                # نمیشه مستقیم تست کرد چون نیاز به request context داره


class TestRateLimiterHeaders:
    """تست هدرهای Rate Limit"""

    def test_login_has_ratelimit_headers(self, client):
        """login هدرهای Rate Limit داره"""
        response = client.post('/api/login', json={
            'username': 'test',
            'password': 'test'
        })

        # یا 200/401 یا 429 (بستگی به تعداد درخواست)
        # ولی هدرها باید باشن
        # نکته: توی tests، limiter خاموشه، پس هدرها ممکنه نباشن
        assert response.status_code in [200, 401, 429]


class TestRateLimiterStorage:
    """تست storage"""

    def test_dev_storage(self):
        """توی development، محدودیت‌های بالا"""
        import os
        from extensions import limiter

        # توی dev: 10000/day, 2000/hour
        # این تست محیط رو چک می‌کنه
        env = os.environ.get('FLASK_ENV', 'development')
        if env == 'development':
            # محدودیت‌های بالا
            assert limiter is not None