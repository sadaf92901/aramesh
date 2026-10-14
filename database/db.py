# ============================================================
# database/db.py
# ============================================================

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine

db = SQLAlchemy()


# ============================================================
# SQLite: فعال‌سازی Foreign Key
# ============================================================
# فقط برای SQLite — PostgreSQL خودش FK رو چک می‌کنه.

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """فعال‌سازی FK در SQLite"""
    # ===== 🆕 چک کن SQLite هست =====
    module_name = dbapi_connection.__class__.__module__
    if 'sqlite' in module_name:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
