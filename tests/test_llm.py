# ============================================================
# تست LLM (Mock)
# ============================================================

import pytest
from unittest.mock import patch


class TestLLMService:
    """تست سرویس LLM"""

    def test_singleton(self):
        """سرویس باید singleton باشه"""
        from utils.llm.service import get_llm_service

        s1 = get_llm_service()
        s2 = get_llm_service()
        assert s1 is s2

    def test_has_methods(self):
        """متدهای موردنیاز"""
        from utils.llm.service import get_llm_service

        s = get_llm_service()
        assert hasattr(s, 'analyze_text')
        assert hasattr(s, 'chat')
        assert hasattr(s, 'weekly_summary')
        assert hasattr(s, 'is_available')

    def test_analyze_with_mock(self):
        """تست analyze_text با mock"""
        from utils.llm.service import get_llm_service

        s = get_llm_service()

        if s.provider:
            with patch.object(s.provider, 'analyze_text', return_value={
                'final_score': 75,
                'status': 'موفق',
                'dominant_emotion': 'خوشحالی',
                'key_concerns': [],
                'treatment': 'خوب'
            }):
                result = s.analyze_text(['تست'] * 3)
                assert result['final_score'] == 75

    def test_fallback_when_unavailable(self):
        """fallback اگه LLM نباشه"""
        from utils.llm.service import get_llm_service

        s = get_llm_service()

        if s.provider:
            with patch.object(s.provider, 'is_available', return_value=False):
                result = s.analyze_text(['تست'])
                assert result is None


class TestOpenAIProvider:
    """تست OpenAIProvider"""

    def test_init(self):
        """مقداردهی"""
        from utils.llm.providers.openai import OpenAIProvider

        p = OpenAIProvider()
        assert p.config is not None
        assert p.api_key is not None
        assert p.base_url is not None
        assert p.model_name is not None

    def test_has_methods(self):
        """متدها"""
        from utils.llm.providers.openai import OpenAIProvider

        p = OpenAIProvider()
        assert hasattr(p, 'analyze_text')
        assert hasattr(p, 'chat')
        assert hasattr(p, 'weekly_summary')
        assert hasattr(p, 'is_available')


class TestLLMProviders:
    """تست Providerها"""

    def test_provider_factory(self):
        """Provider بر اساس config"""
        from config import get_config
        from utils.llm.service import get_llm_service

        c = get_config()
        s = get_llm_service()

        if c.LLM_ENABLED:
            assert s.provider is not None