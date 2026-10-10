# ============================================================
# تست چت‌بات
# ============================================================

import pytest


class TestChat:
    """تست چت‌بات"""

    def test_chat_endpoint_exists(self, logged_in_client):
        """endpoint چت باید کار کنه"""
        response = logged_in_client.post('/api/chat', json={
            'message': 'سلام'
        })
        assert response.status_code == 200

    def test_chat_empty_message(self, logged_in_client):
        """پیام خالی خطا بده"""
        response = logged_in_client.post('/api/chat', json={
            'message': ''
        })
        assert response.status_code == 400

    def test_chat_no_message_field(self, logged_in_client):
        """نبود فیلد message خطا بده"""
        response = logged_in_client.post('/api/chat', json={})
        assert response.status_code == 400

    def test_chat_response_structure(self, logged_in_client):
        """ساختار پاسخ چت"""
        response = logged_in_client.post('/api/chat', json={
            'message': 'سلام، حالم خوب نیست'
        })

        data = response.get_json()
        assert 'response' in data
        assert 'source' in data
        assert len(data['response']) > 0

    def test_chat_source_valid(self, logged_in_client):
        """source باید معتبر باشه"""
        response = logged_in_client.post('/api/chat', json={
            'message': 'سلام'
        })

        data = response.get_json()
        assert data['source'] in ['llm', 'fallback', 'error']

    def test_chat_various_messages(self, logged_in_client):
        """پیام‌های مختلف"""
        messages = [
            'سلام',
            'امروز حالم بده',
            'نمی‌تونم بخوابم',
            'احساس تنهایی می‌کنم',
            'مرسی از کمک',
            'خداحافظ'
        ]

        for msg in messages:
            response = logged_in_client.post('/api/chat', json={
                'message': msg
            })
            assert response.status_code == 200
            data = response.get_json()
            assert len(data['response']) > 0