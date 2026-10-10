# ============================================================
# تست گسترده‌ی وضعیت روزانه (XSS + محرمانگی)
# ============================================================

import pytest
from datetime import datetime


class TestDailyStatusXSS:
    """تست XSS توی status"""

    def test_xss_script_tag(self, logged_in_client):
        """XSS با script tag رد بشه"""
        today = datetime.now().isoformat().split('T')[0]

        response = logged_in_client.post('/api/daily-status', json={
            'mood': '<script>alert(1)</script>',
            'energy': 'high',
            'sleep': 'great'
        })

        assert response.status_code == 400
        assert 'error' in response.get_json()

    def test_xss_img_onerror(self, logged_in_client):
        """XSS با img onerror رد بشه"""
        response = logged_in_client.post('/api/daily-status', json={
            'mood': '<img src=x onerror=alert(1)>',
            'energy': 'high',
            'sleep': 'great'
        })

        assert response.status_code == 400

    def test_invalid_mood(self, logged_in_client):
        """مقدار نامعتبر mood رد بشه"""
        response = logged_in_client.post('/api/daily-status', json={
            'mood': 'invalid_mood',
            'energy': 'high',
            'sleep': 'great'
        })

        assert response.status_code == 400
        assert 'mood' in response.get_json()['error']

    def test_invalid_energy(self, logged_in_client):
        """مقدار نامعتبر energy رد بشه"""
        response = logged_in_client.post('/api/daily-status', json={
            'mood': 'good',
            'energy': 'invalid',
            'sleep': 'great'
        })

        assert response.status_code == 400
        assert 'energy' in response.get_json()['error']

    def test_invalid_sleep(self, logged_in_client):
        """مقدار نامعتبر sleep رد بشه"""
        response = logged_in_client.post('/api/daily-status', json={
            'mood': 'good',
            'energy': 'high',
            'sleep': 'invalid'
        })

        assert response.status_code == 400
        assert 'sleep' in response.get_json()['error']


class TestDailyStatusValues:
    """تست مقادیر معتبر"""

    def test_all_valid_moods(self, logged_in_client):
        """همه‌ی mood های معتبر"""
        for mood in ['good', 'neutral', 'bad']:
            response = logged_in_client.post('/api/daily-status', json={
                'mood': mood,
                'energy': 'high',
                'sleep': 'great'
            })
            assert response.status_code == 200

    def test_all_valid_energies(self, logged_in_client):
        """همه‌ی energy های معتبر"""
        for energy in ['high', 'medium', 'low']:
            response = logged_in_client.post('/api/daily-status', json={
                'mood': 'good',
                'energy': energy,
                'sleep': 'great'
            })
            assert response.status_code == 200

    def test_all_valid_sleeps(self, logged_in_client):
        """همه‌ی sleep های معتبر"""
        for sleep in ['great', 'good', 'bad']:
            response = logged_in_client.post('/api/daily-status', json={
                'mood': 'good',
                'energy': 'high',
                'sleep': sleep
            })
            assert response.status_code == 200

    def test_only_mood(self, logged_in_client):
        """فقط mood (بقیه اختیاری)"""
        response = logged_in_client.post('/api/daily-status', json={
            'mood': 'good'
        })
        assert response.status_code == 200

    def test_empty_body(self, logged_in_client):
        """بدنه‌ی خالی رد بشه"""
        response = logged_in_client.post('/api/daily-status', json={})
        assert response.status_code == 400


class TestDailyStatusUpdate:
    """تست به‌روزرسانی"""

    def test_update_same_day(self, logged_in_client):
        """دو بار توی همون روز → به‌روزرسانی"""
        today = datetime.now().isoformat().split('T')[0]
        # ثبت اول
        logged_in_client.post('/api/daily-status', json={
            'mood': 'good',
            'energy': 'high',
            'sleep': 'great'
        })

        # ثبت دوم (همون روز)
        logged_in_client.post('/api/daily-status', json={
            'mood': 'bad',
            'energy': 'low',
            'sleep': 'bad'
        })

        # چک
        response = logged_in_client.get('/api/daily-status')
        data = response.get_json()

        assert today in data
        assert data[today]['mood'] == 'bad'
        assert data[today]['energy'] == 'low'
        assert data[today]['sleep'] == 'bad'