# ============================================================
# WSGI entry point برای production
# ============================================================

from app import app, preload_services

# ===== لود سرویس‌ها =====
preload_services()

# ===== اجرا =====
if __name__ == "__main__":
    app.run()