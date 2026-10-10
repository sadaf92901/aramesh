# ============================================================
# تست Health Check
# ============================================================

import pytest


class TestHealthcheck:
    """تست healthz endpoint"""

    def test_healthz_returns_200(self, client):
        """باید 200 برگردونه"""
        response = client.get('/healthz')
        assert response.status_code == 200

    def test_healthz_json(self, client):
        """باید JSON معتبر برگردونه"""
        response = client.get('/healthz')
        data = response.get_json()

        assert data is not None
        assert 'status' in data
        assert 'version' in data
        assert 'checks' in data

    def test_healthz_status_ok(self, client):
        """status = ok"""
        response = client.get('/healthz')
        data = response.get_json()

        assert data['status'] == 'ok'

    def test_healthz_database_check(self, client):
        """دیتابیس چک بشه"""
        response = client.get('/healthz')
        data = response.get_json()

        assert 'database' in data['checks']
        assert data['checks']['database'] == 'ok'

    def test_healthz_version(self, client):
        """نسخه درست"""
        response = client.get('/healthz')
        data = response.get_json()

        assert data['version'] == '1.1.0'

    def test_healthz_response_time(self, client):
        """زمان پاسخ محاسبه بشه"""
        response = client.get('/healthz')
        data = response.get_json()

        assert 'response_time_ms' in data
        assert data['response_time_ms'] >= 0

    def test_healthz_service_name(self, client):
        """اسم سرویس"""
        response = client.get('/healthz')
        data = response.get_json()

        assert data['service'] == 'aramesh'


class TestHealthzReady:
    """تست readiness"""

    def test_ready_returns_200(self, client):
        response = client.get('/healthz/ready')
        assert response.status_code == 200

    def test_ready_json(self, client):
        response = client.get('/healthz/ready')
        data = response.get_json()

        assert data['ready'] is True


class TestHealthzLive:
    """تست liveness"""

    def test_live_returns_200(self, client):
        response = client.get('/healthz/live')
        assert response.status_code == 200

    def test_live_json(self, client):
        response = client.get('/healthz/live')
        data = response.get_json()

        assert data['alive'] is True