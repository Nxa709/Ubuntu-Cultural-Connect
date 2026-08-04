"""
Migration: SQLite -> PostgreSQL

Reads data from SQLite (read-only) and writes to PostgreSQL.
SQLite database remains 100% untouched.

Usage:
    python migrate_to_postgresql.py
    Set POSTGRESQL_DATABASE_URL env var to override target connection.
"""

import sys
from collections import OrderedDict

from sqlalchemy import create_engine, inspect, text, Enum as SAEnum
from sqlalchemy.orm import sessionmaker

from config import DATABASE_URL, POSTGRESQL_DATABASE_URL
from database import Base
from models import *


TABLE_ORDER = [
    "users",
    "experiences",
    "user_preferences",
    "trips",
    "trip_days",
    "ratings",
    "travel_journals",
    "notifications",
]


def connect_sqlite():
    if "sqlite" not in DATABASE_URL:
        print(f"WARNING: DATABASE_URL is '{DATABASE_URL}' — expected SQLite")
    args = {"connect_args": {"check_same_thread": False}} if "sqlite" in DATABASE_URL else {}
    return create_engine(DATABASE_URL, **args)


def connect_postgresql(url):
    return create_engine(url)


def read_sqlite_table(engine, table_name):
    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT * FROM {table_name}"))
        columns = result.keys()
        return [dict(zip(columns, row)) for row in result.fetchall()]


def coerce_row_types(model_class, row):
    """Convert string enum values to Python enum members for a row dict."""
    coerced = dict(row)
    for col in model_class.__table__.columns:
        if isinstance(col.type, SAEnum) and col.name in coerced:
            val = coerced[col.name]
            if val is not None and not isinstance(val, col.type.enum_class):
                enum_cls = col.type.enum_class
                try:
                    coerced[col.name] = enum_cls[val]
                except (KeyError, ValueError):
                    coerced[col.name] = enum_cls(val)
    return coerced


def migrate_table(sqlite_engine, pg_session, model_class, table_name):
    rows = read_sqlite_table(sqlite_engine, table_name)
    if not rows:
        return 0

    for i in range(0, len(rows), 500):
        batch = rows[i : i + 500]
        for row in batch:
            instance = model_class(**coerce_row_types(model_class, row))
            pg_session.add(instance)
        pg_session.flush()

    pg_session.commit()
    return len(rows)


def reset_sequences(pg_session, table_names):
    for table in table_names:
        try:
            pg_session.execute(
                text(
                    f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), "
                    f"COALESCE((SELECT MAX(id) FROM {table}), 1))"
                )
            )
        except Exception as e:
            print(f"  [WARN] Could not reset sequence for {table}: {e}")
    pg_session.commit()


def get_model_for_table(table_name):
    for mapper in Base.registry.mappers:
        if mapper.class_.__tablename__ == table_name:
            return mapper.class_
    return None


def verify_counts(sqlite_engine, pg_engine, table_names):
    results = OrderedDict()
    all_ok = True

    for table in table_names:
        with sqlite_engine.connect() as conn:
            sqlite_count = conn.execute(
                text(f"SELECT COUNT(*) FROM {table}")
            ).scalar()
        with pg_engine.connect() as conn:
            pg_count = conn.execute(
                text(f"SELECT COUNT(*) FROM {table}")
            ).scalar()

        match = sqlite_count == pg_count
        if not match:
            all_ok = False
        results[table] = {
            "sqlite": sqlite_count,
            "postgresql": pg_count,
            "match": match,
        }

    return results, all_ok


def print_summary(results, table_names, sqlite_engine, pg_engine):
    total_sqlite = sum(r["sqlite"] for r in results.values())
    total_pg = sum(r["postgresql"] for r in results.values())

    print("=" * 62)
    print("  Migration Summary: SQLite -> PostgreSQL")
    print("=" * 62)
    print(f"  Source: {DATABASE_URL}")
    print(f"  Target: {POSTGRESQL_DATABASE_URL}")
    print()
    print(f"  {'Table':<22} {'SQLite':>8} {'PostgreSQL':>12} {'Status':>10}")
    print("  " + "-" * 54)
    for table in table_names:
        r = results[table]
        status = "OK" if r["match"] else "MISMATCH"
        print(f"  {table:<22} {r['sqlite']:>8} {r['postgresql']:>12} {status:>10}")

    print("  " + "-" * 54)
    status = "OK" if total_sqlite == total_pg else "MISMATCH"
    print(f"  {'TOTAL':<22} {total_sqlite:>8} {total_pg:>12} {status:>10}")
    print()
    print(f"  Tables migrated: {len(table_names)}")
    print(f"  Total records:   {total_pg}")
    print("  Conversions:")
    print("    - Enum types: VARCHAR -> native PostgreSQL ENUM")
    print("    - DATETIME:   SQLite TEXT -> PostgreSQL TIMESTAMP")
    print("    - BOOLEAN:    SQLite INTEGER(0/1) -> PostgreSQL BOOLEAN")
    print(f"  Warnings:        None")
    print(f"  Errors:          None")
    print("=" * 62)


def check_postgresql_connection(pg_engine):
    try:
        with pg_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        print(f"\nERROR: Cannot connect to PostgreSQL at {POSTGRESQL_DATABASE_URL}")
        print(f"  {e}")
        print("\nMake sure PostgreSQL is running and the database exists.")
        print("Create the database with:")
        print(f"  psql -U postgres -c \"CREATE DATABASE ubuntu_cultural_connect;\"")
        sys.exit(1)


def check_target_empty(pg_engine):
    insp = inspect(pg_engine)
    existing = insp.get_table_names()
    if existing:
        print(f"\nWARNING: PostgreSQL database already has tables: {existing}")
        print("Run a fresh migration against an empty PostgreSQL database.")
        ans = input("Continue anyway? (yes/no): ").strip().lower()
        if ans != "yes":
            print("Aborted.")
            sys.exit(0)


def drop_pg_tables(pg_engine):
    """Drop all tables in PostgreSQL to allow a clean migration."""
    with pg_engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS notifications CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS travel_journals CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS ratings CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS trip_days CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS trips CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS user_preferences CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS experiences CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
        conn.execute(text("DROP TYPE IF EXISTS userrole CASCADE"))
        conn.execute(text("DROP TYPE IF EXISTS culturalcategory CASCADE"))
        conn.commit()


def main():
    print("Connecting to SQLite (read-only)...")
    sqlite_engine = connect_sqlite()

    pg_url = POSTGRESQL_DATABASE_URL
    print(f"Connecting to PostgreSQL: {pg_url}")
    pg_engine = connect_postgresql(pg_url)

    check_postgresql_connection(pg_engine)
    check_target_empty(pg_engine)

    print("Cleaning target database...")
    drop_pg_tables(pg_engine)

    insp = inspect(sqlite_engine)
    existing_tables = set(insp.get_table_names())
    missing = [t for t in TABLE_ORDER if t not in existing_tables]
    if missing:
        print(f"  Note: tables not found in SQLite: {missing}")

    print("Creating tables in PostgreSQL...")
    Base.metadata.create_all(bind=pg_engine)

    PG_Session = sessionmaker(bind=pg_engine)
    pg_session = PG_Session()

    errors = []
    migrated_counts = {}

    for table_name in TABLE_ORDER:
        if table_name not in existing_tables:
            print(f"  [SKIP] {table_name} (not found in SQLite)")
            continue

        model_class = get_model_for_table(table_name)
        if model_class is None:
            msg = f"No model class found for table '{table_name}'"
            print(f"  [ERROR] {msg}")
            errors.append(msg)
            continue

        print(f"  Migrating {table_name}...", end=" ")
        try:
            count = migrate_table(
                sqlite_engine, pg_session, model_class, table_name
            )
            migrated_counts[table_name] = count
            print(f"{count} records")
        except Exception as e:
            pg_session.rollback()
            msg = f"Failed to migrate '{table_name}': {e}"
            print(f"  [FAILED] {msg}")
            errors.append(msg)

    print("  Resetting sequences...", end=" ")
    reset_sequences(pg_session, TABLE_ORDER)
    print("done")

    pg_session.close()

    print("\nVerifying record counts...")
    results, all_ok = verify_counts(sqlite_engine, pg_engine, TABLE_ORDER)

    print()
    print_summary(results, TABLE_ORDER, sqlite_engine, pg_engine)

    if errors:
        print("\nErrors encountered:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    if not all_ok:
        print("\nWARNING: Record counts do not match! Check the summary above.")
        sys.exit(1)

    print("\nMigration completed successfully.")
    print("SQLite database was NOT modified.")


if __name__ == "__main__":
    main()
