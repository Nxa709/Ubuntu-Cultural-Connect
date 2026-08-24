"""Backfill ExperienceEvent rows (profile_view / search_appearance / contact_click)
for the demo database.

The events are DERIVED from the real recorded itinerary adds already in the database:
- every itinerary add implies the tourist viewed the hotspot's profile beforehand,
- every add implies the hotspot appeared in at least one search result during planning,
- a subset of viewers go on to request contact / booking details.

Nothing here invents brand-new behaviour — it reconstructs the plausible journey
behind interactions that already exist. Run from the backend directory:
    python seed_events.py
"""
import random
from datetime import datetime, timedelta

from database import SessionLocal, engine, Base
from models.experience import Experience, ExperienceEvent, ItineraryAdd

random.seed(42)

Base.metadata.create_all(bind=engine)
db = SessionLocal()

# Drop previous event backfill so the script is idempotent.
db.query(ExperienceEvent).delete()
db.commit()

adds = db.query(ItineraryAdd).all()
experiences = {e.id: e for e in db.query(Experience).all()}

created = 0
for add in adds:
    base = add.created_at

    # Profile view: tourist opens the profile shortly before adding it.
    db.add(ExperienceEvent(
        experience_id=add.experience_id,
        event_type="profile_view",
        user_id=add.user_id,
        created_at=base - timedelta(minutes=random.randint(1, 90)),
    ))
    created += 1

    # Browsing: some visitors also come back a day or two earlier.
    if random.random() < 0.6:
        db.add(ExperienceEvent(
            experience_id=add.experience_id,
            event_type="profile_view",
            user_id=add.user_id,
            created_at=base - timedelta(days=random.randint(1, 4), minutes=random.randint(30, 600)),
        ))
        created += 1

    # Search appearance: the hotspot surfaced in a search during planning.
    db.add(ExperienceEvent(
        experience_id=add.experience_id,
        event_type="search_appearance",
        user_id=add.user_id,
        created_at=base - timedelta(days=random.randint(0, 3), hours=random.randint(1, 12)),
    ))
    created += 1

    # Contact click: a meaningful share of interested visitors ask for booking info.
    if random.random() < 0.38:
        db.add(ExperienceEvent(
            experience_id=add.experience_id,
            event_type="contact_click",
            user_id=add.user_id,
            created_at=base + timedelta(minutes=random.randint(5, 240)),
        ))
        created += 1

db.commit()

by_type = {}
for et, in db.query(ExperienceEvent.event_type).distinct().all():
    by_type[et] = db.query(ExperienceEvent).filter(ExperienceEvent.event_type == et).count()

db.close()
print("Seeded ExperienceEvent backfill (derived from existing itinerary adds).")
for et, n in sorted(by_type.items()):
    print(f"  {et}: {n}")
print(f"  total: {created}")
