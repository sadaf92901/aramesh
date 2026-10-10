
# ============================================================
# تست روزنگار
# ============================================================

import pytest


class TestNotes:
    """تست یاداشت‌ها"""

    def test_create_note(self, logged_in_client):
        response = logged_in_client.post('/api/notes', json={
            'title': 'امروز',
            'content': 'امروز روز خوبی بود',
            'mood': 'happy',
            'tags': ['خانواده', 'دوستان']
        })
        assert response.status_code == 200
        assert response.get_json()['success'] is True

    def test_create_note_empty_content(self, logged_in_client):
        response = logged_in_client.post('/api/notes', json={
            'content': '',
            'mood': 'happy'
        })
        assert response.status_code == 400

    def test_get_notes(self, logged_in_client):
        logged_in_client.post('/api/notes', json={
            'content': 'تست',
            'mood': 'happy'
        })

        response = logged_in_client.get('/api/notes')
        assert response.status_code == 200
        notes = response.get_json()
        assert isinstance(notes, list)
        assert len(notes) >= 1

    def test_get_notes_not_logged_in(self, client):
        response = client.get('/api/notes')
        assert response.status_code == 401

    def test_update_note(self, logged_in_client):
        # ساخت
        create = logged_in_client.post('/api/notes', json={
            'content': 'متن اولیه',
            'mood': 'happy'
        })
        note_id = create.get_json()['id']

        # آپدیت
        response = logged_in_client.put(f'/api/notes/{note_id}', json={
            'content': 'متن جدید',
            'mood': 'calm'
        })
        assert response.status_code == 200

    def test_delete_note(self, logged_in_client):
        create = logged_in_client.post('/api/notes', json={
            'content': 'برای حذف',
            'mood': 'happy'
        })
        note_id = create.get_json()['id']

        response = logged_in_client.delete(f'/api/notes/{note_id}')
        assert response.status_code == 200
        assert response.get_json()['success'] is True

    def test_notes_stats(self, logged_in_client):
        response = logged_in_client.get('/api/notes/stats')
        assert response.status_code == 200
        data = response.get_json()
        assert 'total' in data
        assert 'streak' in data
        assert 'this_week' in data