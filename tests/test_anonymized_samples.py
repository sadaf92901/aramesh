# ============================================================
# تست ذخیره‌ی نمونه‌ی ناشناس
# ============================================================

import pytest
import os
import json
from datetime import datetime
from config import get_config


class TestAnonymizedSamples:
    """تست ذخیره‌ی نمونه‌ی ناشناس"""

    def test_function_exists(self):
        """تابع save_anonymized_sample وجود داره"""
        from routes.diagnosis import save_anonymized_sample
        assert callable(save_anonymized_sample)

    def test_sample_created_after_diagnosis(self, logged_in_client):
        """بعد از تشخیص، نمونه‌ی ناشناس ذخیره می‌شه"""
        config = get_config()
        samples_file = os.path.join(config.BASE_DIR, 'data', 'training_samples.jsonl')

        # ===== تعداد خطوط قبل =====
        lines_before = 0
        if os.path.exists(samples_file):
            with open(samples_file, 'r', encoding='utf-8') as f:
                lines_before = len(f.readlines())

        # ===== تشخیص بده =====
        response = logged_in_client.post('/api/predict', data={
            'mc_answers[]': ['متوسط'] * 20,
            'text_answers[]': ['تست اول', 'تست دوم', 'تست سوم']
        })

        assert response.status_code == 200

        # ===== تعداد خطوط بعد =====
        lines_after = 0
        if os.path.exists(samples_file):
            with open(samples_file, 'r', encoding='utf-8') as f:
                lines_after = len(f.readlines())

        # باید یه خط اضافه شده باشه
        assert lines_after > lines_before

    def test_sample_no_user_id(self, logged_in_client):
        """نمونه‌ی ذخیره‌شده user_id نداره"""
        config = get_config()
        samples_file = os.path.join(config.BASE_DIR, 'data', 'training_samples.jsonl')

        # ===== تشخیص =====
        logged_in_client.post('/api/predict', data={
            'mc_answers[]': ['متوسط'] * 20,
            'text_answers[]': ['تست'] * 3
        })

        # ===== آخرین خط رو بخون =====
        if not os.path.exists(samples_file):
            pytest.skip('فایل samples نیست')

        with open(samples_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        if not lines:
            pytest.skip('فایل خالیه')

        last_sample = json.loads(lines[-1])

        # چک کن user_id نباشه
        assert 'user_id' not in last_sample
        assert 'audio_files' not in last_sample

        # چک کن این فیلدها باشن
        assert 'timestamp' in last_sample
        assert 'mcq_answers' in last_sample
        assert 'text_answers' in last_sample
        assert 'final_score' in last_sample
        assert 'prediction' in last_sample

    def test_sample_jsonl_format(self, logged_in_client):
        """فرمت JSONL درست باشه (هر خط یه JSON)"""
        config = get_config()
        samples_file = os.path.join(config.BASE_DIR, 'data', 'training_samples.jsonl')

        if not os.path.exists(samples_file):
            pytest.skip('فایل samples نیست')

        with open(samples_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                # هر خط باید JSON معتبر باشه
                json.loads(line)