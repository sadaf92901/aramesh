from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine

db = SQLAlchemy()


# ============================================================
# فعال‌سازی Foreign Key در SQLite
# ============================================================
# به‌صورت پیش‌فرض، SQLite FK constraint رو چک نمی‌کنه!
# این تابع باعث می‌شه چک بشه.

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """فعال‌سازی FK در SQLite"""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()