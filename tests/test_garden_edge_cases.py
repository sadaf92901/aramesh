# ============================================================
# تست مرزهای باغ آرامش
# ============================================================

import pytest
from datetime import datetime
from database.models import Garden
from database import db
from utils.garden_helper import give_seed

# ============================================================
# Helper
# ============================================================

def get_user(username):
    """گرفتن کاربر"""
    from database.models import User
    return User.query.filter_by(username=username).first()

# ============================================================
# Helpers
# ============================================================

def create_flowers(user_id, flower_type, count, date=None):
    """ساخت سریع چند گل"""
    if date is None:
        date = datetime.now().isoformat().split('T')[0]

    flowers = []
    for i in range(count):
        f = Garden(
            user_id=user_id,
            activity_type='test',
            flower_type=flower_type,
            date=date,
            is_planted=True,
            planted_at=datetime.utcnow(),
            position_x=10 + (i % 80),
            position_y=50 + (i % 40)
        )
        db.session.add(f)
        flowers.append(f)

    db.session.commit()
    return flowers


# ============================================================
# Edge Cases
# ============================================================

class TestGardenEdgeCases:
    """تست مرزهای باغ"""

    def test_9_flowers_no_cluster(self, app, logged_in_client):
        """۹ گل → بدون خوشه"""
        with app.app_context():
            user = get_user('ali_70')
            create_flowers(user.id, '🌸', 9)

            response = logged_in_client.get('/api/garden')
            data = response.get_json()

            assert data['stats']['total_flowers'] == 9
            # تعداد خوشه‌ها = ۰ (هنوز به ۱۰ نرسیده)
            clusters = [f for f in data['flowers'] if f['flower_type'] == '🌸']
            assert len(clusters) == 9

            # پاکسازی
            Garden.query.filter_by(user_id=user.id).delete()
            db.session.commit()

    def test_10_flowers_creates_cluster(self, app, logged_in_client):
        """۱۰ گل → یه خوشه"""
        with app.app_context():
            user = get_user('ali_70')
            create_flowers(user.id, '🌷', 10)

            response = logged_in_client.get('/api/garden')
            data = response.get_json()

            assert data['stats']['total_flowers'] == 10

            # پاکسازی
            Garden.query.filter_by(user_id=user.id).delete()
            db.session.commit()

    def test_19_flowers_one_cluster_and_9(self, app, logged_in_client):
        """۱۹ گل → ۱ خوشه + ۹ تکی"""
        with app.app_context():
            user = get_user('ali_70')
            create_flowers(user.id, '🌿', 19)

            response = logged_in_client.get('/api/garden')
            data = response.get_json()

            assert data['stats']['total_flowers'] == 19

            # پاکسازی
            Garden.query.filter_by(user_id=user.id).delete()
            db.session.commit()

    def test_100_flowers_creates_garden(self, app, logged_in_client):
        """۱۰۰ گل → ۱ باغچه"""
        with app.app_context():
            user = get_user('ali_70')
            create_flowers(user.id, '🌸', 100)

            response = logged_in_client.get('/api/garden')
            data = response.get_json()

            assert data['stats']['total_flowers'] == 100

            # پاکسازی
            Garden.query.filter_by(user_id=user.id).delete()
            db.session.commit()

    def test_110_flowers_garden_plus_cluster(self, app, logged_in_client):
        """۱۱۰ گل → ۱ باغچه + ۱ خوشه"""
        with app.app_context():
            user = get_user('ali_70')
            create_flowers(user.id, '🌸', 110)

            response = logged_in_client.get('/api/garden')
            data = response.get_json()

            assert data['stats']['total_flowers'] == 110

            # پاکسازی
            Garden.query.filter_by(user_id=user.id).delete()
            db.session.commit()

    def test_5_types_together(self, app, logged_in_client):
        """۵ نوع گل مختلف با هم"""
        with app.app_context():
            user = get_user('ali_70')

            create_flowers(user.id, '🌸', 15)
            create_flowers(user.id, '🌷', 25)
            create_flowers(user.id, '🌿', 12)
            create_flowers(user.id, '🪷', 8)
            create_flowers(user.id, '🌻', 30)

            response = logged_in_client.get('/api/garden')
            data = response.get_json()

            assert data['stats']['total_flowers'] == 15 + 25 + 12 + 8 + 30

            # پاکسازی
            Garden.query.filter_by(user_id=user.id).delete()
            db.session.commit()


class TestGardenStreak:
    """تست استریک"""

    def test_streak_1_day(self, app, logged_in_client):
        """۱ روز → استریک ۱"""
        with app.app_context():
            user = get_user('ali_70')
            today = datetime.now().isoformat().split('T')[0]
            create_flowers(user.id, '🌸', 1, date=today)

            response = logged_in_client.get('/api/garden')
            data = response.get_json()

            assert data['stats']['streak'] >= 1

            # پاکسازی
            Garden.query.filter_by(user_id=user.id).delete()
            db.session.commit()

    def test_streak_3_days(self, app, logged_in_client):
        """۳ روز متوالی → استریک ۳"""
        with app.app_context():
            from datetime import timedelta

            user = get_user('ali_70')

            for i in range(3):
                date = (datetime.now() - timedelta(days=i)).isoformat().split('T')[0]
                create_flowers(user.id, '🌸', 1, date=date)

            response = logged_in_client.get('/api/garden')
            data = response.get_json()

            assert data['stats']['streak'] >= 3

            # پاکسازی
            Garden.query.filter_by(user_id=user.id).delete()
            db.session.commit()

    def test_streak_broken(self, app, logged_in_client):
        """استریک شکسته (فاصله) → استریک ۱"""
        with app.app_context():
            from datetime import timedelta

            user = get_user('ali_70')

            # ۳ روز پیش
            date1 = (datetime.now() - timedelta(days=5)).isoformat().split('T')[0]
            create_flowers(user.id, '🌸', 1, date=date1)

            # امروز
            today = datetime.now().isoformat().split('T')[0]
            create_flowers(user.id, '🌸', 1, date=today)

            response = logged_in_client.get('/api/garden')
            data = response.get_json()

            # چون فاصله افتاده، استریک باید ۱ باشه
            assert data['stats']['streak'] == 1

            # پاکسازی
            Garden.query.filter_by(user_id=user.id).delete()
            db.session.commit()


class TestGardenStats:
    """تست آمار"""

    def test_unique_days(self, app, logged_in_client):
        """تعداد روزهای فعال"""
        with app.app_context():
            from datetime import timedelta

            user = get_user('ali_70')

            # ۳ گل توی ۳ روز مختلف
            for i in range(3):
                date = (datetime.now() - timedelta(days=i)).isoformat().split('T')[0]
                create_flowers(user.id, '🌸', 1, date=date)

            # ۲ گل توی همون روز سوم
            date = (datetime.now() - timedelta(days=2)).isoformat().split('T')[0]
            create_flowers(user.id, '🌸', 2, date=date)

            response = logged_in_client.get('/api/garden')
            data = response.get_json()

            assert data['stats']['total_flowers'] == 5
            assert data['stats']['unique_days'] == 3

            # پاکسازی
            Garden.query.filter_by(user_id=user.id).delete()
            db.session.commit()


class TestGardenPosition:
    """تست موقعیت گل‌ها"""

    def test_position_saved_on_plant(self, app, logged_in_client):
        """موقعیت هنگام کاشتن ذخیره می‌شه"""
        with app.app_context():
            user = get_user('ali_70')
            seed = give_seed(user.id, 'diagnosis')

            # بکارش
            logged_in_client.post('/api/garden/plant', json={'seed_id': seed.id})

            # چک کن
            updated = db.session.get(Garden, seed.id)
            assert updated.position_x is not None
            assert updated.position_y is not None
            assert 8 <= updated.position_x <= 88
            assert 45 <= updated.position_y <= 90

            # پاکسازی
            Garden.query.filter_by(user_id=user.id).delete()
            db.session.commit()

    def test_position_stable_after_reload(self, app, logged_in_client):
        """موقعیت بعد از reload تغییر نمی‌کنه"""
        with app.app_context():
            user = get_user('ali_70')
            seed = give_seed(user.id, 'note')
            logged_in_client.post('/api/garden/plant', json={'seed_id': seed.id})

            updated = db.session.get(Garden, seed.id)
            x1, y1 = updated.position_x, updated.position_y

            # دوباره fetch
            response = logged_in_client.get('/api/garden')
            data = response.get_json()

            flowers = data['flowers']
            assert len(flowers) == 1
            assert flowers[0]['position_x'] == x1
            assert flowers[0]['position_y'] == y1

            # پاکسازی
            Garden.query.filter_by(user_id=user.id).delete()
            db.session.commit()


