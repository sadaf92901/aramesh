
# ============================================================
# تست تاریخچه
# ============================================================

import pytest


class TestHistory:
    """تست تاریخچه"""

    def test_timeline_empty(self, logged_in_client):
        response = logged_in_client.get('/api/history/timeline')
        assert response.status_code == 200
        data = response.get_json()
        assert 'items' in data

    def test_timeline_not_logged_in(self, client):
        response = client.get('/api/history/timeline')
        assert response.status_code == 401

    def test_stats(self, logged_in_client):
        response = logged_in_client.get('/api/history/stats')
        assert response.status_code == 200
        data = response.get_json()
        assert 'total_diagnoses' in data
        assert 'total_notes' in data

    def test_weekly_summary(self, logged_in_client):
        response = logged_in_client.get('/api/history/weekly-summary')
        assert response.status_code == 200
        data = response.get_json()
        assert 'stats' in data
        assert 'summary' in data

    def test_compare(self, logged_in_client):
        response = logged_in_client.get('/api/history/compare')
        assert response.status_code == 200
        data = response.get_json()
        assert 'has_comparison' in data