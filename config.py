# ============================================================
# تنظیمات پروژه
# ============================================================

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """تنظیمات اصلی پروژه"""

    # ============================================================
    # تنظیمات عمومی
    # ============================================================
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DEBUG = False
    TESTING = False

    # ============================================================
    # مسیرها
    # ============================================================
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    STATIC_FOLDER = os.path.join(BASE_DIR, 'static')
    TEMPLATES_FOLDER = os.path.join(BASE_DIR, 'templates')

    # ============================================================
    # آواتار
    # ============================================================
    AVATAR_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads', 'avatars')
    MAX_AVATAR_SIZE = 2 * 1024 * 1024
    ALLOWED_AVATAR_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    # ============================================================
    # محدودیت‌ها
    # ============================================================
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    MAX_AUDIO_SIZE = 5 * 1024 * 1024
    MAX_TEXT_LENGTH = 1000

    # ============================================================
    # تنظیمات آپلود
    # ============================================================
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg', 'webm', 'm4a'}

    # ============================================================
    # CORS
    # ============================================================
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000']

    # ============================================================
    # دیتابیس
    # ============================================================
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///aramesh.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ============================================================
    # LLM
    # ============================================================
    LLM_ENABLED = True
    LLM_PROVIDER = os.environ.get('LLM_PROVIDER', 'openai')
    LLM_TEMPERATURE = 0.7

    # ===== OpenAI (AvalAI) =====
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_BASE_URL = os.environ.get('OPENAI_BASE_URL', 'https://api.avalai.ir/v1')
    OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-4o-mini')
    OPENAI_TRANSCRIBE_MODEL = os.environ.get('OPENAI_TRANSCRIBE_MODEL', 'whisper-1')

    # ===== Gemini (Google) =====
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-2.5-flash')

    # ============================================================
    # Speech
    # ============================================================
    SPEECH_ENABLED = True
    SPEECH_PROVIDER = os.environ.get('SPEECH_PROVIDER', 'avalai')
    WHISPER_MODEL = 'base'

    # ============================================================
    # RAG
    # ============================================================
    RAG_ENABLED = True
    RAG_DATASET_PATH = os.path.join(BASE_DIR, 'data', 'psychology_dataset.json')
    RAG_STORE_PATH = os.path.join(BASE_DIR, 'data', 'vector_store.json')
    RAG_EMBEDDING_MODEL = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
    RAG_TOP_K = 3

    # ============================================================
    # Email
    # ============================================================
    EMAIL_ENABLED = True
    EMAIL_PROVIDER = 'mock'
    SMTP_HOST = os.environ.get('SMTP_HOST', '')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
    SMTP_USER = os.environ.get('SMTP_USER', '')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')
    SMTP_FROM = os.environ.get('SMTP_FROM', 'noreply@aramesh.app')


# ============================================================
# محیط‌ها
# ============================================================

class DevelopmentConfig(Config):
    """تنظیمات محیط توسعه"""
    DEBUG = True
    ENV = 'development'


class ProductionConfig(Config):
    """تنظیمات محیط تولید"""
    DEBUG = False
    ENV = 'production'

    # ===== 🆕 الزامات امنیتی در Production =====
    def __init__(self):
        super().__init__()
        if not self.SECRET_KEY:
            raise ValueError("⚠️ SECRET_KEY در محیط production تنظیم نشده است!")

        if not os.environ.get('DATABASE_URL'):
            raise ValueError("⚠️ DATABASE_URL در محیط production تنظیم نشده است!")

        # ===== چک کردن کلیدهای AI (حداقل یکی باید باشه) =====
        if not self.OPENAI_API_KEY and not self.GEMINI_API_KEY:
            print("⚠️ هشدار: هیچ کلید API برای LLM تنظیم نشده است. سیستم در حالت fallback کار می‌کند.")


class TestingConfig(Config):
    """تنظیمات محیط تست"""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# ============================================================
# انتخاب تنظیمات
# ============================================================

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config():
    """دریافت تنظیمات مناسب"""
    env = os.environ.get('FLASK_ENV', 'development')
    config_class = config.get(env, DevelopmentConfig)

    # ===== 🆕 برای اینکه ProductionConfig درست مقداردهی بشه =====
    if env == 'production':
        return ProductionConfig()

    return config_class
