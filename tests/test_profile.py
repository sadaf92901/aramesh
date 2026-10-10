
# ============================================================
# تست پروفایل
# ============================================================

import pytest


class TestProfile:
    """تست پروفایل"""

    def test_get_profile(self, logged_in_client):
        response = logged_in_client.get('/api/profile')
        assert response.status_code == 200
        data = response.get_json()
        assert data['username'] == 'ali_70'
        assert data['email'] == 'ali@example.com'

    def test_get_profile_not_logged_in(self, client):
        response = client.get('/api/profile')
        assert response.status_code == 401

    def test_update_profile(self, logged_in_client):
        response = logged_in_client.put('/api/profile/update', json={
            'display_name': 'علی جدید',
            'email': 'newemail@example.com'
        })
        assert response.status_code == 200

    def test_update_profile_invalid_email(self, logged_in_client):
        response = logged_in_client.put('/api/profile/update', json={
            'display_name': 'علی',
            'email': 'invalid-email'
        })
        assert response.status_code == 400

    def test_change_password_wrong_current(self, logged_in_client):
        response = logged_in_client.post('/api/profile/change-password', json={
            'current_password': 'WrongPass1',
            'new_password': 'NewPass123'
        })
        assert response.status_code == 400

    def test_change_password_weak_new(self, logged_in_client):
        response = logged_in_client.post('/api/profile/change-password', json={
            'current_password': 'Ali12345',
            'new_password': '123'
        })
        assert response.status_code == 400

    def test_change_password_success(self, logged_in_client):
        response = logged_in_client.post('/api/profile/change-password', json={
            'current_password': 'Ali12345',
            'new_password': 'NewPass123'
        })
        assert response.status_code == 200

    def test_profile_stats(self, logged_in_client):
        response = logged_in_client.get('/api/profile/stats')
        assert response.status_code == 200
        data = response.get_json()
        assert 'total_diagnoses' in data
        assert 'total_notes' in data