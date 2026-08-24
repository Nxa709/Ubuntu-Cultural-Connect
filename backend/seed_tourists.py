from database import SessionLocal
from models.user import User, UserRole
from services.auth_service import hash_password

db = SessionLocal()

tourists = [
    ("Sipho Ndaba", "sipho@test.com", "0821111111", "local", "South Africa"),
    ("Thandiwe Molefe", "thandiwe@test.com", "0822222222", "local", "South Africa"),
    ("Lerato Mokoena", "lerato@test.com", "0823333333", "international", "United Kingdom"),
    ("Nomsa Dlamini", "nomsa@test.com", "0824444444", "international", "Germany"),
    ("Bongani Zulu", "bongani@test.com", "0825555555", "local", "South Africa"),
    ("Zanele Khumalo", "zanele@test.com", "0826666666", "international", "United States"),
    ("Mandla Mthembu", "mandla@test.com", "0827777777", "local", "South Africa"),
    ("Ayanda Sithole", "ayanda@test.com", "0828888888", "international", "Australia"),
    ("Thabiso Mabaso", "thabiso@test.com", "0829999999", "international", "France"),
    ("Nomvula Zulu", "nomvula@test.com", "0820000000", "local", "South Africa"),
]

created = 0
for name, email, phone, visitor_type, country in tourists:
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        continue
    u = User(
        email=email,
        hashed_password=hash_password("Test123!"),
        full_name=name,
        phone_number=phone,
        role=UserRole.tourist,
        visitor_type=visitor_type,
        country=country,
    )
    db.add(u)
    created += 1

db.commit()
db.close()
print(f"Created {created} tourist accounts")
