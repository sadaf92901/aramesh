"""
اجرای سرویس‌ها — فقط برای production
"""
from utils.llm.service import get_llm_service
from utils.speech.service import get_speech_service
from utils.rag.service import get_rag_service
from utils.logger import logger


def preload_services():
    """لود LLM, Speech, RAG از قبل"""
    logger.info("=" * 60)
    logger.info("🔄 در حال لود سرویس‌ها...")
    logger.info("=" * 60)

    # ===== LLM =====
    try:
        logger.info("🔄 در حال لود LLM...")
        llm = get_llm_service()
        if llm.is_available():
            logger.info("✅ LLM آماده")
        else:
            logger.warning("⚠️ LLM در دسترس نیست")
    except Exception as e:
        logger.warning(f"⚠️ LLM لود نشد: {e}")

    # ===== Speech =====
    try:
        logger.info("🔄 در حال لود Speech...")
        speech = get_speech_service()
        if speech.is_available():
            logger.info("✅ Speech آماده")
        else:
            logger.warning("⚠️ Speech در دسترس نیست")
    except Exception as e:
        logger.warning(f"⚠️ Speech لود نشد: {e}")

    # ===== RAG =====
    try:
        logger.info("🔄 در حال راه‌اندازی RAG...")
        rag = get_rag_service()
        if rag.initialize():
            logger.info("✅ RAG آماده")
        else:
            logger.warning("⚠️ RAG در دسترس نیست")
    except Exception as e:
        logger.warning(f"⚠️ RAG لود نشد: {e}")

    logger.info("=" * 60)
    logger.info("✅ سرویس‌ها آماده شدن")
    logger.info("=" * 60)