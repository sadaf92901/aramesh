# ============================================================
# تست‌های باغ آرامش
# ============================================================

import pytest
from datetime import datetime, timedelta
from database.models import Garden
from utils.garden_helper import give_seed, FLOWERS


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def user_id(app):
    """آی‌دی کاربر لاگین‌شده"""
    with app.app_context():
        from database.models import User
        import bcrypt

        user = User.query.filter_by(username='ali_70').first()
        if user:
            return user.id
        return None


@pytest.fixture
def logged_in_with_id(client, registered_user):
    """کلاینت لاگین‌شده + user_id"""
    # لاگین
    client.post('/api/login', json={
        'username': 'ali_70',
        'password': 'Ali12345'
    })
    return client


# ============================================================
# 1. Garden Model
# ============================================================

class TestGardenModel:
    """تست مدل Garden"""

    def test_create_seed(self, app):
        """ساخت یه دانه"""
        with app.app_context():
            from database.models import User
            import bcrypt

            # کاربر بساز
            user = User(
                username='test_garden_user',
                display_name='تست',
                email='garden@test.com',
                password_hash=bcrypt.hashpw(b'test1234', bcrypt.gensalt()).decode(),
                created_at=datetime.utcnow()
            )
            from database import db
            db.session.add(user)
            db.session.commit()

            # دانه بساز
            seed = Garden(
                user_id=user.id,
                activity_type='diagnosis',
                flower_type='🌸',
                date='2026-10-08',
                is_planted=False
            )
            db.session.add(seed)
            db.session.commit()

            assert seed.id is not None
            assert seed.activity_type == 'diagnosis'
            assert seed.flower_type == '🌸'
            assert seed.is_planted is False

            # پاکسازی
            db.session.delete(seed)
            db.session.delete(user)
            db.session.commit()

    def test_to_dict(self, app):
        """تست to_dict"""
        with app.app_context():
            from database.models import User
            from database import db
            import bcrypt

            user = User(
                username='test_to_dict',
                email='todict@test.com',
                password_hash=bcrypt.hashpw(b'test1234', bcrypt.gensalt()).decode(),
                created_at=datetime.utcnow()
            )
            db.session.add(user)
            db.session.commit()

            seed = Garden(
                user_id=user.id,
                activity_type='note',
                flower_type='🌷',
                date='2026-10-08',
                is_planted=True,
                planted_at=datetime.utcnow()
            )
            db.session.add(seed)
            db.session.commit()

            data = seed.to_dict()

            assert data['id'] == seed.id
            assert data['activity_type'] == 'note'
            assert data['flower_type'] == '🌷'
            assert data['is_planted'] is True
            assert data['date'] == '2026-10-08'
            assert data['planted_at'] is not None

            db.session.delete(seed)
            db.session.delete(user)
            db.session.commit()


# ============================================================
# 2. give_seed
# ============================================================

class TestGiveSeed:
    """تست تابع give_seed"""

    def test_give_seed_first_time(self, app):
        """بار اول → دانه بده"""
        with app.app_context():
            from database.models import User
            from database import db
            import bcrypt

            user = User(
                username='test_give_seed_1',
                email='give1@test.com',
                password_hash=bcrypt.hashpw(b'test1234', bcrypt.gensalt()).decode(),
                created_at=datetime.utcnow()
            )
            db.session.add(user)
            db.session.commit()

            # اولین بار
            seed = give_seed(user.id, 'diagnosis')

            assert seed is not None
            assert seed.activity_type == 'diagnosis'
            assert seed.flower_type == '🌸'

            # پاکسازی
            Garden.query.filter_by(user_id=user.id).delete()
            db.session.delete(user)
            db.session.commit()

    def test_give_seed_same_day(self, app):
        """همون روز → فقط یه دانه"""
        with app.app_context():
            from database.models import User
            from database import db
            import bcrypt

            user = User(
                username='test_give_seed_2',
                email='give2@test.com',
                password_hash=bcrypt.hashpw(b'test1234', bcrypt.gensalt()).decode(),
                created_at=datetime.utcnow()
            )
            db.session.add(user)
            db.session.commit()

            # بار اول
            seed1 = give_seed(user.id, 'diagnosis')

            # بار دوم همون روز
            seed2 = give_seed(user.id, 'diagnosis')

            # باید همون seed1 باشه (نه جدید)
            assert seed2.id == seed1.id

            # تعداد کل باید ۱ باشه
            count = Garden.query.filter_by(user_id=user.id).count()
            assert count == 1

            # پاکسازی
            Garden.query.filter_by(user_id=user.id).delete()
            db.session.delete(user)
            db.session.commit()

    def test_give_seed_different_types(self, app):
        """انواع مختلف → دانه‌های مختلف"""
        with app.app_context():
            from database.models import User
            from database import db
            import bcrypt

            user = User(
                username='test_give_seed_3',
                email='give3@test.com',
                password_hash=bcrypt.hashpw(b'test1234', bcrypt.gensalt()).decode(),
                created_at=datetime.utcnow()
            )
            db.session.add(user)
            db.session.commit()

            # ۵ نوع مختلف
            types = ['diagnosis', 'note', 'breathing', 'meditation', 'daily_status']
            for t in types:
                give_seed(user.id, t)

            count = Garden.query.filter_by(user_id=user.id).count()
            assert count == 5

            # پاکسازی
            Garden.query.filter_by(user_id=user.id).delete()
            db.session.delete(user)
            db.session.commit()

    def test_give_seed_invalid_type(self, app):
        """نوع نامعتبر → None"""
        with app.app_context():
            from database.models import User
            from database import db
            import bcrypt

            user = User(
                username='test_give_seed_4',
                email='give4@test.com',
                password_hash=bcrypt.hashpw(b'test1234', bcrypt.gensalt()).decode(),
                created_at=datetime.utcnow()
            )
            db.session.add(user)
            db.session.commit()

            result = give_seed(user.id, 'invalid_type')

            assert result is None

            db.session.delete(user)
            db.session.commit()

    def test_give_seed_invalid_user(self,app):
        """کاربر نامعتبر → None"""

        with app.app_context():
            result = give_seed(99999, 'diagnosis')
            assert result is None

# ============================================================
# 3. Plant API
# ============================================================

class TestPlantSeed:
    """تست API کاشتن"""

    def test_plant_seed_success(self, app, logged_in_with_id):
        """کاشتن موفق"""
        with app.app_context():
            from database.models import User
            from database import db

            user = User.query.filter_by(username='ali_70').first()
            seed = give_seed(user.id, 'diagnosis')

            response = logged_in_with_id.post('/api/garden/plant', json={
                'seed_id': seed.id
            })

            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert 'flower' in data

            # چک کن توی DB
            updated_seed = db.session.get(Garden, seed.id)
            assert updated_seed.is_planted is True
            assert updated_seed.planted_at is not None

            # پاکسازی
            Garden.query.filter_by(user_id=user.id).delete()
            db.session.commit()

    def test_plant_seed_not_found(self, logged_in_with_id):
        """دانه پیدا نشد → 404"""
        response = logged_in_with_id.post('/api/garden/plant', json={
            'seed_id': 99999
        })

        assert response.status_code == 404

    def test_plant_seed_already_planted(self, app, logged_in_with_id):
        """دانه قبلاً کاشته شده → 404"""
        with app.app_context():
            from database.models import User
            from database import db

            user = User.query.filter_by(username='ali_70').first()
            seed = give_seed(user.id, 'note')

            # کاشت اول
            logged_in_with_id.post('/api/garden/plant', json={'seed_id': seed.id})

            # کاشت دوم
            response = logged_in_with_id.post('/api/garden/plant', json={
                'seed_id': seed.id
            })

            assert response.status_code == 404

            # پاکسازی
            Garden.query.filter_by(user_id=user.id).delete()
            db.session.commit()

    def test_plant_seed_no_auth(self, client):
        """بدون لاگین → 401"""
        response = client.post('/api/garden/plant', json={'seed_id': 1})
        assert response.status_code == 401

    def test_plant_seed_missing_id(self, logged_in_with_id):
        """بدون seed_id → 400"""
        response = logged_in_with_id.post('/api/garden/plant', json={})
        assert response.status_code == 400


# ============================================================
# 4. Garden GET API
# ============================================================

class TestGetGarden:
    """تست API خواندن باغ"""

    def test_get_empty_garden(self, logged_in_with_id):
        """باغ خالی"""
        response = logged_in_with_id.get('/api/garden')

        assert response.status_code == 200
        data = response.get_json()

        assert 'seeds' in data
        assert 'flowers' in data
        assert 'stats' in data
        assert data['seeds'] == []
        assert data['flowers'] == []
        assert data['stats']['total_flowers'] == 0
        assert data['stats']['total_seeds'] == 0

    def test_get_garden_with_seeds(self, app, logged_in_with_id):
        """باغ با دانه (کاشته‌نشده)"""
        with app.app_context():
            from database.models import User
            from database import db

            user = User.query.filter_by(username='ali_70').first()
            give_seed(user.id, 'diagnosis')
            give_seed(user.id, 'note')

            response = logged_in_with_id.get('/api/garden')
            data = response.get_json()

            assert len(data['seeds']) == 2
            assert len(data['flowers']) == 0
            assert data['stats']['total_seeds'] == 2

            # پاکسازی
            Garden.query.filter_by(user_id=user.id).delete()
            db.session.commit()

    def test_get_garden_with_flowers(self, app, logged_in_with_id):
        """باغ با گل (کاشته‌شده)"""
        with app.app_context():
            from database.models import User
            from database import db

            user = User.query.filter_by(username='ali_70').first()
            seed = give_seed(user.id, 'breathing')

            # بکارش
            logged_in_with_id.post('/api/garden/plant', json={'seed_id': seed.id})

            response = logged_in_with_id.get('/api/garden')
            data = response.get_json()

            assert len(data['seeds']) == 0
            assert len(data['flowers']) == 1
            assert data['stats']['total_flowers'] == 1

            # پاکسازی
            Garden.query.filter_by(user_id=user.id).delete()
            db.session.commit()

    def test_get_garden_no_auth(self, client):
        """بدون لاگین → 401"""
        response = client.get('/api/garden')
        assert response.status_code == 401


# ============================================================
# 5. Stats
# ============================================================

class TestGardenStats:
    """تست آمار باغ"""

    def test_stats_unique_days(self, app, logged_in_with_id):
        """تعداد روزهای فعال"""
        with app.app_context():
            from database.models import User
            from database import db

            user = User.query.filter_by(username='ali_70').first()

            # ۳ گل در ۲ روز مختلف
            today = datetime.now().isoformat().split('T')[0]
            yesterday = (datetime.now() - timedelta(days=1)).isoformat().split('T')[0]

            seed1 = Garden(user_id=user.id, activity_type='diagnosis',
                          flower_type='🌸', date=today, is_planted=True,
                          planted_at=datetime.utcnow())
            seed2 = Garden(user_id=user.id, activity_type='note',
                          flower_type='🌷', date=today, is_planted=True,
                          planted_at=datetime.utcnow())
            seed3 = Garden(user_id=user.id, activity_type='breathing',
                          flower_type='🌿', date=yesterday, is_planted=True,
                          planted_at=datetime.utcnow())

            db.session.add_all([seed1, seed2, seed3])
            db.session.commit()

            response = logged_in_with_id.get('/api/garden')
            data = response.get_json()

            assert data['stats']['total_flowers'] == 3
            assert data['stats']['unique_days'] == 2

            # پاکسازی
            Garden.query.filter_by(user_id=user.id).delete()
            db.session.commit()

    def test_stats_streak(self, app, logged_in_with_id):
        """استریک"""
        with app.app_context():
            from database.models import User
            from database import db

            user = User.query.filter_by(username='ali_70').first()

            # استریک ۳ روزه
            for i in range(3):
                date = (datetime.now() - timedelta(days=i)).isoformat().split('T')[0]
                seed = Garden(
                    user_id=user.id,
                    activity_type='diagnosis',
                    flower_type='🌸',
                    date=date,
                    is_planted=True,
                    planted_at=datetime.utcnow()
                )
                db.session.add(seed)

            db.session.commit()

            response = logged_in_with_id.get('/api/garden')
            data = response.get_json()

            assert data['stats']['streak'] >= 3

            # پاکسازی
            Garden.query.filter_by(user_id=user.id).delete()
            db.session.commit()


# ============================================================
# 6. FLOWERS map
# ============================================================

class TestFlowersMap:
    """تست نقشه‌ی گل‌ها"""

    def test_flowers_map_has_all_types(self):
        """همه‌ی ۵ نوع فعالیت"""
        expected = {'diagnosis', 'note', 'breathing', 'meditation', 'daily_status'}
        assert set(FLOWERS.keys()) == expected

    def test_flowers_map_values(self):
        """مقادیر درست"""
        assert FLOWERS['diagnosis'] == '🌸'
        assert FLOWERS['note'] == '🌷'
        assert FLOWERS['breathing'] == '🌿'
        assert FLOWERS['meditation'] == '🪷'
        assert FLOWERS['daily_status'] == '🌻'
