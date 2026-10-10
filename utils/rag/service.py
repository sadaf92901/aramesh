# ============================================================
# سرویس RAG
# ============================================================

from .dataset import PsychologyDataset
from .retriever import Retriever
from config import get_config


class RAGService:
    """
    سرویس RAG — Interface اصلی

    کاربرد:
    ۱. ساخت index از دیتاست (یا لود از cache)
    ۲. جستجوی نمونه‌های مشابه برای یه متن
    ۳. تولید "context" برای LLM
    """

    def __init__(self):
        self.config = get_config()
        self.enabled = self.config.RAG_ENABLED
        self.dataset = PsychologyDataset()
        self.retriever = Retriever()
        self._ready = False

    def initialize(self):
        """
        راه‌اندازی RAG

        - اگه cache داره، از cache لود می‌کنه
        - وگرنه index می‌سازه و ذخیره می‌کنه
        """
        if not self.enabled:
            print("⚠️ RAG غیرفعاله")
            return False

        # ===== جلوگیری از راه‌اندازی دوباره =====
        if self._ready:
            return True

        # ===== ۱. تلاش برای لود از cache =====
        if self.retriever.vector_store.load():
            self._ready = True
            return True

        # ===== ۲. لود دیتاست =====
        if not self.dataset.load():
            return False

        # ===== ۳. ساخت index =====
        documents = self.dataset.get_all()
        if not documents:
            print("⚠️ دیتاست خالیه")
            return False

        if not self.retriever.build_index(documents):
            print("❌ خطا در ساخت index")
            return False

        # ===== ۴. ذخیره برای بار بعد =====
        try:
            self.retriever.vector_store.save()
        except Exception as e:
            print(f"⚠️ خطا در ذخیره‌ی cache: {e}")

        self._ready = True
        return True

    def is_ready(self):
        return self._ready and self.retriever.is_ready()

    def get_context(self, query, top_k=3):
        """
        گرفتن context برای LLM

        Args:
            query: متن کاربر
            top_k: تعداد نمونه‌های مشابه

        Returns:
            str: متن context (برای تزریق به prompt LLM)
        """
        if not self.is_ready():
            return ""

        # ===== جستجو =====
        results = self.retriever.retrieve(query, top_k=top_k)

        if not results:
            return ""

        # ===== ساخت متن context =====
        context_parts = []

        for i, r in enumerate(results, 1):
            doc = r['document']
            score = r['score']

            text = doc.get('text', '')
            emotion = doc.get('emotion', 'نامشخص')
            level = doc.get('level', 'نامشخص')
            signs = doc.get('signs', [])

            part = f"""نمونه {i} (شباهت: {score}):
متن: "{text}"
احساس: {emotion}
سطح: {level}
نشانه‌ها: {', '.join(signs) if signs else 'ندارد'}"""

            context_parts.append(part)

        return "\n\n".join(context_parts)

    def get_analysis_hint(self, query):
        """
        گرفتن یه راهنمای سریع از دیتاست

        Args:
            query: متن کاربر

        Returns:
            dict یا None
        """
        if not self.is_ready():
            return None

        results = self.retriever.retrieve(query, top_k=1)

        if not results:
            return None

        return results[0]['document']


# ============================================================
# Singleton
# ============================================================

_rag_service = None


def get_rag_service():
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
