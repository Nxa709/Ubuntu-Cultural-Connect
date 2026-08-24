"""Diversify tourist countries so business-owner analytics show a range of origins.

Idempotent. Only touches role == 'tourist' users.
"""
import sys

sys.path.insert(0, ".")
from sqlalchemy.orm import sessionmaker
from database import engine
from models.user import User

Session = sessionmaker(bind=engine)
db = Session()

# (user id, visitor_type, country, phone)
TOURISTS = {
    6: ("local", "South Africa", "+27 82 555 3001"),
    7: ("local", "South Africa", "+27 82 555 3002"),
    8: ("international", "United Kingdom", "+44 20 7946 3003"),
    9: ("international", "India", "+91 98 5555 3004"),
    10: ("international", "United States", "+1 202 555 3005"),
    11: ("international", "Kenya", "+254 712 555 3006"),
    12: ("local", "South Africa", "+27 82 555 3007"),
    13: ("international", "Germany", "+49 30 555 3008"),
    14: ("international", "France", "+33 1 55 555 3009"),
    15: ("international", "Canada", "+1 416 555 3010"),
}

updated = 0
for uid, (vtype, country, phone) in TOURISTS.items():
    u = db.query(User).filter(User.id == uid).first()
    if u and u.role.value == "tourist":
        u.visitor_type = vtype
        u.country = country
        u.phone_number = phone
        updated += 1

db.commit()
print(f"Updated {updated} tourists with new countries.")

rows = db.query(User.id, User.email, User.visitor_type, User.country).filter(
    User.role == "tourist"
).all()
for r in rows:
    print(" ", r)

db.close()
