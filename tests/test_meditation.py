
# ============================================================
# تست مدیتیشن
# ============================================================

import pytest


class TestMeditation:
    def test_stats_empty(self, logged_in_client):
        response = logged_in_client.get('/api/meditation/stats')
        assert response.status_code == 200
        data = response.get_json()
        assert 'today_minutes' in data
        assert 'week_minutes' in data
        assert 'today_count' in data

    def test_save_meditation(self, logged_in_client):
        response = logged_in_client.post('/api/meditation/save', json={
            'type': 'morning',
            'duration': 300,
            'completed': True
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True

    def test_save_meditation_missing_data(self, logged_in_client):
        response = logged_in_client.post('/api/meditation/save', json={})
        assert response.status_code == 400

    def test_save_meditation_not_logged_in(self, client):
        response = client.post('/api/meditation/save', json={
            'type': 'morning',
            'duration': 300
        })
        assert response.status_code == 401

    def test_stats_after_meditation(self, logged_in_client):
        # ذخیره
        logged_in_client.post('/api/meditation/save', json={
            'type': 'morning',
            'duration': 300,
            'completed': True
        })

        # آمار
        response = logged_in_client.get('/api/meditation/stats')
        data = response.get_json()
        assert data['today_count'] >= 1
        assert data['today_minutes'] >= 5

    def test_history(self, logged_in_client):
        response = logged_in_client.get('/api/meditation/history')
        assert response.status_code == 200
        assert isinstance(response.get_json(), list)