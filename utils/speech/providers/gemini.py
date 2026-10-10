# ============================================================
# Gemini Speech Provider — استفاده از Gemini برای صوت
# ============================================================

import google.generativeai as genai
from .base import SpeechProvider
from config import get_config


class GeminiSpeechProvider(SpeechProvider):
    """تبدیل صوت به متن با Gemini"""

    def __init__(self):
        self.config = get_config()
        self.api_key = self.config.GEMINI_API_KEY

        if not self.api_key:
            print("⚠️ GEMINI_API_KEY تنظیم نشده")
            self.model = None
            return

        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            print("✅ Gemini Speech Provider آماده")
        except Exception as e:
            print(f"❌ خطا در راه‌اندازی: {e}")
            self.model = None

    def is_available(self):
        return self.model is not None

    def transcribe(self, audio_path):
        """تبدیل صوت به متن"""
        if not self.is_available():
            return None

        try:
            with open(audio_path, 'rb') as f:
                audio_data = f.read()

            response = self.model.generate_content([
                "این فایل صوتی رو به متن فارسی تبدیل کن. فقط متن رو بده.",
                {"mime_type": "audio/wav", "data": audio_data}
            ])

            return response.text.strip()

        except Exception as e:
            print(f"❌ خطا در transcribe: {e}")
            return None

    def analyze_emotion(self, audio_path):
        """تحلیل احساسات از صوت"""
        if not self.is_available():
            return None

        try:
            with open(audio_path, 'rb') as f:
                audio_data = f.read()

            response = self.model.generate_content([
                "احساسات این فایل صوتی رو تحلیل کن و فقط یکی از این کلمات رو بگو: غم، خشم، ترس، شادی، اضطراب، خنثی",
                {"mime_type": "audio/wav", "data": audio_data}
            ])

            return response.text.strip()

        except Exception as e:
            print(f"❌ خطا در analyze_emotion: {e}")
            return None