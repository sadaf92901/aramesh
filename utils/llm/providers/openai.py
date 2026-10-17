# ============================================================
# OpenAI Provider — استفاده از OpenAI SDK
# (سازگار با AvalAI, OpenAI, DeepSeek, ...)
# ============================================================

from .base import LLMProvider
from ..prompts import PROMPTS
from ..parser import parse_json_response, get_fallback_analysis
from config import get_config
from utils.logger import logger


class OpenAIProvider(LLMProvider):
    """Provider بر اساس OpenAI SDK"""

    def __init__(self):
        self.config = get_config()
        self.api_key = self.config.OPENAI_API_KEY
        self.base_url = self.config.OPENAI_BASE_URL
        self.model_name = self.config.OPENAI_MODEL

        if not self.api_key:
            logger.warning("⚠️ OPENAI_API_KEY تنظیم نشده")
            self.client = None
            return

        try:
            from openai import OpenAI

            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )

            logger.info(f"✅ OpenAI Provider آماده")
            logger.info(f"   Base URL: {self.base_url}")
            logger.info(f"   Model: {self.model_name}")

        except ImportError:
            logger.error("❌ openai نصب نیست")
            logger.error("   نصب: pip install openai")
            self.client = None
        except Exception as e:
            logger.error(f"❌ خطا در راه‌اندازی OpenAI: {e}")
            self.client = None

    def is_available(self):
        return self.client is not None

    # ============================================================
    # تحلیل متن (override)
    # ============================================================

    def analyze_text(self, text_answers):
        """تحلیل پاسخ‌های کاربر"""
        if not self.is_available():
            return None

        try:
            # ===== دریافت context از RAG =====
            rag_context = ""
            try:
                from utils.rag.service import get_rag_service
                rag = get_rag_service()

                if rag.is_ready():
                    combined_text = " ".join([t for t in text_answers if t and t.strip()])

                    if combined_text:
                        rag_context = rag.get_context(combined_text, top_k=3)

                        if rag_context:
                            logger.info(f"✅ RAG context دریافت شد ({len(rag_context)} کاراکتر)")
                        else:
                            logger.warning("⚠️ RAG context خالی برگشت")
            except Exception as e:
                logger.warning(f"⚠️ خطا در RAG: {e}")

            # ===== ساخت پرامپت =====
            base_prompt = PROMPTS['analysis'].format(
                answer1=text_answers[0] if len(text_answers) > 0 else '',
                answer2=text_answers[1] if len(text_answers) > 1 else '',
                answer3=text_answers[2] if len(text_answers) > 2 else '',
            )

            # ===== اضافه کردن RAG context =====
            if rag_context:
                prompt = f"""نمونه‌های مشابه از دیتاست روانشناسی:

{rag_context}

---

حالا بر اساس نمونه‌های بالا، این پاسخ‌های کاربر رو تحلیل کن:

{base_prompt}"""
            else:
                prompt = base_prompt

            # ===== فراخوانی LLM =====
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.LLM_TEMPERATURE,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content
            result = parse_json_response(content)

            if not result:
                return None

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
            logger.error(f"❌ خطا در OpenAI analyze: {e}")
            return None

    # ============================================================
    # چت (override)
    # ============================================================

    def chat(self, message):
        """پاسخ چت‌بات با استفاده از RAG"""
        if not self.is_available():
            return None

        try:
            # ===== دریافت context از RAG =====
            rag_context = ""
            try:
                from utils.rag.service import get_rag_service
                rag = get_rag_service()

                if rag.is_ready():
                    rag_context = rag.get_context(message, top_k=2)

                    if rag_context:
                        logger.info(f"✅ RAG context برای چت دریافت شد ({len(rag_context)} کاراکتر)")
                    else:
                        logger.warning("⚠️ RAG context خالی برگشت")
            except Exception as e:
                logger.error(f"⚠️ خطا در RAG چت: {e}")

            # ===== ساخت پرامپت =====
            base_prompt = PROMPTS['chat'].format(message=message)

            # ===== اضافه کردن RAG context =====
            if rag_context:
                prompt = f"""نمونه‌های مشابه از دیتاست روانشناسی:

{rag_context}

---

{base_prompt}"""
            else:
                prompt = base_prompt

            # ===== فراخوانی LLM =====
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=300
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"❌ خطا در OpenAI chat: {e}")
            return None

    # ============================================================
    # جمع‌بندی هفتگی (override)
    # ============================================================

    def weekly_summary(self, data):
        """جمع‌بندی هفتگی"""
        if not self.is_available():
            return None

        try:
            prompt = PROMPTS['weekly_summary'].format(**data)

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"❌ خطا در OpenAI summary: {e}")
            return None
