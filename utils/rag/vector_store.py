# ============================================================
# Vector Store — ذخیره‌ی بردارها
# ============================================================
import numpy as np
import json
import os
from config import get_config

class VectorStore:
    """
    ذخیره‌ی بردارها

    ساده‌ترین پیاده‌سازی: بردارها توی حافظه + ذخیره توی فایل
    برای پروداکشن: از FAISS یا ChromaDB استفاده کن
    """

    def __init__(self):
        self.config = get_config()
        self.vectors = None       # numpy array
        self.documents = []       # لیست متادیتا
        self._loaded = False
        self.store_path = self.config.RAG_STORE_PATH

    def build(self, documents, embeddings):
        """
        ساخت index از بردارها

        Args:
            documents: لیست داکیومنت‌ها (دیکشنری)
            embeddings: بردارها (numpy array)
        """
        self.documents = documents
        self.vectors = embeddings
        self._loaded = True

        print(f"✅ Index ساخته شد: {len(documents)} داکیومنت")

    def search(self, query_vector, top_k=3):
        """
        جستجوی بردارهای مشابه

        Args:
            query_vector: بردار سوال
            top_k: تعداد نتایج

        Returns:
            لیست (document, score)
        """
        if not self._loaded or self.vectors is None:
            return []

        try:
            # ===== شباهت کسینوسی =====
            # چون بردارها normalize شدن، ضرب داخلی = شباهت کسینوسی
            similarities = np.dot(self.vectors, query_vector.T).flatten()

            # ===== مرتب‌سازی =====
            top_indices = np.argsort(similarities)[::-1][:top_k]

            results = []
            for idx in top_indices:
                score = float(similarities[idx])
                # فیلتر: فقط شباهت بالای ۰.۳
                if score >= 0.3:
                    results.append({
                        'document': self.documents[idx],
                        'score': round(score, 3)
                    })

            return results

        except Exception as e:
            print(f"❌ خطا در search: {e}")
            return []

    def save(self, path=None):
        """ذخیره‌ی index"""
        path = path or self.store_path

        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)

            data = {
                'documents': self.documents,
                'vectors': self.vectors.tolist() if self.vectors is not None else []
            }

            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)

            print(f"✅ Index ذخیره شد: {path}")

        except Exception as e:
            print(f"❌ خطا در save: {e}")

    def load(self, path=None):
        """لود index"""
        path = path or self.store_path

        try:
            if not os.path.exists(path):
                return False

            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.documents = data.get('documents', [])
            self.vectors = np.array(data.get('vectors', []))
            self._loaded = len(self.documents) > 0

            if self._loaded:
                print(f"✅ Index لود شد: {len(self.documents)} داکیومنت")

            return self._loaded

        except Exception as e:
            print(f"❌ خطا در load: {e}")
            return False

    def is_loaded(self):
        return self._loaded