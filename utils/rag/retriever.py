# ============================================================
# Retriever — جستجو (Hybrid: Semantic + BM25)
# ============================================================

import re
from .embeddings import EmbeddingModel
from .vector_store import VectorStore
from utils.logger import logger
from utils.helpers import normalize_text


class Retriever:
    """
    جستجوگر — ترکیب embedding + vector store + BM25
    """

    def __init__(self):
        self.embedding_model = EmbeddingModel()
        self.vector_store = VectorStore()
        self.bm25 = None
        self.bm25_docs = []

    def _tokenize(self, text):
        """توکن‌سازی ساده برای فارسی"""
        text = normalize_text(text)
        # حذف کاراکترهای غیرفارسی/غیرعددی
        tokens = re.findall(r'[\u0600-\u06FF]+|\d+', text)
        return tokens

    def build_index(self, documents):
        """ساخت index از داکیومنت‌ها"""
        if not documents:
            logger.warning("⚠️ داکیومنت خالی")
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

        # ===== 🆕 ساخت BM25 =====
        self._build_bm25(documents)

        return True

    def _build_bm25(self, documents):
        """ساخت index BM25"""
        try:
            from rank_bm25 import BM25Okapi
            self.bm25_docs = [self._tokenize(doc.get('text', '')) for doc in documents]
            self.bm25 = BM25Okapi(self.bm25_docs)
            logger.info(f"✅ BM25 ساخته شد: {len(documents)} داکیومنت")
        except ImportError:
            logger.warning("⚠️ rank-bm25 نصب نیست — فقط semantic search")
            self.bm25 = None

    def _load_bm25_if_needed(self):
        """لود BM25 اگر لود نشده"""
        if self.bm25 is None and self.vector_store.is_loaded():
            self._build_bm25(self.vector_store.documents)

    def retrieve(self, query, top_k=3, min_score=0.0):
        """
        جستجوی ترکیبی (Semantic + BM25)
        """
        if not self.vector_store.is_loaded():
            return []

        if not self.embedding_model.is_available():
            self.embedding_model.load()
            if not self.embedding_model.is_available():
                return []

        # 🆕 لود BM25 اگر لازمه
        self._load_bm25_if_needed()

        # ===== نرمال‌سازی query =====
        query = normalize_text(query)

        # ===== Semantic search =====
        query_vector = self.embedding_model.encode(query)
        if query_vector is None:
            return []

        semantic_results = self.vector_store.search(
            query_vector, top_k=top_k * 2, min_score=0.0
        )

        # ===== 🆕 BM25 search =====
        bm25_scores = {}
        if self.bm25 is not None:
            query_tokens = self._tokenize(query)
            if query_tokens:
                scores = self.bm25.get_scores(query_tokens)
                for idx, score in enumerate(scores):
                    bm25_scores[idx] = float(score)

        # ===== 🆕 ترکیب نتایج =====
        combined = {}

        # Semantic
        for r in semantic_results:
            doc_idx = self.vector_store.documents.index(r['document'])
            combined[doc_idx] = {
                'document': r['document'],
                'semantic_score': r['score'],
                'bm25_score': 0.0,
            }

        # BM25
        for doc_idx, bm25_score in bm25_scores.items():
            if doc_idx in combined:
                combined[doc_idx]['bm25_score'] = bm25_score
            elif bm25_score > 0:
                combined[doc_idx] = {
                    'document': self.vector_store.documents[doc_idx],
                    'semantic_score': 0.0,
                    'bm25_score': bm25_score,
                }

        # ===== نرمال‌سازی BM25 =====
        if bm25_scores:
            max_bm25 = max(bm25_scores.values()) if bm25_scores else 1.0
            if max_bm25 > 0:
                for doc_idx in combined:
                    combined[doc_idx]['bm25_score'] /= max_bm25

        # ===== ترکیب نهایی (70% semantic + 30% BM25) =====
        final_results = []
        for doc_idx, data in combined.items():
            final_score = 0.7 * data['semantic_score'] + 0.3 * data['bm25_score']
            if final_score >= min_score:
                final_results.append({
                    'document': data['document'],
                    'score': round(final_score, 3),
                    'semantic_score': round(data['semantic_score'], 3),
                    'bm25_score': round(data['bm25_score'], 3),
                })

        # مرتب‌سازی
        final_results.sort(key=lambda x: x['score'], reverse=True)
        return final_results[:top_k]

    def is_ready(self):
        return (
            self.embedding_model.is_available() and
            self.vector_store.is_loaded()
        )
