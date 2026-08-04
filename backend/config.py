import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data.db")
SECRET_KEY = os.getenv("SECRET_KEY", "ubuntu-cultural-connect-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

POSTGRESQL_DATABASE_URL = os.getenv(
    "POSTGRESQL_DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/ubuntu_cultural_connect",
)
