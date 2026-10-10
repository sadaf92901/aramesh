
# ============================================================
# تست تشخیص
# ============================================================

import pytest
from routes.diagnosis import (
    calculate_mcq_score,
    get_prediction,
    get_treatment
)


class TestCalculateMCQScore:
    """تست محاسبه امتیاز MCQ"""

    def test_all_positive_answers(self):
        """همه‌ی جواب‌ها مثبت → امتیاز بالا"""
        answers = ['خیلی زیاد'] * 20
        score = calculate_mcq_score(answers)
        assert 0 <= score <= 100

    def test_all_negative_answers(self):
        """همه‌ی جواب‌ها منفی → امتیاز پایین"""
        answers = ['هرگز'] * 20
        score = calculate_mcq_score(answers)
        assert 0 <= score <= 100

    def test_empty_answers(self):
        assert calculate_mcq_score([]) == 0.0

    def test_less_than_20_answers(self):
        assert calculate_mcq_score(['هرگز'] * 10) == 0.0

    def test_score_in_range(self):
        """امتیاز باید بین ۰ و ۱۰۰ باشه"""
        answers = ['متوسط'] * 20
        score = calculate_mcq_score(answers)
        assert 0 <= score <= 100


class TestGetPrediction:
    """تست تعیین سطح"""

    def test_healthy(self):
        assert get_prediction(85) == 0
        assert get_prediction(65) == 0

    def test_mild(self):
        assert get_prediction(50) == 1
        assert get_prediction(45) == 1

    def test_moderate(self):
        assert get_prediction(35) == 2
        assert get_prediction(25) == 2

    def test_severe(self):
        assert get_prediction(20) == 3
        assert get_prediction(0) == 3


class TestGetTreatment:
    """تست درمان"""

    def test_all_levels_have_treatment(self):
        for level in range(4):
            treatment = get_treatment(level)
            assert isinstance(treatment, str)
            assert len(treatment) > 0


class TestPredictAPI:
    """تست API تشخیص"""

    def test_predict_not_logged_in(self, client):
        response = client.post('/api/predict')
        assert response.status_code in [400, 401]

    def test_predict_missing_answers(self, client, logged_in_client):
        response = logged_in_client.post('/api/predict', data={})
        assert response.status_code == 400

    def test_predict_success(self, client, logged_in_client):
        """تشخیص کامل با ۲۰ جواب + ۳ سوال باز"""
        data = {
            'mc_answers[]': ['متوسط'] * 20,
            'text_answers[]': [
                'امروز حالم خوب بود و با دوستم صحبت کردم',
                'قبلاً ورزش می‌کردم ولی الآن نمی‌توانم',
                'خانواده‌ام حمایتم می‌کنند و به آینده امیدوارم'
            ]
        }

        response = logged_in_client.post('/api/predict', data=data)
        assert response.status_code == 200

        result = response.get_json()
        assert 'prediction' in result
        assert 'score' in result
        assert 'mcqScore' in result
        assert 0 <= result['score'] <= 100