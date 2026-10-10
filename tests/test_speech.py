# ============================================================
# تست Speech (Mock)
# ============================================================

import pytest
from unittest.mock import patch


class TestSpeechService:
    """تست سرویس Speech"""

    def test_singleton(self):
        """سرویس singleton"""
        from utils.speech.service import get_speech_service

        s1 = get_speech_service()
        s2 = get_speech_service()
        assert s1 is s2

    def test_has_methods(self):
        """متدها"""
        from utils.speech.service import get_speech_service

        s = get_speech_service()
        assert hasattr(s, 'transcribe')
        assert hasattr(s, 'is_available')

    def test_transcribe_with_mock(self):
        """transcribe با mock"""
        from utils.speech.service import get_speech_service

        s = get_speech_service()

        if s.provider:
            with patch.object(s.provider, 'transcribe', return_value='تست'):
                result = s.transcribe('dummy.wav')
                assert result == 'تست'

    def test_transcribe_unavailable(self):
        """transcribe بدون Provider"""
        from utils.speech.service import get_speech_service

        s = get_speech_service()

        if s.provider:
            with patch.object(s.provider, 'is_available', return_value=False):
                result = s.transcribe('dummy.wav')
                assert result is None


class TestAvalAIProvider:
    """تست AvalAI Speech"""

    def test_init(self):
        """مقداردهی"""
        from utils.speech.providers.avalai import AvalAISpeechProvider

        p = AvalAISpeechProvider()
        assert p.config is not None
        assert p.api_key is not None
        assert p.base_url is not None

    def test_has_methods(self):
        """متدها"""
        from utils.speech.providers.avalai import AvalAISpeechProvider

        p = AvalAISpeechProvider()
        assert hasattr(p, 'transcribe')
        assert hasattr(p, 'analyze_emotion')
        assert hasattr(p, 'is_available')


class TestSpeechNotLoggedIn:
    """تست Speech بدون لاگین"""

    def test_audio_upload_no_auth(self, client):
        """آپلود صوت بدون لاگین"""
        response = client.post('/api/upload-audio')
        assert response.status_code in [400, 401, 403]