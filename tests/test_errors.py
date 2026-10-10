# ============================================================
# تست Error Handlers
# ============================================================

import pytest


class TestErrorHandlers:
    """تست مدیریت خطا"""

    def test_404_api(self, client):
        """API 404 → JSON"""
        response = client.get('/api/not-exists')
        assert response.status_code == 404

        data = response.get_json()
        assert 'error' in data

    def test_404_page(self, client):
        """صفحه 404 → HTML"""
        response = client.get('/page-not-exists')
        assert response.status_code == 404

    def test_405_method_not_allowed(self, client):
        """متد غیرمجاز"""
        response = client.get('/api/register')
        assert response.status_code == 405

    def test_app_error_class(self):
        """کلاس AppError"""
        from utils.errors import AppError

        error = AppError('تست')
        assert error.message == 'تست'
        assert error.to_dict()['error'] == 'تست'
        assert error.to_dict()['status'] == 'error'

    def test_validation_error(self):
        """ValidationError"""
        from utils.errors import ValidationError

        error = ValidationError()
        assert error.status_code == 400

    def test_auth_error(self):
        """AuthError"""
        from utils.errors import AuthError

        error = AuthError()
        assert error.status_code == 401

    def test_not_found_error(self):
        """NotFoundError"""
        from utils.errors import NotFoundError

        error = NotFoundError()
        assert error.status_code == 404