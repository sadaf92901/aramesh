# ============================================================
# Local Speech Provider — استفاده از Whisper
# ============================================================

import os
from .base import SpeechProvider
from config import get_config


class LocalSpeechProvider(SpeechProvider):
    """Provider بر اساس Whisper (محلی)"""

    def __init__(self):
        self.config = get_config()
        self.model = None
        self._loaded = False

        if not self.config.SPEECH_ENABLED:
            print("⚠️ LocalSpeechProvider غیرفعاله")
            return

        try:
            self._load_model()
        except Exception as e:
            print(f"❌ خطا در لود Whisper: {e}")
            self.model = None

    def _load_model(self):
        """لود مدل Whisper"""
        import whisper

        model_size = self.config.WHISPER_MODEL

        print(f"🔄 در حال لود Whisper {model_size}...")
        print("   (این ممکنه چند دقیقه طول بکشه)")

        self.model = whisper.load_model(model_size)
        self._loaded = True

        print(f"✅ Whisper لود شد: {model_size}")

    def is_available(self):
        return self._loaded and self.model is not None

    # ============================================================
    # تبدیل صوت به متن
    # ============================================================

    def transcribe(self, audio_path):
        """تبدیل صوت به متن"""
        if not self.is_available():
            return None

        if not os.path.exists(audio_path):
            print(f"❌ فایل پیدا نشد: {audio_path}")
            return None

        try:
            result = self.model.transcribe(
                audio_path,
                language='fa',           # فارسی
                task='transcribe',
                fp16=False
            )

            text = result.get('text', '').strip()
            return text if text else None

        except Exception as e:
            print(f"❌ خطا در transcribe: {e}")
            return None

    # ============================================================
    # تحلیل احساسات از صوت (Whisper فقط متن میده)
    # ============================================================

    def analyze_emotion(self, audio_path):
        """
        Whisper خودش SER نداره.
        پس فقط متن رو برمی‌گردونیم و LLM تحلیل می‌کنه.
        """
        return self.transcribe(audio_path)