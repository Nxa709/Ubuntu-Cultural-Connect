"""Add rejection columns to the experiences table (PostgreSQL/SQLite-safe).

Usage:
    python add_rejection_columns.py                 # uses DATABASE_URL
    Set POSTGRESQL_DATABASE_URL to target a remote PostgreSQL instead.
"""
import os
import sys; sys.path.insert(0, '.')
from sqlalchemy import create_engine, text, inspect
from config import DATABASE_URL, POSTGRESQL_DATABASE_URL

def add_columns():
    if os.getenv("TARGET_DATABASE_URL"):
        url = os.getenv("TARGET_DATABASE_URL")
    elif "postgres" in POSTGRESQL_DATABASE_URL and "sqlite" in DATABASE_URL:
        url = POSTGRESQL_DATABASE_URL
    else:
        url = DATABASE_URL
    engine = create_engine(url, connect_args={"check_same_thread": False} if "sqlite" in url else {})
    insp = inspect(engine)
    existing = [c["name"] for c in insp.get_columns("experiences")]

    with engine.connect() as conn:
        if "rejection_reason" not in existing:
            conn.execute(text("ALTER TABLE experiences ADD COLUMN rejection_reason VARCHAR"))
            print("Added: rejection_reason")
        else:
            print("Already exists: rejection_reason")

        if "rejected_at" not in existing:
            conn.execute(text("ALTER TABLE experiences ADD COLUMN rejected_at TIMESTAMP"))
            print("Added: rejected_at")
        else:
            print("Already exists: rejected_at")
        conn.commit()
    print("Done.")

if __name__ == "__main__":
    add_columns()
