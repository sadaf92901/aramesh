# ============================================================
# Retriever — جستجو
# ============================================================

from .embeddings import EmbeddingModel
from .vector_store import VectorStore


class Retriever:
    """
    جستجوگر — ترکیب embedding + vector store
    """

    def __init__(self):
        self.embedding_model = EmbeddingModel()
        self.vector_store = VectorStore()

    def build_index(self, documents):
        """ساخت index از داکیومنت‌ها"""
        if not documents:
            print("⚠️ داکیومنت خالی")
            return False

        # ===== لود مدل embedding =====
        self.embedding_model.load()
        if not self.embedding_model.is_available():
            return False

        # ===== استخراج متن‌ها =====
        texts = [doc.get('text', '') for doc in documents]

        # ===== تبدیل به بردار =====
        embeddings = self.embedding_model.encode(texts)
        if embeddings is None:
            return False

        # ===== ذخیره =====
        self.vector_store.build(documents, embeddings)
        return True

    def retrieve(self, query, top_k=3):
        """
        جستجوی نمونه‌های مشابه

        Args:
            query: متن سوال
            top_k: تعداد نتایج

        Returns:
            لیست نتایج
        """
        if not self.vector_store.is_loaded():
            return []

        if not self.embedding_model.is_available():
            self.embedding_model.load()
            if not self.embedding_model.is_available():
                return []

        # ===== تبدیل query به بردار =====
        query_vector = self.embedding_model.encode(query)
        if query_vector is None:
            return []

        # ===== جستجو =====
        return self.vector_store.search(query_vector, top_k=top_k)

    def is_ready(self):
        return (
            self.embedding_model.is_available() and
            self.vector_store.is_loaded()
        )