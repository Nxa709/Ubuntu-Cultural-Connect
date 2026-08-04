from database import engine, Base, SessionLocal
from models.user import User, UserRole
from models.experience import Experience, CulturalCategory
from services.auth_service import hash_password

Base.metadata.create_all(bind=engine)
db = SessionLocal()

if db.query(Experience).count() == 0:
    owner = db.query(User).filter(User.role == UserRole.business_owner).first()
    if not owner:
        owner = User(
            email="host@ubuntu.com",
            hashed_password=hash_password("Host123!"),
            full_name="Sipho Dlamini",
            phone_number="0821112222",
            role=UserRole.business_owner,
        )
        db.add(owner)
        db.flush()

    experiences = [
        Experience(title="Traditional Cooking Class", description="Learn to cook bunny chow, bobotie and potjiekos in a real South African kitchen with a local chef.", category=CulturalCategory.traditional_cooking, location="Durban, KwaZulu-Natal", province="KwaZulu-Natal", price=450, duration_hours=3, max_participants=8, owner_id=owner.id),
        Experience(title="Soweto Township Tour", description="Explore the history and culture of Soweto, visiting landmarks like Vilakazi Street and the Apartheid Museum.", category=CulturalCategory.township_life, location="Soweto, Gauteng", province="Gauteng", price=350, duration_hours=4, max_participants=15, owner_id=owner.id),
        Experience(title="Zulu Cultural Experience", description="Witness traditional Zulu dance, music and storytelling by local performers.", category=CulturalCategory.music_dance, location="Ulundi, KwaZulu-Natal", province="KwaZulu-Natal", price=500, duration_hours=5, max_participants=20, owner_id=owner.id),
        Experience(title="Cape Malay Storytelling Evening", description="Hear indigenous stories passed down through generations while enjoying traditional Cape Malay snacks.", category=CulturalCategory.storytelling, location="Bo-Kaap, Cape Town", province="Western Cape", price=280, duration_hours=2, max_participants=12, owner_id=owner.id),
        Experience(title="Beadwork Craft Workshop", description="Create traditional Zulu beadwork with local artisans. Take home your own handmade piece.", category=CulturalCategory.crafts, location="KwaDukuza, KwaZulu-Natal", province="KwaZulu-Natal", price=380, duration_hours=3, max_participants=10, owner_id=owner.id),
        Experience(title="Heritage Walk Johannesburg", description="Walk through Johannesburg's historic streets learning about gold rush history and struggle heritage.", category=CulturalCategory.heritage_tours, location="Johannesburg, Gauteng", province="Gauteng", price=200, duration_hours=3, max_participants=20, owner_id=owner.id),
        Experience(title="Drumming Circle Experience", description="Join a traditional African drumming circle, learn rhythms and their cultural significance.", category=CulturalCategory.music_dance, location="Cape Town, Western Cape", province="Western Cape", price=320, duration_hours=2.5, max_participants=15, owner_id=owner.id),
        Experience(title="Rural Village Homestay", description="Experience authentic rural South African village life. Farm-to-table meals, cattle herding, and stargazing.", category=CulturalCategory.rural_heritage, location="Eastern Cape, Rural Village", province="Eastern Cape", price=1200, duration_hours=48, max_participants=6, owner_id=owner.id),
        Experience(title="Shisa Nyama BBQ Experience", description="Learn the art of South African braai at a local shisa nyama with music and community vibes.", category=CulturalCategory.township_life, location="Soweto, Gauteng", province="Gauteng", price=250, duration_hours=3, max_participants=12, owner_id=owner.id),
        Experience(title="Traditional Herbal Medicine Walk", description="Walk with a traditional healer through indigenous forest, learning about medicinal plants and their uses.", category=CulturalCategory.traditional_healing, location="Hazyview, Mpumalanga", province="Mpumalanga", price=400, duration_hours=4, max_participants=8, owner_id=owner.id),
        Experience(title="Tsonga Fish Braai & Dance", description="Experience Tsonga culture with traditional fish braai, xiTsonga dance and music.", category=CulturalCategory.music_dance, location="Mukula, Limpopo", province="Limpopo", price=350, duration_hours=4, max_participants=10, owner_id=owner.id),
        Experience(title="Weaving & Basket Making", description="Learn traditional Xhosa basket weaving techniques from master craftswomen.", category=CulturalCategory.textile_weaving, location="Alice, Eastern Cape", province="Eastern Cape", price=300, duration_hours=3, max_participants=8, owner_id=owner.id),
    ]

    db.add_all(experiences)
    db.commit()
    print(f"Seeded {len(experiences)} experiences")
else:
    print("Experiences already exist")

db.close()
