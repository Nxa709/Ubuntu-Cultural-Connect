from sqlalchemy import create_engine, text
from config import DATABASE_URL

eng = create_engine(DATABASE_URL)
for r in eng.connect().execute(text("SELECT id,email,role FROM users WHERE role = 'tourist'")):
    print(r[0], r[1], r[2])
