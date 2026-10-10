# ============================================================
# تست برنامه هفتگی
# ============================================================

import pytest


class TestWeeklyPlan:
    """تست برنامه هفتگی"""

    def test_get_plan_empty(self, logged_in_client):
        """برنامه اول خالیه"""
        response = logged_in_client.get('/api/weekly-plan')
        assert response.status_code == 200

        data = response.get_json()
        assert 'plan' in data

    def test_get_plan_not_logged_in(self, client):
        """بدون لاگین خطا بده"""
        response = client.get('/api/weekly-plan')
        assert response.status_code == 401

    def test_generate_plan_without_diagnosis(self, logged_in_client):
        """بدون تشخیص، خطا بده"""
        response = logged_in_client.post('/api/weekly-plan/generate')
        assert response.status_code == 400

    def test_generate_plan_not_logged_in(self, client):
        """بدون لاگین خطا بده"""
        response = client.post('/api/weekly-plan/generate')
        assert response.status_code == 401


class TestPlanGeneration:
    """تست ساخت برنامه"""

    def test_full_flow(self, logged_in_client):
        """تست کامل: تشخیص → برنامه"""
        # ===== تشخیص =====
        logged_in_client.post('/api/predict', data={
            'mc_answers[]': ['متوسط'] * 20,
            'text_answers[]': [
                'امروز حالم خوب بود',
                'ورزش می‌کردم',
                'امیدوارم'
            ]
        })

        # ===== برنامه =====
        response = logged_in_client.post('/api/weekly-plan/generate')
        assert response.status_code == 200

        data = response.get_json()
        assert data.get('success') is True
        assert 'plan' in data

    def test_plan_structure(self, logged_in_client):
        """برنامه ۷ روز داشته باشه"""
        # تشخیص
        logged_in_client.post('/api/predict', data={
            'mc_answers[]': ['متوسط'] * 20,
            'text_answers[]': ['تست'] * 3
        })

        # برنامه
        logged_in_client.post('/api/weekly-plan/generate')

        response = logged_in_client.get('/api/weekly-plan')
        data = response.get_json()

        if data.get('plan'):
            plan_data = data['plan'].get('plan_data', {})
            assert 'days' in plan_data
            assert len(plan_data['days']) == 7

            # هر روز باید activities داشته باشه
            for day in plan_data['days']:
                assert 'day' in day
                assert 'activities' in day
                assert len(day['activities']) > 0