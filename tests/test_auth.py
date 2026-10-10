
# ============================================================
# تست احراز هویت
# ============================================================

import pytest


class TestRegister:
    """تست ثبت‌نام"""

    def test_register_success(self, client):
        response = client.post('/api/register', json={
            'username': 'ali_70',
            'display_name': 'علی رضایی',
            'email': 'ali@example.com',
            'password': 'Ali12345'
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['username'] == 'ali_70'
        assert data['display_name'] == 'علی رضایی'

    def test_register_missing_fields(self, client):
        response = client.post('/api/register', json={
            'username': 'ali_70',
        })
        assert response.status_code == 400
        assert 'error' in response.get_json()

    def test_register_invalid_username(self, client):
        """نام کاربری فارسی"""
        response = client.post('/api/register', json={
            'username': 'علی',
            'email': 'ali@example.com',
            'password': 'Ali12345'
        })
        assert response.status_code == 400

    def test_register_short_username(self, client):
        response = client.post('/api/register', json={
            'username': 'a',
            'email': 'ali@example.com',
            'password': 'Ali12345'
        })
        assert response.status_code == 400

    def test_register_invalid_email(self, client):
        """ایمیل بدون @"""
        response = client.post('/api/register', json={
            'username': 'ali_70',
            'email': 'ali.com',
            'password': 'Ali12345'
        })
        assert response.status_code == 400

    def test_register_weak_password(self, client):
        """رمز کوتاه"""
        response = client.post('/api/register', json={
            'username': 'ali_70',
            'email': 'ali@example.com',
            'password': '123'
        })
        assert response.status_code == 400

    def test_register_password_no_uppercase(self, client):
        response = client.post('/api/register', json={
            'username': 'ali_70',
            'email': 'ali@example.com',
            'password': 'ali12345'
        })
        assert response.status_code == 400

    def test_register_duplicate_username(self, client, registered_user):
        response = client.post('/api/register', json={
            'username': 'ali_70',
            'email': 'other@example.com',
            'password': 'Ali12345'
        })
        assert response.status_code == 400

    def test_register_duplicate_email(self, client, registered_user):
        response = client.post('/api/register', json={
            'username': 'other_70',
            'email': 'ali@example.com',
            'password': 'Ali12345'
        })
        assert response.status_code == 400


class TestLogin:
    """تست ورود"""


    def test_login_wrong_password(self, client, registered_user):
        response = client.post('/api/login', json={
            'username': 'ali_70',
            'password': 'WrongPass1'
        })
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        response = client.post('/api/login', json={
            'username': 'nobody',
            'password': 'AnyPass1'
        })
        assert response.status_code == 401

    def test_login_missing_fields(self, client):
        response = client.post('/api/login', json={
            'username': 'ali_70'
        })
        assert response.status_code == 400


class TestLogout:
    """تست خروج"""

    def test_logout(self, logged_in_client):
        response = logged_in_client.post('/api/logout')
        assert response.status_code == 200
        assert response.get_json()['success'] is True


class TestMe:
    """تست کاربر فعلی"""

    def test_me_logged_in(self, logged_in_client):
        response = logged_in_client.get('/api/me')
        assert response.status_code == 200
        data = response.get_json()
        assert data['username'] == 'ali_70'

    def test_me_not_logged_in(self, client):
        response = client.get('/api/me')
        assert response.status_code == 401