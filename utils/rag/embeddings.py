# ============================================================
# Embeddings — تبدیل متن به بردار
# ============================================================
from config import get_config
class EmbeddingModel:
    """
    مدل تبدیل متن به بردار

    از sentence-transformers استفاده می‌کنه.
    مدل پیش‌فرض: paraphrase-multilingual-MiniLM-L12-v2 (چندزبانه، فارسی رو هم پشتیبانی می‌کنه)
    """

    def __init__(self):
        self.config = get_config()
        self.model = None
        self._loaded = False
        self.model_name = self.config.RAG_EMBEDDING_MODEL

    def load(self):
        """لود مدل"""
        if self._loaded:
            return

        try:
            from sentence_transformers import SentenceTransformer

            print(f"🔄 در حال لود مدل embedding: {self.model_name}...")
            self.model = SentenceTransformer(self.model_name)
            self._loaded = True
            print(f"✅ مدل embedding لود شد")

        except ImportError:
            print("❌ sentence-transformers نصب نیست")
            print("   نصب: pip install sentence-transformers")
        except Exception as e:
            print(f"❌ خطا در لود embedding: {e}")

    def is_available(self):
        return self._loaded and self.model is not None

    def encode(self, texts):
        """
        تبدیل متن‌ها به بردار

        Args:
            texts: لیست متن یا یه متن

        Returns:
            لیست بردارها یا یه بردار
        """
        if not self.is_available():
            return None

        if isinstance(texts, str):
            texts = [texts]

        try:
            embeddings = self.model.encode(
                texts,
                convert_to_numpy=True,
                normalize_embeddings=True
            )
            return embeddings
        except Exception as e:
            print(f"❌ خطا در encode: {e}")
            return None