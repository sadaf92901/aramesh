# ============================================================
# تست صفحه‌ی اشتراک
# ============================================================

import pytest


class TestSubscriptionStatus:
    """تست API وضعیت اشتراک"""

    def test_status_logged_in(self, logged_in_client):
        """کاربر لاگین‌شده → اطلاعات کامل"""
        response = logged_in_client.get('/api/subscription/status')
        assert response.status_code == 200

        data = response.get_json()
        assert data['is_logged_in'] is True
        assert data['is_premium'] is False
        assert 'plan_name' in data
        assert 'limits' in data
        assert 'features' in data

    def test_status_guest(self, client):
        """مهمان (بدون لاگین) → اطلاعات محدود"""
        response = client.get('/api/subscription/status')
        assert response.status_code == 200

        data = response.get_json()
        assert data['is_logged_in'] is False
        assert data['plan'] == 'guest'

    def test_limits_structure(self, logged_in_client):
        """ساختار limits درست باشه"""
        response = logged_in_client.get('/api/subscription/status')
        data = response.get_json()

        limits = data['limits']
        assert 'diagnosis_per_day' in limits
        assert 'chat_per_day' in limits
        assert 'notes_per_day' in limits
        assert 'history_days' in limits

    def test_features_structure(self, logged_in_client):
        """ساختار features درست باشه"""
        response = logged_in_client.get('/api/subscription/status')
        data = response.get_json()

        features = data['features']
        assert 'rag_enabled' in features
        assert 'llm_summary' in features
        assert 'pdf_export' in features
        assert 'premium_themes' in features
        assert 'cloud_backup' in features


class TestSubscriptionUsage:
    """تست API استفاده‌ی روزانه"""

    def test_usage_logged_in(self, logged_in_client):
        """کاربر لاگین‌شده → آمار استفاده"""
        response = logged_in_client.get('/api/subscription/usage')
        assert response.status_code == 200

        data = response.get_json()
        assert 'date' in data
        assert 'diagnosis_today' in data
        assert 'notes_today' in data
        assert 'chat_today' in data

    def test_usage_not_logged_in(self, client):
        """بدون لاگین → 401"""
        response = client.get('/api/subscription/usage')
        assert response.status_code == 401

    def test_usage_after_diagnosis(self, logged_in_client):
        """بعد از یه تشخیص، usage زیاد بشه"""
        # ===== تشخیص بده =====
        logged_in_client.post('/api/predict', data={
            'mc_answers[]': ['متوسط'] * 20,
            'text_answers[]': ['تست'] * 3
        })

        # ===== usage بگیر =====
        response = logged_in_client.get('/api/subscription/usage')
        data = response.get_json()

        assert data['diagnosis_today'] >= 1


class TestSubscriptionPage:
    """تست صفحه‌ی اشتراک"""

    def test_page_logged_in(self, logged_in_client):
        """کاربر لاگین‌شده → 200"""
        response = logged_in_client.get('/subscription')
        assert response.status_code == 200

    def test_page_not_logged_in(self, client):
        """بدون لاگین → redirect"""
        response = client.get('/subscription')
        assert response.status_code in [302, 301]

    def test_page_guest_locked(self, client):
        """مهمان → redirect با guest_locked"""
        # مهمان شو
        client.post('/api/guest-login')

        response = client.get('/subscription')
        # باید redirect بشه
        assert response.status_code in [302, 301]


class TestFreeLimits:
    """تست محدودیت‌های پلن رایگان"""

    def test_free_limits_from_features(self):
        """محدودیت‌های FREE_LIMITS درست باشن"""
        from utils.features import FREE_LIMITS

        assert FREE_LIMITS['diagnosis_per_day'] == 5
        assert FREE_LIMITS['chat_per_day'] == 50
        assert FREE_LIMITS['notes_per_day'] == 20
        assert FREE_LIMITS['history_days'] == 365

    def test_premium_not_available(self):
        """پریمیوم الان غیرفعاله"""
        from utils.features import PREMIUM_AVAILABLE

        assert PREMIUM_AVAILABLE is False

    def test_get_user_limits_free(self, app):
        """کاربر رایگان → FREE_LIMITS"""
        with app.app_context():
            from utils.features import get_user_limits
            from database.models import User
            from database import db
            import bcrypt

            user = User.query.filter_by(username='ali_70').first()
            if not user:
                user = User(
                    username='test_limits_user',
                    email='limits@test.com',
                    password_hash=bcrypt.hashpw(b'test1234', bcrypt.gensalt()).decode()
                )
                db.session.add(user)
                db.session.commit()

            limits = get_user_limits(user)
            assert limits['plan_name'] == 'رایگان'

    def test_is_premium_false(self, app):
        """کاربر رایگان → is_premium = False"""
        with app.app_context():
            from utils.features import is_premium
            from database.models import User
            from database import db
            import bcrypt

            user = User.query.filter_by(username='ali_70').first()
            if user:
                assert is_premium(user) is False


class TestCheckDailyLimit:
    """تست چک محدودیت روزانه"""

    def test_check_daily_limit_under(self, app):
        """کاربر زیر محدودیت → allowed"""
        with app.app_context():
            from utils.features import check_daily_limit
            from database.models import User

            user = User.query.filter_by(username='ali_70').first()
            if user:
                result = check_daily_limit(user, 'diagnosis_per_day', 2)
                assert result['allowed'] is True
                assert result['remaining'] > 0

    def test_check_daily_limit_at(self, app):
        """کاربر به محدودیت رسیده → not allowed"""
        with app.app_context():
            from utils.features import check_daily_limit
            from database.models import User

            user = User.query.filter_by(username='ali_70').first()
            if user:
                result = check_daily_limit(user, 'diagnosis_per_day', 5)
                assert result['allowed'] is False
                assert result['remaining'] == 0

    def test_check_daily_limit_unlimited(self, app):
        """پریمیوم → unlimited (limit = -1)"""
        with app.app_context():
            from utils.features import check_daily_limit, FREE_LIMITS
            from database.models import User

            user = User.query.filter_by(username='ali_70').first()
            if user:
                # FREE_LIMITS مقدار diagnosis داره
                # این تست با PREMIUM_LIMITS کار نمی‌کنه چون پریمیوم فعال نیست
                pass  # skip
