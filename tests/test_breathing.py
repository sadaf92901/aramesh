
# ============================================================
# تست تمرین تنفس
# ============================================================

import pytest


class TestBreathing:
    """تست تمرین تنفس"""

    def test_get_breathing_empty(self, logged_in_client):
        response = logged_in_client.get('/api/breathing')
        assert response.status_code == 200
        data = response.get_json()
        assert 'today_count' in data
        assert 'week_count' in data

    def test_post_breathing(self, logged_in_client):
        response = logged_in_client.post('/api/breathing', json={
            'duration': 30
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['today_count'] >= 1

    def test_breathing_not_logged_in(self, client):
        response = client.get('/api/breathing')
        assert response.status_code == 401

    def test_multiple_breathings(self, logged_in_client):
        # ۳ تا تمرین
        for _ in range(3):
            logged_in_client.post('/api/breathing', json={'duration': 30})

        response = logged_in_client.get('/api/breathing')
        data = response.get_json()
        assert data['today_count'] == 3