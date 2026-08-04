"""Add performance indexes to PostgreSQL database."""
import sys; sys.path.insert(0, '.')
from sqlalchemy import create_engine, text
from config import DATABASE_URL

idx = [
    ("idx_experiences_owner", "CREATE INDEX IF NOT EXISTS idx_experiences_owner ON experiences(owner_id)"),
    ("idx_experiences_category", "CREATE INDEX IF NOT EXISTS idx_experiences_category ON experiences(category)"),
    ("idx_experiences_active_approved", "CREATE INDEX IF NOT EXISTS idx_experiences_active_approved ON experiences(is_active, is_approved)"),
    ("idx_ratings_experience", "CREATE INDEX IF NOT EXISTS idx_ratings_experience ON ratings(experience_id)"),
    ("idx_ratings_user", "CREATE INDEX IF NOT EXISTS idx_ratings_user ON ratings(user_id)"),
    ("idx_ratings_approved", "CREATE INDEX IF NOT EXISTS idx_ratings_approved ON ratings(is_approved)"),
    ("idx_trip_days_experience", "CREATE INDEX IF NOT EXISTS idx_trip_days_experience ON trip_days(experience_id)"),
    ("idx_notifications_user", "CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id)"),
    ("idx_travel_journals_user", "CREATE INDEX IF NOT EXISTS idx_travel_journals_user ON travel_journals(user_id)"),
]

def add_indexes():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        for name, sql in idx:
            conn.execute(text(sql))
            print(f"  {name} ... OK")
        conn.commit()
    print("All indexes created.")

if __name__ == "__main__":
    add_indexes()
