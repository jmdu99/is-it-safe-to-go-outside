# backend/storage/test_db_connection.py

from sqlalchemy import text
from backend.storage.db import get_connection

if __name__ == "__main__":
    with get_connection() as conn:
        result = conn.execute(text("SELECT 1"))
        print("Connection OK, SELECT 1 =", result.scalar())
