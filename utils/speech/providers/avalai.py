# ============================================================
# AvalAI Speech Provider — تبدیل صوت به متن با AvalAI
# ============================================================

from .base import SpeechProvider
from config import get_config


class AvalAISpeechProvider(SpeechProvider):
    """Provider تبدیل صوت به متن با AvalAI"""

    def __init__(self):
        self.config = get_config()
        self.api_key = self.config.OPENAI_API_KEY
        self.base_url = self.config.OPENAI_BASE_URL
        self.model_name = self.config.OPENAI_TRANSCRIBE_MODEL

        if not self.api_key:
            print("⚠️ OPENAI_API_KEY تنظیم نشده")
            self.client = None
            return

        try:
            from openai import OpenAI

            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )

            print(f"✅ AvalAI Speech Provider آماده")
            print(f"   Model: {self.model_name}")

        except ImportError:
            print("❌ openai نصب نیست")
            self.client = None
        except Exception as e:
            print(f"❌ خطا در راه‌اندازی AvalAI Speech: {e}")
            self.client = None

    def is_available(self):
        return self.client is not None

    # ============================================================
    # تبدیل صوت به متن
    # ============================================================
    def transcribe(self, audio_path):
        if not self.is_available():
            return None

        try:
            with open(audio_path, 'rb') as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model=self.model_name,
                    file=audio_file,
                    language="fa",
                    response_format="text"
                )

            # ===== اگه transcript رشته بود =====
            if isinstance(transcript, str):
                # ===== اگه JSON بود، پارس کن =====
                try:
                    import json
                    data = json.loads(transcript)
                    if isinstance(data, dict) and 'text' in data:
                        return data['text'].strip()
                except (json.JSONDecodeError, ValueError):
                    pass

                return transcript.strip()

            # ===== اگه object بود =====
            if hasattr(transcript, 'text'):
                return transcript.text.strip()

            return str(transcript).strip() if transcript else None

        except Exception as e:
            print(f"❌ خطا در transcribe: {e}")
            return None
    # ============================================================
    # تحلیل احساسات (فقط متن برمی‌گردونه)
    # ============================================================

    def analyze_emotion(self, audio_path):
        """
        AvalAI Speech فقط متن برمی‌گردونه.
        تحلیل احساسات توسط LLM انجام میشه.
        """
        return self.transcribe(audio_path)