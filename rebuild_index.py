# ============================================================
# بازسازی vector store
# اجرا: python rebuild_index.py
# ============================================================

import os
from config import get_config


def main():
    config = get_config()

    # ===== حذف cache قدیمی =====
    if os.path.exists(config.RAG_STORE_PATH):
        os.remove(config.RAG_STORE_PATH)
        print(f"🗑️ cache قدیمی حذف شد: {config.RAG_STORE_PATH}")

    # ===== ساخت مجدد =====
    from utils.rag.service import RAGService
    rag = RAGService()

    print("🔄 در حال ساخت index جدید...")
    ok = rag.initialize()

    if ok:
        count = len(rag.retriever.vector_store.documents)
        print(f"✅ index ساخته شد: {count} داکیومنت")
    else:
        print("❌ خطا در ساخت index")


if __name__ == '__main__':
    main()