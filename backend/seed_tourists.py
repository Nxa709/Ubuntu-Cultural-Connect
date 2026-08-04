from database import SessionLocal
from models.user import User, UserRole
from services.auth_service import hash_password

db = SessionLocal()

tourists = [
    ("Sipho Ndaba", "sipho@test.com", "0821111111"),
    ("Thandiwe Molefe", "thandiwe@test.com", "0822222222"),
    ("Lerato Mokoena", "lerato@test.com", "0823333333"),
    ("Nomsa Dlamini", "nomsa@test.com", "0824444444"),
    ("Bongani Zulu", "bongani@test.com", "0825555555"),
    ("Zanele Khumalo", "zanele@test.com", "0826666666"),
    ("Mandla Mthembu", "mandla@test.com", "0827777777"),
    ("Ayanda Sithole", "ayanda@test.com", "0828888888"),
    ("Thabiso Mabaso", "thabiso@test.com", "0829999999"),
    ("Nomvula Zulu", "nomvula@test.com", "0820000000"),
]

created = 0
for name, email, phone in tourists:
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        continue
    u = User(
        email=email,
        hashed_password=hash_password("Test123!"),
        full_name=name,
        phone_number=phone,
        role=UserRole.tourist,
    )
    db.add(u)
    created += 1

db.commit()
db.close()
print(f"Created {created} tourist accounts")
