# ============================================================
# تست‌های پنل ادمین
# ============================================================

import pytest
from database import db
from database.models import User


class TestAdminAccess:
    """تست‌های دسترسی به پنل ادمین"""

    def test_admin_panel_without_login(self, client):
        """دسترسی به پنل ادمین بدون لاگین (باید ریدایرکت بشه)"""
        response = client.get('/admin', follow_redirects=False)
        assert response.status_code in [302,308]
        assert '/' in response.headers['Location']

    def test_admin_api_without_login(self, client):
        """دسترسی به API ادمین بدون لاگین (باید 403 بده)"""
        response = client.get('/admin/api/stats')
        assert response.status_code == 403
        assert response.json.get('error') == 'دسترسی غیرمجاز'

    def test_admin_panel_with_normal_user(self, client, auth_user):
        """دسترسی کاربر عادی به پنل ادمین (باید ریدایرکت بشه)"""
        client.post('/api/login', json={
            'username': 'normaluser',
            'password': 'Test1234'
        })
        response = client.get('/admin', follow_redirects=False)
        assert response.status_code in [302,308]

    def test_admin_api_with_normal_user(self, client, auth_user):
        """دسترسی کاربر عادی به API ادمین (باید 403 بده)"""
        client.post('/api/login', json={
            'username': 'normaluser',
            'password': 'Test1234'
        })
        response = client.get('/admin/api/stats')
        assert response.status_code == 403


class TestAdminDashboard:
    """تست‌های داشبورد ادمین"""

    def test_admin_stats_api(self, client, auth_admin):
        """گرفتن آمار توسط ادمین"""
        client.post('/api/login', json={
            'username': 'adminuser',
            'password': 'Test1234'
        })
        response = client.get('/admin/api/stats')
        assert response.status_code == 200
        data = response.json
        assert 'total_users' in data
        assert 'total_diagnoses' in data
        assert 'total_flowers' in data

    def test_admin_users_page(self, client, auth_admin):
        """صفحه کاربران ادمین"""
        client.post('/api/login', json={
            'username': 'adminuser',
            'password': 'Test1234'
        })
        response = client.get('/admin/users')
        assert response.status_code == 200
        assert b'adminuser' in response.data


class TestAdminActions:
    """تست‌های عملیات ادمین"""

    def test_toggle_admin_status(self, client, auth_admin, auth_user):
        """تغییر وضعیت ادمین یک کاربر"""
        client.post('/api/login', json={
            'username': 'adminuser',
            'password': 'Test1234'
        })

        with client.application.app_context():
            normal_user = User.query.filter_by(username='normaluser').first()
            user_id = normal_user.id

        response = client.post(f'/admin/api/users/{user_id}/toggle-admin')
        assert response.status_code == 200
        assert response.json.get('success') is True

    def test_toggle_own_admin_status(self, client, auth_admin):
        """ادمین نمی‌تواند وضعیت ادمین خودش را تغییر دهد"""
        client.post('/api/login', json={
            'username': 'adminuser',
            'password': 'Test1234'
        })

        with client.application.app_context():
            admin_user = User.query.filter_by(username='adminuser').first()
            admin_id = admin_user.id

        response = client.post(f'/admin/api/users/{admin_id}/toggle-admin')
        assert response.status_code == 400
        assert 'نمی‌تونی' in response.json.get('error', '')

    def test_delete_user(self, client, auth_admin, auth_user):
        """حذف یک کاربر توسط ادمین"""
        client.post('/api/login', json={
            'username': 'adminuser',
            'password': 'Test1234'
        })

        with client.application.app_context():
            normal_user = User.query.filter_by(username='normaluser').first()
            user_id = normal_user.id
        response = client.delete(f'/admin/api/users/{user_id}')
        assert response.status_code == 200
        assert response.json.get('success') is True