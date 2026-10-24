# ============================================================
# تست‌های مدیریت اخلاقی داده‌های صوتی (EthicalDataManager)
# ============================================================

import os
import pytest
import tempfile
from utils.ethical_data import EthicalDataManager

@pytest.fixture
def temp_dirs():
    """ساخت پوشه‌های موقت برای تست"""
    with tempfile.TemporaryDirectory() as upload_dir:
        with tempfile.TemporaryDirectory() as archive_dir:
            yield upload_dir, archive_dir

@pytest.fixture
def manager(temp_dirs):
    """ساخت نمونه از EthicalDataManager با پوشه‌های موقت"""
    upload_dir, archive_dir = temp_dirs
    return EthicalDataManager(archive_dir, upload_dir)

@pytest.fixture
def fake_audio_file(temp_dirs):
    """ساخت یک فایل صوتی فیک برای تست"""
    upload_dir, _ = temp_dirs
    file_path = os.path.join(upload_dir, 'test_audio.wav')
    with open(file_path, 'wb') as f:
        f.write(b'fake audio data')
    return file_path

class TestEthicalDataManager:
    """تست‌های کلاس EthicalDataManager"""

    def test_archive_with_consent(self, manager, fake_audio_file, temp_dirs):
        """اگر کاربر رضایت بده، فایل باید به آرشیو منتقل شود"""
        _, archive_dir = temp_dirs
        user_id = '1'
        has_consent = True

        # اجرای تابع
        new_filename = manager.process_audio_for_archive(user_id, fake_audio_file, has_consent)

        # بررسی نتایج
        assert new_filename is not None
        assert new_filename.startswith('anon_')
        assert new_filename.endswith('.wav')

        # فایل اصلی باید حذف شده باشد
        assert not os.path.exists(fake_audio_file)

        # فایل جدید باید در آرشیو باشد
        archived_path = os.path.join(archive_dir, new_filename)
        assert os.path.exists(archived_path)

        # فایل manifest باید ساخته شده باشد
        manifest_path = os.path.join(archive_dir, 'archive_manifest.log')
        assert os.path.exists(manifest_path)

    def test_delete_without_consent(self, manager, fake_audio_file, temp_dirs):
        """اگر کاربر رضایت نده، فایل باید فوراً پاک شود"""
        _, archive_dir = temp_dirs
        user_id = '2'
        has_consent = False

        # اجرای تابع
        result = manager.process_audio_for_archive(user_id, fake_audio_file, has_consent)

        # بررسی نتایج
        assert result is None  # خروجی باید None باشد

        # فایل اصلی باید حذف شده باشد
        assert not os.path.exists(fake_audio_file)

        # آرشیو باید خالی باشد
        assert len(os.listdir(archive_dir)) == 0

    def test_file_not_found(self, manager):
        """اگر فایل وجود نداشته باشد، نباید خطا بدهد"""
        result = manager.process_audio_for_archive('1', '/path/to/non/existent.wav', True)
        assert result is None