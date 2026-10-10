# ============================================================
# تست وضعیت روزانه
# ============================================================

import pytest
from datetime import datetime


class TestDailyStatus:
    """تست وضعیت روزانه"""

    def test_get_empty_status(self, logged_in_client):
        """وضعیت اول خالیه"""
        response = logged_in_client.get('/api/daily-status')
        assert response.status_code == 200
        assert isinstance(response.get_json(), dict)

    def test_get_status_not_logged_in(self, client):
        """بدون لاگین، dict خالی برگردونه"""
        response = client.get('/api/daily-status')
        assert response.status_code == 200
        assert response.get_json() == {}

    def test_post_status_success(self, logged_in_client):
        """ثبت وضعیت موفق"""
        today = datetime.now().isoformat().split('T')[0]

        response = logged_in_client.post('/api/daily-status', json={
            'date': today,
            'mood': 'good',
            'energy': 'high',
            'sleep': 'great'
        })

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['date'] == today

    def test_post_status_not_logged_in(self, client):
        """بدون لاگین خطا بده"""
        response = client.post('/api/daily-status', json={
            'mood': 'good',
            'energy': 'high',
            'sleep': 'great'
        })
        assert response.status_code == 401

    def test_post_empty_data(self, logged_in_client):
        """داده خالی خطا بده"""
        response = logged_in_client.post('/api/daily-status', json={})
        assert response.status_code == 400

    def test_update_existing_status(self, logged_in_client):
        """بروزرسانی وضعیت موجود"""
        today = datetime.now().isoformat().split('T')[0]

        # ثبت اول
        logged_in_client.post('/api/daily-status', json={
            'date': today,
            'mood': 'good',
            'energy': 'high',
            'sleep': 'great'
        })

        # بروزرسانی
        response = logged_in_client.post('/api/daily-status', json={
            'date': today,
            'mood': 'bad',
            'energy': 'low',
            'sleep': 'bad'
        })

        assert response.status_code == 200

        # چک کن
        get_response = logged_in_client.get('/api/daily-status')
        data = get_response.get_json()

        assert today in data
        assert data[today]['mood'] == 'bad'

    def test_get_after_post(self, logged_in_client):
        """بعد از ثبت، وضعیت برگرده"""
        today = datetime.now().isoformat().split('T')[0]

        logged_in_client.post('/api/daily-status', json={
            'date': today,
            'mood': 'neutral',
            'energy': 'medium',
            'sleep': 'good'
        })

        response = logged_in_client.get('/api/daily-status')
        data = response.get_json()

        assert today in data
        assert data[today]['mood'] == 'neutral'
        assert data[today]['energy'] == 'medium'
        assert data[today]['sleep'] == 'good'