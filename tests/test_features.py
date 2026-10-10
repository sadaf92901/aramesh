# ============================================================
# تست Feature Flags و محدودیت‌ها
# ============================================================

import pytest
from datetime import datetime, timedelta


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def test_user(app):
    """ساخت یه کاربر تستی"""
    with app.app_context():
        from database.models import User
        from database import db
        import bcrypt

        user = User.query.filter_by(username='features_test_user').first()
        if not user:
            user = User(
                username='features_test_user',
                display_name='تست',
                email='features@test.com',
                password_hash=bcrypt.hashpw(b'test1234', bcrypt.gensalt()).decode(),
                created_at=datetime.utcnow()
            )
            db.session.add(user)
            db.session.commit()

        return user.id


@pytest.fixture
def premium_user(app):
    """ساخت کاربر با اشتراک پریمیوم"""
    with app.app_context():
        from database.models import User, Subscription
        from database import db
        import bcrypt

        user = User.query.filter_by(username='premium_test_user').first()
        if not user:
            user = User(
                username='premium_test_user',
                email='premium@test.com',
                password_hash=bcrypt.hashpw(b'test1234', bcrypt.gensalt()).decode(),
                created_at=datetime.utcnow()
            )
            db.session.add(user)
            db.session.commit()

        # ===== اشتراک فعال =====
        sub = Subscription.query.filter_by(user_id=user.id, status='active').first()
        if not sub:
            sub = Subscription(
                user_id=user.id,
                plan='premium',
                status='active',
                started_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(days=30)
            )
            db.session.add(sub)
            db.session.commit()

        return user.id


@pytest.fixture(autouse=True)
def cleanup(app):
    """پاکسازی بعد از هر تست"""
    yield

    with app.app_context():
        from database.models import User, Subscription
        from database import db

        # ===== ۱. اول Subscriptions رو حذف کن (FK) =====
        user_ids = [
            u.id for u in User.query.filter(
                User.username.in_(['features_test_user', 'premium_test_user'])
            ).all()
        ]

        if user_ids:
            Subscription.query.filter(
                Subscription.user_id.in_(user_ids)
            ).delete(synchronize_session=False)

            # ===== ۲. بعد کاربران =====
            User.query.filter(
                User.id.in_(user_ids)
            ).delete(synchronize_session=False)

            db.session.commit()


# ============================================================
# تست‌های FREE_LIMITS
# ============================================================

class TestFreeLimits:
    """تست محدودیت‌های پلن رایگان"""

    def test_free_limits_exists(self):
        from utils.features import FREE_LIMITS
        assert isinstance(FREE_LIMITS, dict)

    def test_free_limits_values(self):
        from utils.features import FREE_LIMITS

        assert FREE_LIMITS['diagnosis_per_day'] == 5
        assert FREE_LIMITS['chat_per_day'] == 50
        assert FREE_LIMITS['notes_per_day'] == 20
        assert FREE_LIMITS['history_days'] == 365
        assert FREE_LIMITS['plan_name'] == 'رایگان'

    def test_free_limits_features(self):
        from utils.features import FREE_LIMITS

        assert FREE_LIMITS['rag_enabled'] is True
        assert FREE_LIMITS['llm_summary'] is True
        assert FREE_LIMITS['pdf_export'] is True
        assert FREE_LIMITS['premium_themes'] is False
        assert FREE_LIMITS['cloud_backup'] is False


# ============================================================
# تست‌های PREMIUM_LIMITS
# ============================================================

class TestPremiumLimits:
    """تست محدودیت‌های پلن پریمیوم"""

    def test_premium_limits_exists(self):
        from utils.features import PREMIUM_LIMITS
        assert isinstance(PREMIUM_LIMITS, dict)

    def test_premium_unlimited(self):
        from utils.features import PREMIUM_LIMITS

        assert PREMIUM_LIMITS['diagnosis_per_day'] == -1
        assert PREMIUM_LIMITS['chat_per_day'] == -1
        assert PREMIUM_LIMITS['notes_per_day'] == -1

    def test_premium_features(self):
        from utils.features import PREMIUM_LIMITS

        assert PREMIUM_LIMITS['rag_enabled'] is True
        assert PREMIUM_LIMITS['premium_themes'] is True
        assert PREMIUM_LIMITS['cloud_backup'] is True

    def test_premium_plan_name(self):
        from utils.features import PREMIUM_LIMITS
        assert PREMIUM_LIMITS['plan_name'] == 'پریمیوم'


# ============================================================
# تست‌های PRO_LIMITS
# ============================================================

class TestProLimits:
    """تست پلن سازمانی"""

    def test_pro_limits_inherits_premium(self):
        from utils.features import PRO_LIMITS, PREMIUM_LIMITS

        assert PRO_LIMITS['diagnosis_per_day'] == PREMIUM_LIMITS['diagnosis_per_day']
        assert PRO_LIMITS['chat_per_day'] == PREMIUM_LIMITS['chat_per_day']

    def test_pro_unique_features(self):
        from utils.features import PRO_LIMITS

        assert PRO_LIMITS.get('api_access') is True
        assert PRO_LIMITS.get('clinic_panel') is True
        assert PRO_LIMITS['plan_name'] == 'سازمانی'


# ============================================================
# تست‌های get_user_limits
# ============================================================

class TestGetUserLimits:
    """تست get_user_limits"""

    def test_get_user_limits_none(self, app):
        from utils.features import get_user_limits, FREE_LIMITS

        with app.app_context():
            limits = get_user_limits(None)
            assert limits == FREE_LIMITS

    def test_get_user_limits_free_user(self, app, test_user):
        from utils.features import get_user_limits
        from database.models import User
        from database import db

        with app.app_context():
            user = db.session.get(User, test_user)
            limits = get_user_limits(user)
            assert limits['plan_name'] == 'رایگان'

    def test_get_user_limits_premium_user(self, app, premium_user):
        from utils.features import get_user_limits, PREMIUM_AVAILABLE
        from database.models import User
        from database import db

        with app.app_context():
            user = db.session.get(User, premium_user)
            limits = get_user_limits(user)

            if not PREMIUM_AVAILABLE:
                assert limits['plan_name'] == 'رایگان'


# ============================================================
# تست‌های is_premium
# ============================================================

class TestIsPremium:
    """تست is_premium"""

    def test_is_premium_none(self):
        from utils.features import is_premium
        assert is_premium(None) is False

    def test_is_premium_free_user(self, app, test_user):
        from utils.features import is_premium
        from database.models import User
        from database import db

        with app.app_context():
            user = db.session.get(User, test_user)
            assert is_premium(user) is False

    def test_is_premium_premium_user(self, app, premium_user):
        from utils.features import is_premium, PREMIUM_AVAILABLE
        from database.models import User
        from database import db

        with app.app_context():
            user = db.session.get(User, premium_user)
            result = is_premium(user)

            if not PREMIUM_AVAILABLE:
                assert result is False


# ============================================================
# تست‌های can_use
# ============================================================

class TestCanUse:
    """تست can_use"""

    def test_can_use_rag_enabled(self, app, test_user):
        from utils.features import can_use
        from database.models import User
        from database import db

        with app.app_context():
            user = db.session.get(User, test_user)
            assert can_use(user, 'rag_enabled') is True

    def test_can_use_premium_themes(self, app, test_user):
        from utils.features import can_use
        from database.models import User
        from database import db

        with app.app_context():
            user = db.session.get(User, test_user)
            assert can_use(user, 'premium_themes') is False

    def test_can_use_cloud_backup(self, app, test_user):
        from utils.features import can_use
        from database.models import User
        from database import db

        with app.app_context():
            user = db.session.get(User, test_user)
            assert can_use(user, 'cloud_backup') is False

    def test_can_use_nonexistent_feature(self, app, test_user):
        from utils.features import can_use
        from database.models import User
        from database import db

        with app.app_context():
            user = db.session.get(User, test_user)
            assert can_use(user, 'nonexistent_feature_xyz') is False


# ============================================================
# تست‌های check_daily_limit
# ============================================================

class TestCheckDailyLimit:
    """تست check_daily_limit"""

    def test_check_daily_limit_under(self, app, test_user):
        from utils.features import check_daily_limit
        from database.models import User
        from database import db

        with app.app_context():
            user = db.session.get(User, test_user)
            result = check_daily_limit(user, 'diagnosis_per_day', 2)

            assert result['allowed'] is True
            assert result['remaining'] == 3
            assert result['limit'] == 5

    def test_check_daily_limit_at(self, app, test_user):
        from utils.features import check_daily_limit
        from database.models import User
        from database import db

        with app.app_context():
            user = db.session.get(User, test_user)
            result = check_daily_limit(user, 'diagnosis_per_day', 5)

            assert result['allowed'] is False
            assert result['remaining'] == 0

    def test_check_daily_limit_over(self, app, test_user):
        from utils.features import check_daily_limit
        from database.models import User
        from database import db

        with app.app_context():
            user = db.session.get(User, test_user)
            result = check_daily_limit(user, 'diagnosis_per_day', 10)

            assert result['allowed'] is False
            assert result['remaining'] == 0

    def test_check_daily_limit_first_use(self, app, test_user):
        from utils.features import check_daily_limit
        from database.models import User
        from database import db

        with app.app_context():
            user = db.session.get(User, test_user)
            result = check_daily_limit(user, 'diagnosis_per_day', 0)

            assert result['allowed'] is True
            assert result['remaining'] == 5

    def test_check_daily_limit_chat(self, app, test_user):
        from utils.features import check_daily_limit
        from database.models import User
        from database import db

        with app.app_context():
            user = db.session.get(User, test_user)
            result = check_daily_limit(user, 'chat_per_day', 49)

            assert result['allowed'] is True
            assert result['remaining'] == 1


# ============================================================
# تست‌های check_monthly_limit
# ============================================================

class TestCheckMonthlyLimit:
    """تست check_monthly_limit"""

    def test_check_monthly_limit_under(self, app, test_user):
        from utils.features import check_monthly_limit
        from database.models import User
        from database import db

        with app.app_context():
            user = db.session.get(User, test_user)
            result = check_monthly_limit(user, 'diagnosis_per_month', 20)

            assert result['allowed'] is True
            assert result['remaining'] == 30

    def test_check_monthly_limit_at(self, app, test_user):
        from utils.features import check_monthly_limit
        from database.models import User
        from database import db

        with app.app_context():
            user = db.session.get(User, test_user)
            result = check_monthly_limit(user, 'diagnosis_per_month', 50)

            assert result['allowed'] is False
            assert result['remaining'] == 0
