# backend/storage/test_insert_computed.py

from datetime import datetime
from backend.storage.db import insert_risk_index

if __name__ == "__main__":
    now = datetime.utcnow().isoformat()

    # Test insertion indice
    insert_risk_index("TestVille", now, "vert")
    print("✔️ risk_index inserted with 'vert'")
