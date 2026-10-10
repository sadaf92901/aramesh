# ============================================================
# تست RAG
# ============================================================

import pytest
import os


class TestRAGService:
    """تست سرویس RAG"""

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


class TestDataset:
    """تست دیتاست"""

    def test_dataset_exists(self):
        """فایل دیتاست وجود داره"""
        from config import get_config

        c = get_config()
        assert os.path.exists(c.RAG_DATASET_PATH)

    def test_load(self):
        """لود دیتاست"""
        from utils.rag.dataset import PsychologyDataset

        d = PsychologyDataset()
        result = d.load()

        assert result is True
        assert not d.is_empty()

    def test_not_empty(self):
        """دیتاست خالی نیست"""
        from utils.rag.dataset import PsychologyDataset

        d = PsychologyDataset()
        d.load()

        assert len(d.get_all()) > 0

    def test_structure(self):
        """ساختار درست"""
        from utils.rag.dataset import PsychologyDataset

        d = PsychologyDataset()
        d.load()

        for doc in d.get_all():
            assert 'text' in doc
            assert 'emotion' in doc


class TestEmbedding:
    """تست Embedding"""

    def test_init(self):
        """مقداردهی"""
        from utils.rag.embeddings import EmbeddingModel

        m = EmbeddingModel()
        assert m.config is not None
        assert m.model_name is not None


class TestVectorStore:
    """تست Vector Store"""

    def test_init(self):
        """مقداردهی"""
        from utils.rag.vector_store import VectorStore

        v = VectorStore()
        assert v.documents == []
        assert v.vectors is None
        assert v.is_loaded() is False


class TestRetriever:
    """تست Retriever"""

    def test_init(self):
        """مقداردهی"""
        from utils.rag.retriever import Retriever

        r = Retriever()
        assert r.embedding_model is not None
        assert r.vector_store is not None