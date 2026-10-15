# ============================================================
# سرویس Speech
# ============================================================

from config import get_config


class SpeechService:
    """سرویس Speech — Interface ثابت"""

    def __init__(self):
        self.config = get_config()
        self.enabled = self.config.SPEECH_ENABLED
        self.provider = self._create_provider()

    def _create_provider(self):
        if not self.enabled:
            print("⚠️ Speech غیرفعاله")
            return None

        provider_name = self.config.SPEECH_PROVIDER

        if provider_name == 'avalai':
            from .providers.avalai import AvalAISpeechProvider
            return AvalAISpeechProvider()

        elif provider_name == 'gemini':
            from .providers.gemini import GeminiSpeechProvider
            return GeminiSpeechProvider()

        elif provider_name == 'local':
            from .providers.local import LocalSpeechProvider
            return LocalSpeechProvider()

        else:
            print(f"❌ Provider ناشناخته: {provider_name}")
            return None

    def transcribe(self, audio_path):
        if not self.provider or not self.provider.is_available():
            return None
        return self.provider.transcribe(audio_path)

    def analyze_emotion(self, audio_path):
        if not self.provider or not self.provider.is_available():
            return None
        return self.provider.analyze_emotion(audio_path)

    def is_available(self):
        return self.provider is not None and self.provider.is_available()


_speech_service = None


def get_speech_service():
    global _speech_service
    if _speech_service is None:
        _speech_service = SpeechService()
    return _speech_service
