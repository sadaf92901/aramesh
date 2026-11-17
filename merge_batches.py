# ============================================================
# ادغام batch‌ها در یک دیتاست نهایی
# اجرا: python merge_batches.py
# ============================================================

import json
import os
import glob

BATCHES_DIR = 'data/batches'
OUTPUT_PATH = 'data/psychology_dataset.json'
BACKUP_PATH = 'data/psychology_dataset_backup.json'


def main():
    # ===== ۱. بکاپ از دیتاست قدیمی =====
    if os.path.exists(OUTPUT_PATH):
        with open(OUTPUT_PATH, 'r', encoding='utf-8') as f:
            old = json.load(f)
        with open(BACKUP_PATH, 'w', encoding='utf-8') as f:
            json.dump(old, f, ensure_ascii=False, indent=2)
        print(f"🗂️ بکاپ دیتاست قدیمی: {BACKUP_PATH} ({len(old)} رکورد)")

    # ===== ۲. لیست batch‌ها =====
    files = sorted(glob.glob(os.path.join(BATCHES_DIR, 'batch_*.json')))
    if not files:
        print(f"❌ هیچ batch‌ای در {BATCHES_DIR} پیدا نشد")
        return

    # ===== ۳. ادغام =====
    merged = []
    seen_texts = set()

    for path in files:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                items = json.load(f)

            for item in items:
                text = item.get('text', '').strip()
                if not text:
                    continue
                # حذف تکراری بر اساس متن
                if text in seen_texts:
                    print(f"⚠️ تکراری رد شد: {text[:40]}...")
                    continue
                seen_texts.add(text)
                merged.append(item)

            print(f"✅ {os.path.basename(path)}: {len(items)} رکورد")

        except Exception as e:
            print(f"❌ خطا در {path}: {e}")

    # ===== ۴. ذخیره =====
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}")
    print(f"✅ دیتاست نهایی: {OUTPUT_PATH}")
    print(f"   تعداد رکورد: {len(merged)}")
    print(f"   فایل‌های batch: {len(files)}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()