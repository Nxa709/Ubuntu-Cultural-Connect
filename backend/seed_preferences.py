"""Populate cultural preferences (user_preferences) so the Business Owner
Analytics "Interests" time-series has realistic data.

This is NON-DESTRUCTIVE: it only inserts/updates user_preferences rows for
tourist accounts. It never touches experiences, itinerary adds, events or
ratings, so it is safe to run against an existing (even production) database.

Run from the backend directory:
    python seed_preferences.py

To target a remote DB, set DATABASE_URL first, e.g.:
    $env:DATABASE_URL="postgresql://..."; python seed_preferences.py
"""
import random
from datetime import datetime, timedelta, timezone

from database import SessionLocal, engine, Base
from models.user import User, UserRole
from models.experience import UserPreference, CulturalCategory

random.seed(2026)
Base.metadata.create_all(bind=engine)

db = SessionLocal()
NOW = datetime.now(timezone.utc)
CATEGORIES = [c.value for c in CulturalCategory]

tourists = db.query(User).filter(User.role == UserRole.tourist).all()
created = updated = 0

for t in tourists:
    cats = ", ".join(random.sample(CATEGORIES, random.randint(1, 3)))
    when = NOW - timedelta(days=random.randint(0, 180))
    pref = db.query(UserPreference).filter(UserPreference.user_id == t.id).first()
    if pref:
        pref.categories = cats
        pref.updated_at = when
        updated += 1
    else:
        db.add(UserPreference(user_id=t.id, categories=cats, updated_at=when))
        created += 1

db.commit()

print(f"Tourists found:        {len(tourists)}")
print(f"Preferences created:   {created}")
print(f"Preferences updated:   {updated}")
print(f"Total user_preferences: {db.query(UserPreference).count()}")
db.close()
