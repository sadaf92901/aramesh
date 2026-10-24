# ============================================================
# utils/ethical_data.py — مدیریت اخلاقی داده‌های صوتی
# ============================================================

import os
import uuid
import shutil
import datetime
from typing import Optional
from utils.logger import logger


class EthicalDataManager:
    def __init__(self, archive_dir: str, upload_dir: str):
        self.archive_dir = archive_dir
        self.upload_dir = upload_dir

        if not os.path.exists(self.archive_dir):
            os.makedirs(self.archive_dir)
            logger.info(f"📂 Created archive directory: {self.archive_dir}")

    def process_audio_for_archive(self, user_id: str, file_path: str, has_consent: bool) -> Optional[str]:
        """
        بررسی رضایت، گمنام‌سازی و انتقال فایل به آرشیو.
        اگر رضایت نباشد، فایل فوراً پاک می‌شود.
        """
        # ===== لاگ دیباگ برای دیدن مسیر و وضعیت =====
        print(f"🔍 [DEBUG] process_audio_for_archive called | User: {user_id} | Consent: {has_consent} | File: {file_path}")
        logger.info(f"🎤 Processing audio | User: {user_id} | Consent: {has_consent}")

        if not os.path.exists(file_path):
            logger.warning(f"⚠️ File not found: {file_path}")
            print(f"❌ [DEBUG] File not found: {file_path}")
            return None

        # ===== ۱. اگر رضایت ندارد: فایل را پاک کن =====
        if not has_consent:
            try:
                os.remove(file_path)
                logger.info(f"🗑️ Audio deleted (no consent) for User: {user_id}")
                print(f"🗑️ [DEBUG] Audio deleted (no consent): {file_path}")
            except Exception as e:
                logger.error(f"❌ Error deleting audio: {e}")
                print(f"❌ [DEBUG] Error deleting: {e}")
            return None

        # ===== ۲. اگر رضایت دارد: گمنام‌سازی و آرشیو =====
        try:
            anonymous_id = str(uuid.uuid4())
            file_extension = os.path.splitext(file_path)[1]
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

            new_filename = f"anon_{anonymous_id}_{timestamp}{file_extension}"
            destination_path = os.path.join(self.archive_dir, new_filename)

            # انتقال فایل
            shutil.move(file_path, destination_path)

            # ثبت در Manifest
            self._log_to_manifest(anonymous_id, new_filename)

            logger.info(f"✅ Audio archived (anonymized): {new_filename}")
            print(f"✅ [DEBUG] Audio archived successfully: {new_filename}")
            return new_filename

        except Exception as e:
            logger.error(f"❌ Error in EthicalDataManager for User {user_id}: {str(e)}")
            print(f"❌ [DEBUG] Error archiving: {e}")
            return None

    def _log_to_manifest(self, anon_id: str, filename: str):
        """ثبت متادیتای گمنام در فایل مخصوص آرشیو"""
        manifest_path = os.path.join(self.archive_dir, "archive_manifest.log")
        log_entry = f"{datetime.datetime.now().isoformat()} | ID: {anon_id} | File: {filename}\n"

        try:
            with open(manifest_path, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception as e:
            logger.error(f"❌ Error writing to manifest: {e}")
