# ============================================================
# تست صفحات
# ============================================================

import pytest


class TestPublicPages:
    """صفحات عمومی"""

    def test_login_page(self, client):
        """صفحه لاگین"""
        response = client.get('/')
        assert response.status_code == 200

    def test_about_page(self, client):
        """صفحه About"""
        response = client.get('/about')
        assert response.status_code == 200

    def test_privacy_page(self, client):
        """صفحه Privacy"""
        response = client.get('/privacy')
        assert response.status_code == 200

    def test_terms_page(self, client):
        """صفحه Terms"""
        response = client.get('/terms')
        assert response.status_code == 200

    def test_offline_page(self, client):
        """صفحه Offline"""
        response = client.get('/offline')
        assert response.status_code == 200


class TestProtectedPages:
    """صفحات محافظت‌شده"""

    def test_profile_redirects_anonymous(self, client):
        """بدون لاگین → redirect"""
        response = client.get('/profile')
        assert response.status_code in [302, 301]

    def test_journal_redirects_anonymous(self, client):
        """بدون لاگین → redirect"""
        response = client.get('/journal')
        assert response.status_code in [302, 301]

    def test_profile_logged_in(self, logged_in_client):
        """با لاگین → 200"""
        response = logged_in_client.get('/profile')
        assert response.status_code == 200

    def test_journal_logged_in(self, logged_in_client):
        """با لاگین → 200"""
        response = logged_in_client.get('/journal')
        assert response.status_code == 200

    def test_history_logged_in(self, logged_in_client):
        """با لاگین → 200"""
        response = logged_in_client.get('/history')
        assert response.status_code == 200

    def test_breathing_logged_in(self, logged_in_client):
        """با لاگین → 200"""
        response = logged_in_client.get('/breathing')
        assert response.status_code == 200

    def test_meditation_logged_in(self, logged_in_client):
        """با لاگین → 200"""
        response = logged_in_client.get('/meditation')
        assert response.status_code == 200