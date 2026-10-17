# ============================================================
# سرویس اصلی LLM
# ============================================================

from .providers import OpenAIProvider,GeminiProvider

try:
    from .providers import LocalProvider
except ImportError:
    LocalProvider = None

from config import get_config
from utils.logger import logger

class LLMService:
    """سرویس LLM — Interface ثابت"""

    def __init__(self):
        self.config = get_config()
        self.enabled = self.config.LLM_ENABLED
        self.provider = self._create_provider()

    def _create_provider(self):
        if not self.enabled:
            logger.warning("⚠️ LLM غیرفعاله")
            return None

        provider_name = self.config.LLM_PROVIDER

        if provider_name == 'openai':
            return OpenAIProvider()
        elif provider_name == 'gemini':
            return GeminiProvider()
        elif provider_name == 'local':
            if LocalProvider is None:
                logger.error("❌ LocalProvider در دسترس نیست")
                return None
            return LocalProvider()
        else:
            logger.error(f"❌ Provider ناشناخته: {provider_name}")
            return None

    def analyze_text(self, text_answers):
        if not self.provider or not self.provider.is_available():
            from .parser import get_fallback_analysis
            return get_fallback_analysis()
        return self.provider.analyze_text(text_answers)

    def chat(self, message):
        if not self.provider or not self.provider.is_available():
            return None
        return self.provider.chat(message)

    def weekly_summary(self, data):
        if not self.provider or not self.provider.is_available():
            return None
        return self.provider.weekly_summary(data)

    def is_available(self):
        return self.provider is not None and self.provider.is_available()


_llm_service = None

def get_llm_service():
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
