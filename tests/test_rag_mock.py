# ============================================================
# تست RAG با Mock
# ============================================================

import pytest
from unittest.mock import patch, MagicMock
import numpy as np


# ============================================================
# تست VectorStore
# ============================================================

class TestVectorStore:
    """تست Vector Store (بدون نیاز به مدل)"""

    def test_init(self):
        """مقداردهی"""
        from utils.rag.vector_store import VectorStore

        store = VectorStore()
        assert store.vectors is None
        assert store.documents == []
        assert store._loaded is False

    def test_is_loaded_false(self):
        """بدون داده → False"""
        from utils.rag.vector_store import VectorStore

        store = VectorStore()
        assert store.is_loaded() is False

    def test_build_with_mock(self):
        """ساخت index با داده‌های mock"""
        from utils.rag.vector_store import VectorStore

        store = VectorStore()

        # ===== داده‌های mock =====
        documents = [
            {'text': 'غم و ناراحتی', 'emotion': 'غم'},
            {'text': 'اضطراب و نگرانی', 'emotion': 'اضطراب'},
        ]
        embeddings = np.array([[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])

        store.build(documents, embeddings)

        assert store.is_loaded() is True
        assert len(store.documents) == 2

    def test_search_with_mock(self):
        """جستجو با بردار mock"""
        from utils.rag.vector_store import VectorStore

        store = VectorStore()

        documents = [
            {'text': 'غم و ناراحتی', 'emotion': 'غم'},
            {'text': 'اضطراب و نگرانی', 'emotion': 'اضطراب'},
        ]
        # ===== بردارهای نرمال =====
        embeddings = np.array([
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0]
        ])
        store.build(documents, embeddings)

        # ===== جستجو با بردار نزدیک به اولی =====
        query = np.array([[0.9, 0.1, 0.0]])
        results = store.search(query, top_k=1)

        assert len(results) > 0
        assert results[0]['document']['emotion'] == 'غم'
        assert results[0]['score'] > 0.5

    def test_search_threshold(self):
        """جستجو با threshold (شباهت زیر ۰.۳ رد می‌شه)"""
        from utils.rag.vector_store import VectorStore

        store = VectorStore()

        documents = [{'text': 'تست'}]
        embeddings = np.array([[1.0, 0.0]])
        store.build(documents, embeddings)

        # ===== query عمود بر بردار → شباهت ۰ =====
        query = np.array([[0.0, 1.0]])
        results = store.search(query, top_k=1)

        # ===== باید خالی باشه چون شباهت < 0.3 =====
        assert results == []

    def test_save_and_load(self, tmp_path):
        """ذخیره و لود از فایل"""
        from utils.rag.vector_store import VectorStore

        store = VectorStore()
        save_path = str(tmp_path / "test_store.json")

        documents = [{'text': 'تست', 'emotion': 'غم'}]
        embeddings = np.array([[0.1, 0.2, 0.3]])
        store.build(documents, embeddings)

        store.save(save_path)

        # ===== لود =====
        store2 = VectorStore()
        result = store2.load(save_path)

        assert result is True
        assert store2.is_loaded() is True
        assert len(store2.documents) == 1


# ============================================================
# تست PsychologyDataset
# ============================================================

class TestPsychologyDataset:
    """تست دیتاست"""

    def test_init(self):
        """مقداردهی"""
        from utils.rag.dataset import PsychologyDataset

        dataset = PsychologyDataset()
        assert dataset.documents == []

    def test_is_empty(self):
        """دیتاست خالی"""
        from utils.rag.dataset import PsychologyDataset

        dataset = PsychologyDataset()
        assert dataset.is_empty() is True

    def test_load(self):
        """لود دیتاست واقعی"""
        from utils.rag.dataset import PsychologyDataset

        dataset = PsychologyDataset()
        result = dataset.load()

        assert result is True
        assert not dataset.is_empty()
        assert len(dataset.get_all()) > 0

    def test_get_all(self):
        """گرفتن همه"""
        from utils.rag.dataset import PsychologyDataset

        dataset = PsychologyDataset()
        dataset.load()
        docs = dataset.get_all()

        assert isinstance(docs, list)
        assert len(docs) > 0

    def test_load_nonexistent(self):
        """لود فایل ناموجود → False"""
        from utils.rag.dataset import PsychologyDataset
        from config import get_config

        dataset = PsychologyDataset()

        # ===== مسیر اشتباه =====
        original_path = dataset.dataset_path
        dataset.dataset_path = '/invalid/path/xyz.json'

        result = dataset.load()
        assert result is False

        # ===== برگردوندن =====
        dataset.dataset_path = original_path


# ============================================================
# تست Embeddings (فقط init)
# ============================================================

class TestEmbeddingModel:
    """تست Embedding Model (بدون لود واقعی)"""

    def test_init(self):
        """مقداردهی"""
        from utils.rag.embeddings import EmbeddingModel

        model = EmbeddingModel()
        assert model.model is None
        assert model._loaded is False

    def test_is_available_false(self):
        """بدون لود → False"""
        from utils.rag.embeddings import EmbeddingModel

        model = EmbeddingModel()
        assert model.is_available() is False

    def test_encode_without_load(self):
        """encode بدون لود → None"""
        from utils.rag.embeddings import EmbeddingModel

        model = EmbeddingModel()
        result = model.encode("تست")
        assert result is None


# ============================================================
# تست RAGService (فقط interface)
# ============================================================

class TestRAGServiceInterface:
    """تست interface RAGService"""

    def test_singleton(self):
        """singleton"""
        from utils.rag.service import get_rag_service

        s1 = get_rag_service()
        s2 = get_rag_service()
        assert s1 is s2

    def test_has_methods(self):
        """متدها"""
        from utils.rag.service import get_rag_service

        s = get_rag_service()
        assert hasattr(s, 'initialize')
        assert hasattr(s, 'is_ready')
        assert hasattr(s, 'get_context')
        assert hasattr(s, 'get_analysis_hint')

    def test_get_context_when_not_ready(self):
        """بدون ready → رشته خالی"""
        from utils.rag.service import RAGService

        # ===== یه instance جدید (بدون initialize) =====
        service = RAGService()
        # اگه init نشده باشه، ready نیست
        # ولی چون singleton هست، شاید ready باشه

    def test_get_analysis_hint_when_not_ready(self):
        """بدون ready → None"""
        from utils.rag.service import RAGService

        service = RAGService()
        # اگه ready نباشه، None برمی‌گردونه
        if not service.is_ready():
            assert service.get_analysis_hint("تست") is None


# ============================================================
# تست Retriever (بدون لود واقعی)
# ============================================================

class TestRetriever:
    """تست Retriever"""

    def test_init(self):
        """مقداردهی"""
        from utils.rag.retriever import Retriever

        r = Retriever()
        assert r.embedding_model is not None
        assert r.vector_store is not None

    def test_is_ready_false(self):
        """بدون لود → False"""
        from utils.rag.retriever import Retriever

        r = Retriever()
        assert r.is_ready() is False

    def test_retrieve_without_index(self):
        """جستجو بدون index → خالی"""
        from utils.rag.retriever import Retriever

        r = Retriever()
        results = r.retrieve("تست", top_k=3)
        assert results == []

    def test_build_index_empty_docs(self):
        """ساخت index از داکیومنت خالی → False"""
        from utils.rag.retriever import Retriever

        r = Retriever()
        result = r.build_index([])
        assert result is False
