# ============================================================
# دیتاست روانشناسی
# ============================================================

import json
import os
from config import get_config


class PsychologyDataset:
    """
    دیتاست نمونه‌های روانشناسی فارسی
    """

    def __init__(self):
        self.config = get_config()
        self.dataset_path = self.config.RAG_DATASET_PATH
        self.documents = []

    def load(self):
        """لود دیتاست از فایل JSON"""
        try:
            if not os.path.exists(self.dataset_path):
                print(f"⚠️ دیتاست پیدا نشد: {self.dataset_path}")
                return False

            with open(self.dataset_path, 'r', encoding='utf-8') as f:
                self.documents = json.load(f)

            print(f"✅ دیتاست لود شد: {len(self.documents)} نمونه")
            return True

        except Exception as e:
            print(f"❌ خطا در لود دیتاست: {e}")
            return False

    def get_all(self):
        return self.documents

    def is_empty(self):
        return len(self.documents) == 0