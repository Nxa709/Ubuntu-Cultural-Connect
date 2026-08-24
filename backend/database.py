from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool, NullPool

from config import DATABASE_URL

is_sqlite = "sqlite" in DATABASE_URL
is_supabase = "supabase" in DATABASE_URL or "pooler.supabase" in DATABASE_URL

if is_sqlite:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=NullPool,
        echo=False,
    )
elif is_supabase:
    # Supabase (managed Postgres) is heavily connection-limited (free ≈ 2, hobby ≈ 10).
    # Use a very small pool so we never exhaust the cap and stall requests.
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=1,
        max_overflow=2,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=False,
    )
else:
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=False,
    )

if is_sqlite:
    @event.listens_for(engine, "connect")
    def _set_sqlite_pragmas(dbapi_connection, connection_record):
        """SQLite throughput/concurrency tuning (harmless if not SQLite)."""
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA synchronous=NORMAL;")
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
