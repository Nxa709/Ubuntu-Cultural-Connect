"""Set visitor_type/country on tourist users and seed itinerary adds.

Idempotent. Only updates tourists (role == 'tourist').
"""
import sys
import random
from datetime import datetime, timedelta, timezone

sys.path.insert(0, ".")
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL
from database import engine
from models.user import User
from models.experience import Experience, ItineraryAdd

Session = sessionmaker(bind=engine)
db = Session()

# (user id, visitor_type, country, phone)
TOURISTS = {
    6: ("local", "South Africa", "+27 82 555 3001"),
    7: ("local", "South Africa", "+27 82 555 3002"),
    8: ("international", "United Kingdom", "+44 20 7946 3003"),
    9: ("local", "South Africa", "+27 82 555 3004"),
    10: ("international", "United States", "+1 202 555 3005"),
    11: ("local", "South Africa", "+27 82 555 3006"),
    12: ("local", "South Africa", "+27 82 555 3007"),
    13: ("international", "Germany", "+49 30 555 3008"),
    14: ("international", "France", "+33 1 55 555 3009"),
}

# update tourists
for uid, (vtype, country, phone) in TOURISTS.items():
    u = db.query(User).filter(User.id == uid).first()
    if u and u.role.value == "tourist":
        u.visitor_type = vtype
        u.country = country
        u.phone_number = phone
db.commit()
print("Updated tourist visitor types/countries.")

# seed itinerary adds (only if almost empty)
existing = db.query(ItineraryAdd).count()
if existing < 20:
    exp_ids = [e.id for e in db.query(Experience.id).filter(
        Experience.is_active == True, Experience.is_approved == True).all()]
    tourist_ids = [uid for uid in TOURISTS.keys()]
    rnd = random.Random(7)
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    added = 0
    for eid in exp_ids:
        n = rnd.randint(2, 7)
        for _ in range(n):
            uid = rnd.choice(tourist_ids)
            days_ago = rnd.randint(0, 55)
            # favour daytime hours so Morning/Afternoon/Evening buckets are populated
            hour = rnd.choice([7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20])
            ts = now - timedelta(days=days_ago, hours=rnd.randint(0, 23 - hour), minutes=rnd.randint(0, 59))
            ts = ts.replace(hour=hour)
            db.add(ItineraryAdd(user_id=uid, experience_id=eid, trip_id=None, created_at=ts))
            added += 1
    db.commit()
    print(f"Seeded {added} itinerary adds.")
else:
    print(f"Itinerary adds already present ({existing}); skipping seed.")

db.close()
