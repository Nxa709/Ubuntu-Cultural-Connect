"""Fresh seed with realistic dummy data for all actors."""
import random
from datetime import datetime, date, timedelta, timezone
from database import SessionLocal, engine, Base
from models.user import User, UserRole
from models.experience import (
    Experience, CulturalCategory, UserPreference, Trip, TripDay, Rating,
)
from services.auth_service import hash_password

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# ── Users ──────────────────────────────────────────────
ADMIN_PASS = hash_password("Admin123!")
HOST_PASS = hash_password("Host123!")
TOURIST_PASS = hash_password("Tourist123!")

admin = User(
    email="admin@ubuntu.com", hashed_password=ADMIN_PASS,
    full_name="Thabo Mokoena", phone_number="082 555 1001",
    role=UserRole.admin, is_verified=True,
)

# 25 business owners so the 50 hotspots stay at <= 3 per owner (2 each).
hosts = [
    User(email="sipho@ubuntu.com", hashed_password=HOST_PASS,
         full_name="Sipho Dlamini", phone_number="082 555 2001",
         role=UserRole.business_owner, is_verified=True),
    User(email="nomsa@ubuntu.com", hashed_password=HOST_PASS,
         full_name="Nomsa Khumalo", phone_number="082 555 2002",
         role=UserRole.business_owner, is_verified=True),
    User(email="pieter@ubuntu.com", hashed_password=HOST_PASS,
         full_name="Pieter van der Merwe", phone_number="082 555 2003",
         role=UserRole.business_owner, is_verified=True),
    User(email="zanele@ubuntu.com", hashed_password=HOST_PASS,
         full_name="Zanele Ndlovu", phone_number="082 555 2004",
         role=UserRole.business_owner, is_verified=True),
    User(email="host5@ubuntu.com", hashed_password=HOST_PASS,
         full_name="Naledi Mkhize", phone_number="082 555 2005",
         role=UserRole.business_owner, is_verified=True),
    User(email="host6@ubuntu.com", hashed_password=HOST_PASS,
         full_name="Thulani Zuma", phone_number="082 555 2006",
         role=UserRole.business_owner, is_verified=True),
    User(email="host7@ubuntu.com", hashed_password=HOST_PASS,
         full_name="Busisiwe Nkosi", phone_number="082 555 2007",
         role=UserRole.business_owner, is_verified=True),
    User(email="host8@ubuntu.com", hashed_password=HOST_PASS,
         full_name="Sibusiso Mahlangu", phone_number="082 555 2008",
         role=UserRole.business_owner, is_verified=True),
    User(email="host9@ubuntu.com", hashed_password=HOST_PASS,
         full_name="Lindiwe Mthembu", phone_number="082 555 2009",
         role=UserRole.business_owner, is_verified=True),
    User(email="host10@ubuntu.com", hashed_password=HOST_PASS,
         full_name="Mandla Khumalo", phone_number="082 555 2010",
         role=UserRole.business_owner, is_verified=True),
    User(email="host11@ubuntu.com", hashed_password=HOST_PASS,
         full_name="Ayanda Dlamini", phone_number="082 555 2011",
         role=UserRole.business_owner, is_verified=True),
    User(email="host12@ubuntu.com", hashed_password=HOST_PASS,
         full_name="Phumzile Mokoena", phone_number="082 555 2012",
         role=UserRole.business_owner, is_verified=True),
    User(email="host13@ubuntu.com", hashed_password=HOST_PASS,
         full_name="Jabulani Sithole", phone_number="082 555 2013",
         role=UserRole.business_owner, is_verified=True),
    User(email="host14@ubuntu.com", hashed_password=HOST_PASS,
         full_name="Nomvula Zulu", phone_number="082 555 2014",
         role=UserRole.business_owner, is_verified=True),
    User(email="host15@ubuntu.com", hashed_password=HOST_PASS,
         full_name="Thabo Ngubane", phone_number="082 555 2015",
         role=UserRole.business_owner, is_verified=True),
    User(email="host16@ubuntu.com", hashed_password=HOST_PASS,
         full_name="Zodwa Mchunu", phone_number="082 555 2016",
         role=UserRole.business_owner, is_verified=True),
    User(email="host17@ubuntu.com", hashed_password=HOST_PASS,
         full_name="Bongani Ntuli", phone_number="082 555 2017",
         role=UserRole.business_owner, is_verified=True),
    User(email="host18@ubuntu.com", hashed_password=HOST_PASS,
         full_name="Fikile Mavundla", phone_number="082 555 2018",
         role=UserRole.business_owner, is_verified=True),
    User(email="host19@ubuntu.com", hashed_password=HOST_PASS,
         full_name="Sanele Mthembu", phone_number="082 555 2019",
         role=UserRole.business_owner, is_verified=True),
    User(email="host20@ubuntu.com", hashed_password=HOST_PASS,
         full_name="Ntombi Gumede", phone_number="082 555 2020",
         role=UserRole.business_owner, is_verified=True),
    User(email="host21@ubuntu.com", hashed_password=HOST_PASS,
         full_name="Mlungisi Cele", phone_number="082 555 2021",
         role=UserRole.business_owner, is_verified=True),
    User(email="host22@ubuntu.com", hashed_password=HOST_PASS,
         full_name="Thandeka Mngoma", phone_number="082 555 2022",
         role=UserRole.business_owner, is_verified=True),
    User(email="host23@ubuntu.com", hashed_password=HOST_PASS,
         full_name="Vusi Mthethwa", phone_number="082 555 2023",
         role=UserRole.business_owner, is_verified=True),
    User(email="host24@ubuntu.com", hashed_password=HOST_PASS,
         full_name="Nompilo Zondi", phone_number="082 555 2024",
         role=UserRole.business_owner, is_verified=True),
    User(email="host25@ubuntu.com", hashed_password=HOST_PASS,
         full_name="Lungile Makhubu", phone_number="082 555 2025",
         role=UserRole.business_owner, is_verified=True),
]

tourists = [
    User(email="lebo@ubuntu.com", hashed_password=TOURIST_PASS,
         full_name="Lebo Matlala", phone_number="082 555 3001",
         role=UserRole.tourist, visitor_type="local", country="South Africa", is_verified=True),
    User(email="thandi@ubuntu.com", hashed_password=TOURIST_PASS,
         full_name="Thandiwe Molefe", phone_number="082 555 3002",
         role=UserRole.tourist, visitor_type="local", country="South Africa", is_verified=True),
    User(email="james@ubuntu.com", hashed_password=TOURIST_PASS,
         full_name="James van Zyl", phone_number="082 555 3003",
         role=UserRole.tourist, visitor_type="international", country="United Kingdom", is_verified=True),
    User(email="priya@ubuntu.com", hashed_password=TOURIST_PASS,
         full_name="Priya Naidoo", phone_number="082 555 3004",
         role=UserRole.tourist, visitor_type="international", country="India", is_verified=True),
    User(email="sarah@ubuntu.com", hashed_password=TOURIST_PASS,
         full_name="Sarah Botha", phone_number="082 555 3005",
         role=UserRole.tourist, visitor_type="local", country="South Africa", is_verified=True),
    User(email="michael@ubuntu.com", hashed_password=TOURIST_PASS,
         full_name="Michael Pretorius", phone_number="082 555 3006",
         role=UserRole.tourist, visitor_type="international", country="United States", is_verified=True),
    User(email="amahle@ubuntu.com", hashed_password=TOURIST_PASS,
         full_name="Amahle Zulu", phone_number="082 555 3007",
         role=UserRole.tourist, visitor_type="local", country="South Africa", is_verified=True),
    User(email="daniel@ubuntu.com", hashed_password=TOURIST_PASS,
         full_name="Daniel Mabaso", phone_number="082 555 3008",
         role=UserRole.tourist, visitor_type="international", country="Germany", is_verified=True),
]

db.add_all([admin] + hosts + tourists)
db.flush()

# ── Experiences (68 real KZN cultural tourism entries) ──
experiences_data = [
    # ═══════════════════════════════════════════════════════
    # 1. LOCAL RESTAURANTS (7)
    # ═══════════════════════════════════════════════════════
    ("Amanzimtoti Fisheries",
     "A beloved seaside restaurant in Amanzimtoti serving fresh line-caught fish, calamari, and classic South African seafood platters with ocean views.",
     CulturalCategory.traditional_cooking, "030 Majuba Rd, Amanzimtoti, 4126, KZN", "KwaZulu-Natal", 150, 1.5, 30, True),
    ("Ocean Basket Musgrave",
     "Popular seafood restaurant in Musgrave, Durban offering a wide selection of fresh fish, sushi, and Mediterranean-inspired seafood dishes in a family-friendly setting.",
     CulturalCategory.traditional_cooking, "123 Musgrave Rd, Musgrave, Durban, 4001, KZN", "KwaZulu-Natal", 250, 1.5, 30, True),
    ("The Spice Restaurant & Bar",
     "An upscale dining venue in uMhlanga offering a fusion of African and international cuisine, craft cocktails, and panoramic views of the Indian Ocean.",
     CulturalCategory.traditional_cooking, "27 Marine Terrace, uMhlanga, 4320, KZN", "KwaZulu-Natal", 200, 1.5, 30, True),
    ("Tiger's Milk Ballito",
     "A vibrant sports bar and restaurant in Ballito's Lifestyle Centre known for gourmet burgers, wood-fired pizzas, craft beers, and a lively social atmosphere.",
     CulturalCategory.traditional_cooking, "Shop 5, Lifestyle Centre, Ballito, 4420, KZN", "KwaZulu-Natal", 200, 1.5, 30, True),
    ("Moonshine Restaurant",
     "A Durban beachfront dining destination serving contemporary South African cuisine with an emphasis on fresh seafood and stunning ocean views.",
     CulturalCategory.traditional_cooking, "12 South Beach Ave, South Beach, Durban, 4001, KZN", "KwaZulu-Natal", 300, 1.5, 25, True),

    # ═══════════════════════════════════════════════════════
    # 2. MUSEUMS (7)
    # ═══════════════════════════════════════════════════════
    ("uShaka Maritime Museum",
     "Located at uShaka Marine World, this museum showcases the maritime history of Durban's harbour with historic vessels, naval artifacts, and interactive exhibits.",
     CulturalCategory.heritage_tours, "1 King Shaka Ave, Point, Durban, 4001, KZN", "KwaZulu-Natal", 80, 1.5, 30, True),
    ("KwaMuhle Museum",
     "Housed in the former Native Administration Department, this museum documents Durban's apartheid history and the struggle for democracy with powerful exhibits.",
     CulturalCategory.heritage_tours, "130 Bram Fischer Rd, Durban, 4001, KZN", "KwaZulu-Natal", 0, 1.5, 25, True),
    ("Durban Natural Science Museum",
     "Located in the Durban City Hall, this free museum features natural history exhibits including dinosaur fossils, taxidermy, and educational displays on southern African wildlife.",
     CulturalCategory.heritage_tours, "City Hall, 1st Floor, Durban, 4001, KZN", "KwaZulu-Natal", 0, 1.5, 30, True),
    ("Bergtheil Museum",
     "Set in a historic cotton plantation house in Westville, this museum tells the story of early German settlers and colonial life in the Durban area.",
     CulturalCategory.heritage_tours, "16 Flamingo Ave, Westville, 3630, KZN", "KwaZulu-Natal", 10, 1.5, 20, True),
    ("Natal Museum",
     "Pietermaritzburg's premier museum featuring natural science, cultural history, and a renowned collection of African art and artifacts spanning centuries.",
     CulturalCategory.heritage_tours, "237 Jabu Ndlovu St, Pietermaritzburg, 3201, KZN", "KwaZulu-Natal", 20, 1.5, 25, True),

    # ═══════════════════════════════════════════════════════
    # 3. NATURE RESERVES (7)
    # ═══════════════════════════════════════════════════════
    ("Kenneth Stainbank Nature Reserve",
     "A coastal forest reserve in Yellowwood Park featuring walking trails, bird hides, and diverse wildlife including zebra, impala, and over 200 bird species.",
     CulturalCategory.nature_wildlife, "Coedmore Rd, Yellowwood Park, Durban, 4001, KZN", "KwaZulu-Natal", 20, 2.0, 20, True),
    ("Palmiet Nature Reserve",
     "A 120-hectare reserve in Westville with trails along the Palmiet River, rich birdlife, and indigenous coastal forest perfect for nature walks and photography.",
     CulturalCategory.nature_wildlife, "10 Palmiet Rd, Westville, 3629, KZN", "KwaZulu-Natal", 0, 2.0, 20, True),
    ("Umgeni River Birding Trail",
     "A scenic birding trail along the Umgeni River in Durban, home to kingfishers, herons, fish eagles, and many other bird species in a tranquil riverine setting.",
     CulturalCategory.nature_wildlife, "603 The Ridge, Barcelona, Durban, 4001, KZN", "KwaZulu-Natal", 0, 2.0, 15, True),
    ("Burman Bush Nature Reserve",
     "A 40-hectare coastal forest reserve in Morningside, Durban with walking trails through indigenous bush, ideal for birdwatching and nature walks close to the city.",
     CulturalCategory.nature_wildlife, "152 Mariam Bee St, Morningside, Durban, 4001, KZN", "KwaZulu-Natal", 0, 1.5, 15, True),
    ("Paradise Valley Nature Reserve",
     "A 100-hectare reserve in New Germany featuring grasslands, forest trails, a river, and abundant birdlife — a peaceful escape into nature within the urban area.",
     CulturalCategory.nature_wildlife, "101 Paradise Rd, New Germany, 3610, KZN", "KwaZulu-Natal", 0, 2.0, 20, True),

    # ═══════════════════════════════════════════════════════
    # 4. GAME RESERVES (4)
    # ═══════════════════════════════════════════════════════
    ("Hluhluwe-iMfolozi Park — Hluhluwe Section",
     "Africa's oldest proclaimed nature reserve, this section offers exceptional game viewing of the Big Five in rolling hills of savannah and riverine forest.",
     CulturalCategory.nature_wildlife, "Hluhluwe, 3960, KZN", "KwaZulu-Natal", 120, 8.0, 15, True),
    ("Hluhluwe-iMfolozi Park — Memorial Gate",
     "The main entrance to this world-renowned game reserve, offering self-drive safaris, guided game drives, and access to over 90,000 hectares of pristine African bush.",
     CulturalCategory.nature_wildlife, "Hluhluwe, 3960, KZN", "KwaZulu-Natal", 120, 8.0, 20, True),
    ("uMkhuze Game Reserve",
     "A diverse reserve with wetlands, sand forest, and savannah, famous for its rhino population, birding hide, and ancient archaeological sites.",
     CulturalCategory.nature_wildlife, "uMkhuze, 3960, KZN", "KwaZulu-Natal", 120, 8.0, 15, True),
    ("iSimangaliso Wetland Park — Southern Section",
     "A UNESCO World Heritage Site featuring Lake St Lucia, hippos, crocodiles, and prolific birdlife in Africa's largest estuarine system.",
     CulturalCategory.nature_wildlife, "St Lucia, 3936, KZN", "KwaZulu-Natal", 200, 8.0, 20, True),

    # ═══════════════════════════════════════════════════════
    # 5. LODGES (6)
    # ═══════════════════════════════════════════════════════
    ("Mame Offers B&B",
     "A warm and welcoming bed and breakfast in Manguzi offering comfortable rooms, traditional Zulu hospitality, and a home-cooked breakfast to start your day.",
     CulturalCategory.accommodation, "P230, Manguzi, 3973, KZN", "KwaZulu-Natal", 450, 8.0, 10, True),
    ("Manguzi Guest Lodge",
     "A well-appointed guest lodge in Manguzi providing modern accommodation with en-suite rooms, a restaurant serving local cuisine, and easy access to nature reserves.",
     CulturalCategory.accommodation, "P230, Manguzi, 3973, KZN", "KwaZulu-Natal", 950, 8.0, 12, True),
    ("The Ndumo Wilderness Camp",
     "An eco-lodge within the Ndumo Game Reserve offering luxury tented accommodation, guided game drives, and birding experiences in a pristine wilderness setting.",
     CulturalCategory.accommodation, "Ndumo Game Reserve, 3973, KZN", "KwaZulu-Natal", 1200, 8.0, 8, True),
    ("Shakaland Zulu Cultural Village Lodge",
     "A renowned cultural lodge in Eshowe offering traditional Zulu beehive hut accommodation, spear-making demonstrations, and authentic Zulu dance and storytelling performances.",
     CulturalCategory.accommodation, "R66, Eshowe, 3815, KZN", "KwaZulu-Natal", 850, 8.0, 15, True),
    ("Emakhaya Lodge",
     "A comfortable urban lodge in Durban offering stylish rooms, a swimming pool, and easy access to the city's cultural attractions and beachfront.",
     CulturalCategory.accommodation, "34 Mbabane Rd, Durban, 4001, KZN", "KwaZulu-Natal", 750, 8.0, 12, True),

    # ═══════════════════════════════════════════════════════
    # 6. CULTURAL STORYTELLING (6)
    # ═══════════════════════════════════════════════════════
    ("The Storytelling Circle Durban",
     "A community storytelling gathering at Durban City Hall where local elders share folktales, oral histories, and Zulu legends passed down through generations.",
     CulturalCategory.storytelling, "Durban City Hall, Durban, 4001, KZN", "KwaZulu-Natal", 0, 2.0, 25, True),
    ("Gogo's Tales at Phansi Museum",
     "Experience the magic of Gogo (grandmother) storytelling at the Phansi Museum, where traditional Zulu tales come alive with song, dance, and audience participation.",
     CulturalCategory.storytelling, "500 Roberts Rd, Glenwood, Durban, 4001, KZN", "KwaZulu-Natal", 50, 1.5, 20, True),
    ("African Storytelling Nights at The Bat Centre",
     "An evening of African storytelling at Durban's Bat Centre featuring professional storytellers, live music, and tales from Zulu, Xhosa, and other South African traditions.",
     CulturalCategory.storytelling, "45 Maritime Pl, Durban, 4001, KZN", "KwaZulu-Natal", 80, 1.5, 30, True),
    ("Eshowe Cultural Storytelling Experience",
     "An immersive storytelling experience in Eshowe where local elders share the history of the Zulu kingdom, Shaka's legacy, and the traditions of King Cetshwayo's people.",
     CulturalCategory.storytelling, "17 Main St, Eshowe, 3815, KZN", "KwaZulu-Natal", 200, 2.5, 15, True),

    # ═══════════════════════════════════════════════════════
    # 7. CULTURAL ATTIRE MARKET (4)
    # ═══════════════════════════════════════════════════════
    ("Victoria Street Market",
     "Durban's iconic indoor market offering a vibrant array of African crafts, traditional clothing, beadwork, spices, and souvenirs in a historic building.",
     CulturalCategory.textile_weaving, "151 Victoria St, Durban, 4001, KZN", "KwaZulu-Natal", 0, 2.0, 30, True),
    ("Muthi Traditional Market",
     "Durban's famous muthi (traditional medicine) market where sangomas and inyangas sell herbs, roots, and traditional remedies alongside cultural attire and artifacts.",
     CulturalCategory.textile_weaving, "14 Glass St, Durban, 4001, KZN", "KwaZulu-Natal", 0, 2.0, 25, True),
    ("Inanda Craft & Design Centre",
     "A community craft centre in Inanda showcasing Zulu pottery, weaving, beadwork, and traditional attire made by local artisans, supporting sustainable livelihoods.",
     CulturalCategory.textile_weaving, "200 Inanda Rd, Inanda, 4300, KZN", "KwaZulu-Natal", 0, 2.0, 20, True),
    ("KwaMashu Craft Market",
     "A vibrant township market in KwaMashu offering authentic Zulu crafts, traditional clothing, beaded jewelry, and home decor made by local community artisans.",
     CulturalCategory.textile_weaving, "12 KwaMashu Hwy, KwaMashu, 4013, KZN", "KwaZulu-Natal", 0, 2.0, 25, True),

    # ═══════════════════════════════════════════════════════
    # 8. TRADITIONAL HEALING (5)
    # ═══════════════════════════════════════════════════════
    ("Sangoma Consultation & Cultural Talk",
     "An authentic sangoma consultation in Inanda where a traditional healer explains the calling process, divination using bones, and the role of ancestral spirits in healing.",
     CulturalCategory.traditional_healing, "Inanda, 4300, KZN", "KwaZulu-Natal", 250, 1.5, 5, True),
    ("Inyanga Traditional Healing Workshop",
     "A hands-on workshop in KwaMashu where an inyanga (herbalist) demonstrates traditional medicine preparation, plant identification, and the spiritual philosophy of healing.",
     CulturalCategory.traditional_healing, "34 Muthi Ln, KwaMashu, 4013, KZN", "KwaZulu-Natal", 300, 2.5, 8, True),
    ("Muthi Market & Healing Walk",
     "A guided walk through Durban's Muthi Market with a traditional healer who explains the medicinal uses of plants, roots, and herbs in Zulu traditional medicine.",
     CulturalCategory.traditional_healing, "14 Glass St, Durban, 4001, KZN", "KwaZulu-Natal", 0, 2.0, 10, True),
    ("Zulu Herbal Remedy Workshop",
     "Learn about the healing properties of indigenous KZN plants in this workshop led by a traditional healer who shares knowledge of herbal remedies passed down through families.",
     CulturalCategory.traditional_healing, "9 Plantation Rd, Durban, 4001, KZN", "KwaZulu-Natal", 200, 2.0, 8, True),
    ("Nongoma Traditional Healing Village",
     "Visit a traditional healing village in Nongoma where multiple sangomas practice ancestral healing, offering visitors insight into Zulu spiritual traditions and herbal medicine.",
     CulturalCategory.traditional_healing, "15 Sangoma St, Nongoma, 3950, KZN", "KwaZulu-Natal", 350, 3.0, 8, True),

    # ═══════════════════════════════════════════════════════
    # 9. HISTORICAL LANDMARKS (4)
    # ═══════════════════════════════════════════════════════
    ("The Old Fort",
     "Durban's oldest surviving building, built in 1837 by Voortrekkers, later used by British forces, now a heritage museum showcasing early colonial and military history.",
     CulturalCategory.heritage_tours, "71 Fort St, Durban, 4001, KZN", "KwaZulu-Natal", 0, 1.0, 20, True),
    ("Durban City Hall",
     "An architectural masterpiece built in 1910, housing the Natural Science Museum and art gallery, with beautiful Edwardian baroque design in the heart of the city.",
     CulturalCategory.heritage_tours, "150 Bram Fischer Rd, Durban, 4001, KZN", "KwaZulu-Natal", 0, 1.5, 30, True),
    ("Emmanuel Cathedral",
     "Durban's historic Catholic cathedral built in 1904, featuring stunning Gothic revival architecture, stained glass windows, and a rich multicultural parish history.",
     CulturalCategory.heritage_tours, "44 Cathedral Rd, Durban, 4001, KZN", "KwaZulu-Natal", 0, 1.0, 25, True),
    ("Juma Masjid Mosque",
     "The largest mosque in the Southern Hemisphere, located in Durban's Grey Street complex, featuring beautiful Islamic architecture and a rich history of the Indian Muslim community.",
     CulturalCategory.heritage_tours, "127 Grey St, Durban, 4001, KZN", "KwaZulu-Natal", 0, 1.0, 25, True),

    # ═══════════════════════════════════════════════════════
    # 10. CULTURAL THEATRE (5)
    # ═══════════════════════════════════════════════════════
    ("The Playhouse Theatre",
     "Durban's premier performing arts venue hosting theatre productions, ballet, opera, and music concerts in a beautifully restored Edwardian building.",
     CulturalCategory.music_dance, "29 Acutt St, Durban, 4001, KZN", "KwaZulu-Natal", 200, 2.5, 50, True),
    ("The Bat Centre",
     "Durban's vibrant waterfront arts centre showcasing African music, dance, theatre, and visual art in a dynamic creative space on the harbour edge.",
     CulturalCategory.music_dance, "45 Maritime Pl, Durban, 4001, KZN", "KwaZulu-Natal", 75, 3.0, 40, True),
    ("Elizabeth Sneddon Theatre",
     "A renowned theatre on the UKZN campus presenting cutting-edge drama, contemporary dance, and experimental performances by South Africa's leading artists.",
     CulturalCategory.music_dance, "1 Lennox Rd, Durban, 4001, KZN", "KwaZulu-Natal", 175, 2.5, 40, True),
    ("The Stable Theatre",
     "A historic Durban theatre that was a gathering place for anti-apartheid activists, now hosting community theatre, poetry slams, and emerging local talent.",
     CulturalCategory.music_dance, "104 Warwick Ave, Durban, 4001, KZN", "KwaZulu-Natal", 75, 2.0, 35, True),
    ("The Heritage Theatre",
     "An intimate Durban theatre venue presenting plays, live music, comedy shows, and cultural performances celebrating South African storytelling and performing arts.",
     CulturalCategory.music_dance, "12 Heritage Ave, Durban, 4001, KZN", "KwaZulu-Natal", 150, 2.5, 35, True),

    # ═══════════════════════════════════════════════════════
    # 11. CULTURAL TOURS (4)
    # ═══════════════════════════════════════════════════════
    ("Inanda Heritage Route Tour",
     "A full-day tour of Inanda's rich heritage sites including the Gandhi Settlement, Ohlange Institute, and the Shembe Church's holy village — a journey through South Africa's liberation history.",
     CulturalCategory.heritage_tours, "Inanda, 4300, KZN", "KwaZulu-Natal", 350, 8.0, 12, True),
    ("PheZulu Cultural Village & Safari",
     "Experience Zulu culture at PheZulu Village with traditional dancing, homestead tours, and a game drive through the Valley of a Thousand Hills for wildlife viewing.",
     CulturalCategory.heritage_tours, "5 PheZulu Rd, Botha's Hill, 3660, KZN", "KwaZulu-Natal", 450, 8.0, 15, True),
    ("The Zulu Experience",
     "An authentic half-day immersion in Zulu culture in Eshowe, including traditional dancing, beadwork demonstrations, spear-making, and a taste of Zulu cuisine.",
     CulturalCategory.heritage_tours, "5 Mountain Dr, Eshowe, 3815, KZN", "KwaZulu-Natal", 200, 4.0, 15, True),
    ("Valley of a Thousand Hills Tour",
     "A scenic full-day tour through the breathtaking Valley of a Thousand Hills with cultural stops, Zulu village visits, craft markets, and panoramic viewpoints.",
     CulturalCategory.heritage_tours, "10 Valley Rd, Hillcrest, 3610, KZN", "KwaZulu-Natal", 300, 8.0, 15, True),
]

# ── Image mapping ───────────────────────────────────────
def pick_image(title, cat):
    cat_map = {
        "Traditional Cooking": "/img/hotspots/food.jpg",
        "Storytelling": "/img/hotspots/storytelling.jpg",
        "Music & Dance": "/img/hotspots/theatre.jpg",
        "Crafts & Art": "/img/hotspots/crafts.jpg",
        "Heritage Tours": "/img/hotspots/museum.jpg",
        "Township Life": "/img/hotspots/market.jpg",
        "Rural Heritage": "/img/hotspots/landscape.jpg",
        "Traditional Healing": "/img/hotspots/herbs.jpg",
        "Textile & Weaving": "/img/hotspots/fabric.jpg",
        "Photography Tours": "/img/hotspots/road-trip.jpg",
        "Nature & Wildlife": "/img/hotspots/nature-forest.jpg",
        "Accommodation & Lodging": "/img/hotspots/lodge.jpg",
    }
    cat_val = cat.value if hasattr(cat, "value") else cat
    url = cat_map.get(cat_val, "/img/hotspots/landscape.jpg")
    # Override for specific well-known hotspots
    tl = title.lower()
    if any(w in tl for w in ["amanzimtoti", "moonshine", "ocean basket", "spice restaurant", "beach"]):
        url = "/img/hotspots/beachfront.jpg"
    elif "ushaka" in tl or "maritime" in tl:
        url = "/img/hotspots/beach.jpg"
    elif "hluhluwe" in tl or "imfolozi" in tl or "umkhuze" in tl:
        url = "/img/hotspots/elephant.jpg"
    elif "isimangaliso" in tl:
        url = "/img/hotspots/safari-sunset.jpg"
    elif "city hall" in tl or "old fort" in tl or "cathedral" in tl or "mosque" in tl or "temple" in tl or "voortrekker" in tl:
        url = "/img/hotspots/church.jpg"
    elif "playhouse" in tl or "bat centre" in tl or "sneddon" in tl or "stable theatre" in tl or "heritage theatre" in tl:
        url = "/img/hotspots/theatre.jpg"
    elif "cultural dance" in tl or "zulu experience" in tl or "phezulu" in tl:
        url = "/img/hotspots/cultural-dance.jpg"
    elif "market" in tl or "uzimbi" in tl:
        url = "/img/hotspots/market.jpg"
    elif "sangoma" in tl or "inyanga" in tl or "healing" in tl or "herbal" in tl:
        url = "/img/hotspots/herbs.jpg"
    elif "beadwork" in tl or "craft" in tl or "design centre" in tl:
        url = "/img/hotspots/crafts.jpg"
    return url

all_experiences = []
# Round-robin over the 25 hosts: 50 hotspots / 25 hosts = 2 each, so every
# business owner stays well below the maximum of 3 hotspots.
for i, (title, desc, cat, loc, prov, price, dur, max_p, active) in enumerate(experiences_data):
    owner = hosts[i % len(hosts)]
    exp = Experience(
        title=title, description=desc, category=cat,
        location=loc, province=prov, price=price,
        duration_hours=dur, max_participants=max_p,
        image_url=pick_image(title, cat),
        owner_id=owner.id, is_active=True, is_approved=True,
    )
    all_experiences.append(exp)

db.add_all(all_experiences)
db.flush()

# ── Ratings ────────────────────────────────────────────
approved_exps = [e for e in all_experiences if e.is_approved]
comment_templates = [
    "Absolutely incredible experience! The hosts were so welcoming and I learned so much about {} culture.",
    "This was the highlight of my trip to South Africa. Truly authentic and well-organised.",
    "Amazing! I would recommend this to anyone visiting {}.",
    "A beautiful cultural experience. The storytelling was captivating and the food was delicious.",
    "So glad I did this. It gave me a deep appreciation for South African heritage.",
    "The guides were knowledgeable and passionate. Worth every rand.",
    "A must-do for anyone interested in authentic South African culture.",
    "Wonderful from start to finish. The attention to cultural detail was impressive.",
    "Loved every minute of this experience. The community was so warm and inviting.",
    "This changed my perspective on South Africa. Beyond the tourist trail.",
]

all_ratings = []
for exp in approved_exps:
    num_ratings = random.randint(2, 6)
    chosen_tourists = random.sample(tourists, min(num_ratings, len(tourists)))
    for t in chosen_tourists:
        score = random.choices([3, 4, 4, 5, 5, 5], k=1)[0]
        loc_name = exp.location.split(",")[0]
        comment = random.choice(comment_templates).format(loc_name) if score >= 4 else "Decent experience overall."
        all_ratings.append(Rating(
            user_id=t.id, experience_id=exp.id,
            score=score, comment=comment, is_approved=True,
            created_at=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 90)),
        ))

db.add_all(all_ratings)
db.flush()

# ── Preferences ────────────────────────────────────────
pref_sets = [
    ["Traditional Cooking", "Township Life"],
    ["Heritage Tours", "Storytelling"],
    ["Music & Dance", "Crafts & Art"],
    ["Photography Tours", "Heritage Tours"],
    ["Traditional Healing", "Rural Heritage"],
    ["Textile & Weaving", "Crafts & Art"],
]

for i, t in enumerate(tourists):
    db.add(UserPreference(
        user_id=t.id,
        categories=", ".join(random.choice(pref_sets)),
    ))

# ── Trips ──────────────────────────────────────────────
trip_data = [
    ("KZN Cultural Explorer", "Durban, KwaZulu-Natal", date(2026, 8, 1), date(2026, 8, 5)),
    ("Cape Town Heritage Trail", "Cape Town, Western Cape", date(2026, 9, 10), date(2026, 9, 14)),
    ("Johannesburg Township Tour", "Johannesburg, Gauteng", date(2026, 10, 1), date(2026, 10, 3)),
]

for t in tourists[:3]:
    td = random.choice(trip_data)
    trip = Trip(user_id=t.id, title=td[0], destination=td[1],
                start_date=td[2], end_date=td[3], notes="Looking forward to it!")
    db.add(trip)
    db.flush()
    for day_num in range(1, (td[3] - td[2]).days + 1):
        db.add(TripDay(
            trip_id=trip.id, day_number=day_num,
            date=td[2] + timedelta(days=day_num - 1),
            activity=f"Day {day_num} activity",
            experience_id=random.choice(approved_exps).id,
        ))

db.commit()

# ── Summary ────────────────────────────────────────────
u_count = db.query(User).count()
e_count = db.query(Experience).count()
r_count = db.query(Rating).count()
p_count = db.query(UserPreference).count()
tr_count = db.query(Trip).count()
host_count = db.query(User).filter(User.role == UserRole.business_owner).count()

from collections import Counter
owner_counts = Counter(e.owner_id for e in db.query(Experience).all())
host_emails = [h.email for h in hosts]
db.close()

max_per_owner = max(owner_counts.values()) if owner_counts else 0

print(f"\n{'='*50}")
print(f"  DATABASE SEEDED SUCCESSFULLY")
print(f"{'='*50}")
print(f"  Users:           {u_count}")
print(f"  Business owners: {host_count}")
print(f"  Experiences:     {e_count}")
print(f"  Ratings:         {r_count}")
print(f"  Preferences:     {p_count}")
print(f"  Trips:           {tr_count}")
print(f"  Hotspots per owner: max {max_per_owner} (limit 3) -> {'OK' if max_per_owner <= 3 else 'VIOLATION'}")
print(f"\n  LOGIN CREDENTIALS")
print(f"{'='*50}")
print(f"  Admin:     admin@ubuntu.com     / Admin123!")
for email in host_emails:
    print(f"  Host:      {email:<24} / Host123!")
print(f"  Tourist:   lebo@ubuntu.com      / Tourist123!")
print(f"  Tourist:   thandi@ubuntu.com    / Tourist123!")
print(f"  Tourist:   james@ubuntu.com     / Tourist123!")
print(f"  Tourist:   priya@ubuntu.com     / Tourist123!")
print(f"  Tourist:   sarah@ubuntu.com     / Tourist123!")
print(f"  Tourist:   michael@ubuntu.com   / Tourist123!")
print(f"  Tourist:   amahle@ubuntu.com    / Tourist123!")
print(f"  Tourist:   daniel@ubuntu.com    / Tourist123!")
print(f"{'='*50}\n")
