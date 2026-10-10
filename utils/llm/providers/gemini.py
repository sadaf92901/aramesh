# ============================================================
# Gemini Provider — استفاده از Google Gemini API
# ============================================================

import google.generativeai as genai
from .base import LLMProvider
from ..prompts import PROMPTS
from ..parser import parse_json_response, get_fallback_analysis
from config import get_config


class GeminiProvider(LLMProvider):
    """Provider بر اساس Google Gemini API"""

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
            print("✅ Gemini Provider آماده")
        except Exception as e:
            print(f"❌ خطا در راه‌اندازی Gemini: {e}")
            self.model = None

    def is_available(self):
        return self.model is not None

    # ============================================================
    # تحلیل متن
    # ============================================================

    def analyze_text(self, text_answers):
        if not self.is_available():
            return get_fallback_analysis()

        try:
            prompt = PROMPTS['analysis'].format(
                answer1=text_answers[0] if len(text_answers) > 0 else '',
                answer2=text_answers[1] if len(text_answers) > 1 else '',
                answer3=text_answers[2] if len(text_answers) > 2 else '',
            )

            response = self.model.generate_content(prompt)
            result = parse_json_response(response.text)

            if not result:
                return get_fallback_analysis()

            return {
                'dominant_emotion': result.get('dominant_emotion', 'نامشخص'),
                'emotion_intensity': result.get('emotion_intensity', 5),
                'depression_score': result.get('depression_score', 0),
                'anxiety_score': result.get('anxiety_score', 0),
                'protective_factors_score': result.get('protective_factors_score', 0),
                'risk_factors_score': result.get('risk_factors_score', 0),
                'final_score': result.get('final_score', 50),
                'key_concerns': result.get('key_concerns', []),
                'treatment': result.get('treatment', ''),
                'status': 'موفق'
            }

        except Exception as e:
            print(f"❌ خطا در Gemini analyze: {e}")
            return get_fallback_analysis()

    # ============================================================
    # چت
    # ============================================================

    def chat(self, message):
        if not self.is_available():
            return None

        try:
            prompt = PROMPTS['chat'].format(message=message)
            response = self.model.generate_content(prompt)
            return response.text.strip()

        except Exception as e:
            print(f"❌ خطا در Gemini chat: {e}")
            return None

    # ============================================================
    # جمع‌بندی هفتگی
    # ============================================================

    def weekly_summary(self, data):
        if not self.is_available():
            return None

        try:
            prompt = PROMPTS['weekly_summary'].format(**data)
            response = self.model.generate_content(prompt)
            return response.text.strip()

        except Exception as e:
            print(f"❌ خطا در Gemini summary: {e}")
            return None