# ============================================================
# Gemini Provider — استفاده از Google Gemini API
# (پکیج جدید: google-genai)
# ============================================================

from .base import LLMProvider
from ..prompts import PROMPTS
from ..parser import parse_json_response, get_fallback_analysis
from config import get_config


class GeminiProvider(LLMProvider):
    """Provider بر اساس Google Gemini API"""

    def __init__(self):
        self.config = get_config()
        self.api_key = self.config.GEMINI_API_KEY
        self.model_name = self.config.GEMINI_MODEL

        if not self.api_key:
            print("⚠️ GEMINI_API_KEY تنظیم نشده")
            self.client = None
            return

        try:
            from google import genai

            self.client = genai.Client(api_key=self.api_key)

            print(f"✅ Gemini Provider آماده")
            print(f"   Model: {self.model_name}")

        except ImportError:
            print("❌ google-genai نصب نیست")
            print("   نصب: pip install google-genai")
            self.client = None
        except Exception as e:
            print(f"❌ خطا در راه‌اندازی Gemini: {e}")
            self.client = None

    def is_available(self):
        return self.client is not None

    # ============================================================
    # تولید متن پایه
    # ============================================================

    def _generate(self, prompt, json_mode=False):
        """تولید متن با Gemini"""
        if not self.is_available():
            return None

        try:
            config = {}
            if json_mode:
                config['response_mime_type'] = 'application/json'

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config if config else None
            )

            return response.text.strip() if response.text else None

        except Exception as e:
            print(f"❌ خطا در Gemini generate: {e}")
            return None

    # ============================================================
    # تحلیل متن
    # ============================================================

    def analyze_text(self, text_answers):
        if not self.is_available():
            return get_fallback_analysis()

        try:
            # ===== RAG context =====
            rag_context = ""
            try:
                from utils.rag.service import get_rag_service
                rag = get_rag_service()

                if rag.is_ready():
                    combined_text = " ".join([t for t in text_answers if t and t.strip()])
                    if combined_text:
                        rag_context = rag.get_context(combined_text, top_k=3)
            except Exception as e:
                print(f"⚠️ خطا در RAG: {e}")

            # ===== ساخت پرامپت =====
            base_prompt = PROMPTS['analysis'].format(
                answer1=text_answers[0] if len(text_answers) > 0 else '',
                answer2=text_answers[1] if len(text_answers) > 1 else '',
                answer3=text_answers[2] if len(text_answers) > 2 else '',
            )

            if rag_context:
                prompt = f"""نمونه‌های مشابه از دیتاست روانشناسی:

{rag_context}

---

حالا بر اساس نمونه‌های بالا، این پاسخ‌های کاربر رو تحلیل کن:

{base_prompt}"""
            else:
                prompt = base_prompt

            # ===== فراخوانی =====
            response_text = self._generate(prompt, json_mode=True)

            if not response_text:
                return get_fallback_analysis()

            result = parse_json_response(response_text)

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
            # ===== RAG =====
            rag_context = ""
            try:
                from utils.rag.service import get_rag_service
                rag = get_rag_service()

                if rag.is_ready():
                    rag_context = rag.get_context(message, top_k=2)
            except Exception as e:
                print(f"⚠️ خطا در RAG چت: {e}")

            base_prompt = PROMPTS['chat'].format(message=message)

            if rag_context:
                prompt = f"""نمونه‌های مشابه از دیتاست روانشناسی:

{rag_context}

---

{base_prompt}"""
            else:
                prompt = base_prompt

            return self._generate(prompt)

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
            return self._generate(prompt)

        except Exception as e:
            print(f"❌ خطا در Gemini summary: {e}")
            return None
