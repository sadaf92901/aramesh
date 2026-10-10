"""
اجرای سرویس‌ها — فقط برای production
"""
from utils.llm.service import get_llm_service
from utils.speech.service import get_speech_service
from utils.rag.service import get_rag_service


def preload_services():
    """لود LLM, Speech, RAG از قبل"""
    print("\n" + "=" * 60)
    print("🔄 در حال لود سرویس‌ها...")
    print("=" * 60)

    # ===== LLM =====
    try:
        print("🔄 در حال لود LLM...")
        llm = get_llm_service()
        if llm.is_available():
            print("✅ LLM آماده")
        else:
            print("⚠️ LLM در دسترس نیست")
    except Exception as e:
        print(f"⚠️ LLM لود نشد: {e}")

    # ===== Speech =====
    try:
        print("🔄 در حال لود Speech...")
        speech = get_speech_service()
        if speech.is_available():
            print("✅ Speech آماده")
        else:
            print("⚠️ Speech در دسترس نیست")
    except Exception as e:
        print(f"⚠️ Speech لود نشد: {e}")

    # ===== RAG =====
    try:
        print("🔄 در حال راه‌اندازی RAG...")
        rag = get_rag_service()
        if rag.initialize():
            print("✅ RAG آماده")
        else:
            print("⚠️ RAG در دسترس نیست")
    except Exception as e:
        print(f"⚠️ RAG لود نشد: {e}")

    print("=" * 60)
    print("✅ سرویس‌ها آماده شدن")
    print("=" * 60 + "\n")