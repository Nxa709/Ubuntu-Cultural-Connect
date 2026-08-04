import random
from datetime import datetime, timedelta, timezone
from database import SessionLocal, engine, Base
from models.user import User, UserRole
from models.experience import Experience, Rating, CulturalCategory
from services.auth_service import hash_password

Base.metadata.create_all(bind=engine)
db = SessionLocal()

admin = db.query(User).filter(User.email == "admin@ubuntu.com").first()
if not admin:
    admin = User(
        email="admin@ubuntu.com",
        hashed_password=hash_password("Admin123!"),
        full_name="System Admin",
        phone_number="0800000000",
        role=UserRole.admin,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    print("Created admin user: admin@ubuntu.com / Admin123!")
else:
    print("Admin user already exists")

owner = db.query(User).filter(User.role == UserRole.business_owner).first()
tourists = db.query(User).filter(User.role == UserRole.tourist).all()

unapproved_exps = [
    ("Zulu Beadwork Workshop", "Learn the ancient art of Zulu beadwork from master crafters in rural KwaZulu-Natal.", "Crafts & Art", "Eshowe, KwaZulu-Natal", "KwaZulu-Natal"),
    ("Sangoma Healing Ceremony", "Experience a traditional healing ceremony led by a respected sangoma in Limpopo.", "Traditional Healing", "Polokwane, Limpopo", "Limpopo"),
    ("Ndebele Mural Painting", "Paint vibrant Ndebele murals under the guidance of local women artists.", "Crafts & Art", "Middelburg, Mpumalanga", "Mpumalanga"),
]

created_exps = 0
for title, desc, cat, loc, prov in unapproved_exps:
    existing = db.query(Experience).filter(Experience.title == title).first()
    if existing:
        continue
    e = Experience(
        title=title,
        description=desc,
        category=cat,
        location=loc,
        province=prov,
        price=0.0,
        duration_hours=3.0,
        max_participants=8,
        owner_id=owner.id,
        is_active=True,
        is_approved=False,
    )
    db.add(e)
    created_exps += 1

db.commit()
print(f"Created {created_exps} unapproved hotspots")

unapproved_comments = [
    (5, "Absolutely magical experience! The beadwork was stunning."),
    (4, "Very educational, I learnt so much about Zulu culture."),
    (3, "Interesting but could be longer."),
    (5, "Highly recommend this to anyone visiting South Africa!"),
    (2, "The location was hard to find, but worth the trip."),
    (4, "Beautiful crafts and wonderful people."),
    (1, "This was not what I expected. Very disappointing."),
    (5, "A must-do cultural experience!"),
]

if tourists:
    unapproved_exps_from_db = db.query(Experience).filter(Experience.is_approved == False).all()
    created_comments = 0
    for exp in unapproved_exps_from_db:
        tourist = random.choice(tourists)
        existing = db.query(Rating).filter(
            Rating.user_id == tourist.id,
            Rating.experience_id == exp.id,
        ).first()
        if existing:
            continue
        score, comment = random.choice(unapproved_comments)
        r = Rating(
            user_id=tourist.id,
            experience_id=exp.id,
            score=score,
            comment=comment,
            is_approved=False,
        )
        db.add(r)
        created_comments += 1
    db.commit()
    print(f"Created {created_comments} unapproved comments")
else:
    print("No tourists found, skipping comment seeding")

db.close()
print("\nAdmin login: admin@ubuntu.com / Admin123!")
