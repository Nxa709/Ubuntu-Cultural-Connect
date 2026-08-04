import random
from datetime import datetime, timedelta, timezone
from database import SessionLocal
from models.user import User, UserRole
from models.experience import Experience, Rating

db = SessionLocal()

owner = db.query(User).filter(User.role == UserRole.business_owner).first()
tourists = db.query(User).filter(User.role == UserRole.tourist).all()

if not tourists:
    print("No tourists found. Register some tourist accounts first.")
    db.close()
    exit()

my_exps = db.query(Experience).filter(Experience.owner_id == owner.id).all()

if not my_exps:
    print("No experiences found for this owner.")
    db.close()
    exit()

comments = [
    "Amazing experience! Highly recommend.",
    "Great cultural immersion, loved every minute.",
    "The host was very welcoming and knowledgeable.",
    "Authentic and well-organized. Thank you!",
    "Unforgettable experience, a must-do!",
    "Learnt so much about the local culture.",
    "Perfect for families and solo travelers alike.",
    "The food was incredible and the stories even better.",
    "Would definitely do this again!",
    "A wonderful way to experience South Africa.",
    "Very professional and fun experience.",
    "The drumming circle was my highlight.",
    "Beautiful crafts and amazing people.",
    "Best cultural experience I've ever had.",
    "The storytelling evening was magical.",
]

ratings_created = 0
months_back = [0, 0, 0, 1, 1, 1, 2, 2, 3, 3, 4, 5]

for tourist in tourists:
    exp = random.choice(my_exps)
    existing = db.query(Rating).filter(
        Rating.user_id == tourist.id,
        Rating.experience_id == exp.id,
    ).first()
    if existing:
        continue

    score = random.choices([5, 4, 3, 2, 1], weights=[40, 30, 15, 10, 5])[0]
    comment = random.choice(comments) if random.random() > 0.3 else None

    days_offset = random.choice(months_back) * 30 + random.randint(0, 29)
    created = datetime.now(timezone.utc) - timedelta(days=days_offset)

    r = Rating(
        user_id=tourist.id,
        experience_id=exp.id,
        score=score,
        comment=comment,
        created_at=created,
    )
    db.add(r)
    ratings_created += 1

db.commit()
db.close()
print(f"Created {ratings_created} test ratings across {len(my_exps)} experiences")
