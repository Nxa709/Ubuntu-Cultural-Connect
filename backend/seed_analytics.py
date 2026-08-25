"""Populate the analytics tables so every business-owner account looks like an
active, healthy business for the demo.

What this adds:
  - ~30 extra tourist accounts (varied countries / local-vs-international)
  - itinerary adds for EVERY experience (~12-18 each => each host 24-36 total)
  - profile_view / search_appearance / contact_click events derived from adds
  - a few extra recent ratings per experience (so Recent Reviews + star bar fill up)

Time-stamps are spread over the last ~90 days, across all weekdays and with a
realistic hour-of-day distribution (morning + evening peaks).

Idempotent: run again and it resets only the rows it owns.

Run from the backend directory:
    python seed_analytics.py
"""
import random
from datetime import datetime, timedelta, timezone

from database import SessionLocal, engine, Base
from models.user import User, UserRole
from models.experience import (
    Experience, ExperienceEvent, ItineraryAdd, Rating,
)
from services.auth_service import hash_password

random.seed(2026)
Base.metadata.create_all(bind=engine)
db = SessionLocal()

NOW = datetime.now(timezone.utc)

# ── 1. Extra tourists ─────────────────────────────────────────────
TOURIST_PASS = hash_password("Tourist123!")

new_tourists = [
    # (name, email, phone, visitor_type, country)
    ("Naledi Mhlongo", "tourist01@demo.com", "082 600 0001", "local", "South Africa"),
    ("Bongani Dube", "tourist02@demo.com", "082 600 0002", "local", "South Africa"),
    ("Ayanda Ntuli", "tourist03@demo.com", "082 600 0003", "local", "South Africa"),
    ("Zinhle Khanyile", "tourist04@demo.com", "082 600 0004", "local", "South Africa"),
    ("Siphiwe Mthembu", "tourist05@demo.com", "082 600 0005", "local", "South Africa"),
    ("Luyanda Cele", "tourist06@demo.com", "082 600 0006", "local", "South Africa"),
    ("Nosipho Gcabashe", "tourist07@demo.com", "082 600 0007", "local", "South Africa"),
    ("Kwanele Mthembu", "tourist08@demo.com", "082 600 0008", "local", "South Africa"),
    ("Thandazile Zuma", "tourist09@demo.com", "082 600 0009", "local", "South Africa"),
    ("Minenhle Dlamini", "tourist10@demo.com", "082 600 0010", "local", "South Africa"),
    ("Oliver Bennett", "tourist11@demo.com", "082 600 0011", "international", "United Kingdom"),
    ("Charlotte Hughes", "tourist12@demo.com", "082 600 0012", "international", "United Kingdom"),
    ("Lena Fischer", "tourist13@demo.com", "082 600 0013", "international", "Germany"),
    ("Lucas Müller", "tourist14@demo.com", "082 600 0014", "international", "Germany"),
    ("Emma Rousseau", "tourist15@demo.com", "082 600 0015", "international", "France"),
    ("Diego Santos", "tourist16@demo.com", "082 600 0016", "international", "Brazil"),
    ("Aisha Patel", "tourist17@demo.com", "082 600 0017", "international", "India"),
    ("Yuki Tanaka", "tourist18@demo.com", "082 600 0018", "international", "Japan"),
    ("Wei Zhang", "tourist19@demo.com", "082 600 0019", "international", "China"),
    ("Sophie van Dijk", "tourist20@demo.com", "082 600 0020", "international", "Netherlands"),
    ("Jack Wilson", "tourist21@demo.com", "082 600 0021", "international", "United States"),
    ("Chloé Dubois", "tourist22@demo.com", "082 600 0022", "international", "Belgium"),
    ("Marco Rossi", "tourist23@demo.com", "082 600 0023", "international", "Italy"),
    ("Kwame Mensah", "tourist24@demo.com", "082 600 0024", "international", "Ghana"),
    ("Wanjiku Kamau", "tourist25@demo.com", "082 600 0025", "international", "Kenya"),
    ("Thabo Marobe", "tourist26@demo.com", "082 600 0026", "international", "Botswana"),
    ("Amina Hassan", "tourist27@demo.com", "082 600 0027", "international", "Nigeria"),
    ("Tariro Ncube", "tourist28@demo.com", "082 600 0028", "international", "Zimbabwe"),
    ("Sofia Andrade", "tourist29@demo.com", "082 600 0029", "international", "Portugal"),
    ("Anna Nowak", "tourist30@demo.com", "082 600 0030", "international", "Poland"),
]

tourist_objs = []
for name, email, phone, vtype, country in new_tourists:
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        tourist_objs.append(existing)
        continue
    u = User(
        email=email, hashed_password=TOURIST_PASS, full_name=name,
        phone_number=phone, role=UserRole.tourist,
        visitor_type=vtype, country=country, is_verified=True,
    )
    db.add(u)
    tourist_objs.append(u)

# Also include the original seeded tourists so adds come from a broad pool.
for t in db.query(User).filter(User.role == UserRole.tourist).all():
    if t not in tourist_objs:
        tourist_objs.append(t)

db.flush()

all_experiences = db.query(Experience).all()
exp_ids = [e.id for e in all_experiences]
print(f"Tourists available: {len(tourist_objs)} | Experiences: {len(all_experiences)}")

# ── 2. Reset rows we own ──────────────────────────────────────────
db.query(ExperienceEvent).delete()
db.query(ItineraryAdd).delete()
new_tourist_ids = [t.id for t in tourist_objs]
db.query(Rating).filter(Rating.user_id.in_(new_tourist_ids)).delete()
db.commit()

# ── 3. Helpers for realistic time stamps ──────────────────────────
# Hour-of-day weights: morning (9a-12p) and evening (6p-10p) peaks.
HOUR_WEIGHTS = [1, 1, 1, 1, 1, 1, 2, 3, 4, 7, 8, 8, 7, 6, 6, 6, 6, 6, 8, 9, 9, 8, 5, 2]
HOURS = list(range(24))


def random_datetime(recency_bias=0.65, max_days=90):
    """A timestamp in the last `max_days` days, biased toward recent."""
    if random.random() < recency_bias:
        days_back = random.randint(0, max(0, int(max_days * 0.4)))
    else:
        days_back = random.randint(int(max_days * 0.4), max_days)
    day = NOW - timedelta(days=days_back)
    hour = random.choices(HOURS, weights=HOUR_WEIGHTS, k=1)[0]
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return day.replace(hour=hour, minute=minute, second=second, microsecond=0)


# ── 4. Itinerary adds + events ────────────────────────────────────
comment_templates = [
    "Absolutely incredible experience! The hosts were so welcoming and I learned so much about the culture.",
    "This was the highlight of my trip to South Africa. Truly authentic and well-organised.",
    "Amazing! I would recommend this to anyone visiting KwaZulu-Natal.",
    "A beautiful cultural experience. The storytelling was captivating and the food was delicious.",
    "So glad I did this. It gave me a deep appreciation for South African heritage.",
    "The guides were knowledgeable and passionate. Worth every rand.",
    "A must-do for anyone interested in authentic South African culture.",
    "Wonderful from start to finish. The attention to cultural detail was impressive.",
    "Loved every minute of this experience. The community was so warm and inviting.",
    "This changed my perspective on South Africa. Beyond the tourist trail.",
]

adds = []
events = []
ratings = []

for exp in all_experiences:
    n_adds = random.randint(12, 18)  # each host has 2 experiences -> 24-36 total
    # Keep some visitors local so the Local/International pie stays balanced.
    for _ in range(n_adds):
        user = random.choice(tourist_objs)
        when = random_datetime()

        # The tourist viewed the profile shortly before adding it.
        events.append(ExperienceEvent(
            experience_id=exp.id, event_type="profile_view",
            user_id=user.id,
            created_at=when - timedelta(minutes=random.randint(5, 120)),
        ))
        # Some browsed again a day or two earlier.
        if random.random() < 0.55:
            events.append(ExperienceEvent(
                experience_id=exp.id, event_type="profile_view",
                user_id=user.id,
                created_at=when - timedelta(days=random.randint(1, 4), hours=random.randint(1, 10)),
            ))
        # The hotspot surfaced in a search during planning.
        for _ in range(random.randint(1, 3)):
            events.append(ExperienceEvent(
                experience_id=exp.id, event_type="search_appearance",
                user_id=user.id,
                created_at=when - timedelta(days=random.randint(0, 4), hours=random.randint(1, 20)),
            ))
        # A share of interested visitors click contact / booking.
        if random.random() < 0.42:
            events.append(ExperienceEvent(
                experience_id=exp.id, event_type="contact_click",
                user_id=user.id,
                created_at=when + timedelta(minutes=random.randint(5, 300)),
            ))

        adds.append(ItineraryAdd(
            user_id=user.id, experience_id=exp.id, created_at=when,
        ))

    # A few extra "browsing" profile views from visitors who never added.
    extra_views = random.randint(3, 8)
    for _ in range(extra_views):
        user = random.choice(tourist_objs)
        events.append(ExperienceEvent(
            experience_id=exp.id, event_type="profile_view",
            user_id=user.id,
            created_at=random_datetime(),
        ))

    # 2-4 fresh ratings so Recent Reviews + the star bar look live.
    n_new_ratings = random.randint(2, 4)
    existing_raters = set()
    for _ in range(n_new_ratings):
        user = random.choice(tourist_objs)
        if user.id in existing_raters:
            continue
        existing_raters.add(user.id)
        score = random.choices([3, 4, 4, 5, 5, 5], k=1)[0]
        comment = random.choice(comment_templates) if score >= 4 else "Decent experience overall."
        ratings.append(Rating(
            user_id=user.id, experience_id=exp.id,
            score=score, comment=comment, is_approved=True,
            created_at=random_datetime(recency_bias=0.8, max_days=60),
        ))

print(f"  itinerary adds to insert: {len(adds)}")
print(f"  events to insert:        {len(events)}")
print(f"  ratings to insert:       {len(ratings)}")

db.add_all(adds)
db.flush()
db.add_all(events)
db.add_all(ratings)
db.commit()

# ── 5. Summary ────────────────────────────────────────────────────
from collections import Counter
hosts = db.query(User).filter(User.role == UserRole.business_owner).all()
print("\nPer-host itinerary adds (total):")
for h in hosts:
    total = db.query(ItineraryAdd).join(Experience).filter(Experience.owner_id == h.id).count()
    pv = (db.query(ExperienceEvent).join(Experience)
          .filter(Experience.owner_id == h.id, ExperienceEvent.event_type == "profile_view").count())
    sc = (db.query(ExperienceEvent).join(Experience)
          .filter(Experience.owner_id == h.id, ExperienceEvent.event_type == "search_appearance").count())
    ct = (db.query(ExperienceEvent).join(Experience)
          .filter(Experience.owner_id == h.id, ExperienceEvent.event_type == "contact_click").count())
    print(f"  {h.email:<26} adds={total:<3} profile_views={pv:<4} searches={sc:<4} contacts={ct}")

print("\nTotals:")
print(f"  itinerary_adds:  {db.query(ItineraryAdd).count()}")
print(f"  experience_events: {db.query(ExperienceEvent).count()}")
print(f"  ratings:         {db.query(Rating).count()}")

db.close()
print("\nDone. Log in as any host (Host123!) and open /analytics.")
