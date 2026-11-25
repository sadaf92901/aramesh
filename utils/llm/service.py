# ============================================================
# سرویس اصلی LLM
# ============================================================

from .providers import OpenAIProvider, GeminiProvider

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

    # ============================================================
    # متدهای اصلی (بدون تغییر)
    # ============================================================

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

    # ============================================================
    # 🆕 RAG مستقیم (بدون LLM)
    # ============================================================

    def try_rag_analysis(self, text_answers):
        """
        تحلیل با RAG — هر متن جداگانه match می‌شه و میانگین گرفته می‌شه
        با آستانه‌ی تطبیقی
        """
        try:
            from utils.rag.service import get_rag_service
            rag = get_rag_service()
            if not rag.is_ready():
                return None

            valid_texts = [t for t in text_answers if t and t.strip()]
            if not valid_texts:
                return None

            matched_docs = []
            scores = []

            for text in valid_texts:
                results = rag.retriever.retrieve(
                    text,
                    top_k=1,
                    min_score=self.config.RAG_ANALYSIS_THRESHOLD
                )
                if results:
                    matched_docs.append(results[0]['document'])
                    scores.append(results[0]['score'])

            if not matched_docs:
                return None

            # ===== میانگین‌گیری =====
            avg_dep = sum(d.get('depression_score', 50) for d in matched_docs) / len(matched_docs)
            avg_anx = sum(d.get('anxiety_score', 50) for d in matched_docs) / len(matched_docs)
            avg_score = sum(scores) / len(scores)

            # ===== 🆕 تعیین سطح اطمینان =====
            if avg_score >= self.config.RAG_HIGH_CONFIDENCE:
                confidence = 'high'
                status = f'موفق (RAG، اطمینان بالا، {len(matched_docs)} match)'
            elif avg_score >= self.config.RAG_MEDIUM_CONFIDENCE:
                confidence = 'medium'
                status = f'موفق (RAG، اطمینان متوسط، {len(matched_docs)} match)'
            else:
                return None

            # emotion غالب
            dominant_emotion = matched_docs[0].get('emotion', 'نامشخص')

            # signs ترکیبی
            all_signs = []
            for d in matched_docs:
                for s in d.get('signs', []):
                    if s not in all_signs:
                        all_signs.append(s)

            return {
                'dominant_emotion': dominant_emotion,
                'emotion_intensity': 5,
                'depression_score': round(avg_dep, 1),
                'anxiety_score': round(avg_anx, 1),
                'protective_factors_score': round(max(0, 100 - avg_dep), 1),
                'risk_factors_score': round(avg_dep, 1),
                'final_score': round(max(0, 100 - avg_dep), 1),
                'key_concerns': all_signs[:5],
                'treatment': matched_docs[0].get('treatment', ''),
                'status': status,
                'confidence': confidence,
                '_rag_score': round(avg_score, 3),
            }
        except Exception as e:
            logger.error(f"❌ خطا در RAG مستقیم: {e}")
            return None


    def try_rag_chat(self, message):
        """
        تلاش برای پاسخ چت فقط با RAG
        فقط اگر match خیلی قوی باشد (آستانه بالا)
        """
        try:
            from utils.rag.service import get_rag_service
            rag = get_rag_service()
            if not rag.is_ready():
                return None

            results = rag.retriever.retrieve(
                message,
                top_k=1,
                min_score=self.config.RAG_CHAT_THRESHOLD
            )
            if not results:
                return None

            doc = results[0]['document']
            treatment = doc.get('treatment', '')
            if not treatment:
                return None

            return treatment
        except Exception as e:
            logger.error(f"❌ خطا در RAG چت مستقیم: {e}")
            return None

    # ============================================================
    # 🆕 Analyze با ترتیب RAG → LLM
    # ============================================================

    def analyze_text_smart(self, text_answers):
        """اول RAG، اگر نشد LLM"""
        rag_result = self.try_rag_analysis(text_answers)
        if rag_result is not None:
            logger.info(f"✅ تحلیل با RAG (score={rag_result['_rag_score']})")
            return rag_result

        logger.info("⚠️ RAG match قوی نداشت → LLM")
        return self.analyze_text(text_answers)

    def chat_smart(self, message):
        """اول RAG، اگر نشد LLM"""
        rag_reply = self.try_rag_chat(message)
        if rag_reply is not None:
            logger.info("✅ چت با RAG")
            return rag_reply

        return self.chat(message)


_llm_service = None


def get_llm_service():
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
