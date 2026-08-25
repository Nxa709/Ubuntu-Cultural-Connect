"""
Generate a PostgreSQL-compatible .sql file from the SQLite database.
Tables use models defined in SQLAlchemy; data is read from SQLite
and rendered as INSERT statements with correct Postgres types.

Usage:
    python generate_supabase_sql.py          # writes supabase_dump.sql
    python generate_supabase_sql.py -o out.sql
"""
import argparse
import sqlite3
import sys
import enum as pyenum
from pathlib import Path
from datetime import datetime, date

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, inspect, text, Enum as SAEnum
from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateTable
from database import Base
from models import *  # noqa: F401,F403  — registers all models with Base

SQLITE_PATH = Path(__file__).parent / "data.db"

# Experiences to exclude (commercial / fancy / well-known restaurants).
# IDs 1-5 are the traditional_cooking restaurant entries:
#   1 Amanzimtoti Fisheries, 2 Ocean Basket Musgrave, 3 The Spice Restaurant & Bar,
#   4 Tiger's Milk Ballito, 5 Moonshine Restaurant
EXCLUDE_EXPERIENCE_IDS = {1, 2, 3, 4, 5}

TABLE_ORDER = [
    "users",
    "experiences",
    "user_preferences",
    "trips",
    "trip_days",
    "ratings",
    "travel_journals",
    "notifications",
    "itinerary_adds",
    "experience_events",
]


def get_model(table_name):
    for mapper in Base.registry.mappers:
        if mapper.class_.__tablename__ == table_name:
            return mapper.class_
    return None


def collect_enum_types():
    """Walk all models, collect Enum columns and their Python enum classes."""
    enums = {}  # pg_type_name -> [values]
    for table_name in TABLE_ORDER:
        model = get_model(table_name)
        if model is None:
            continue
        for col in model.__table__.columns:
            if isinstance(col.type, SAEnum) and hasattr(col.type, 'enum_class'):
                enum_cls = col.type.enum_class
                pg_type = enum_cls.__name__.lower()
                if pg_type not in enums:
                    enums[pg_type] = [e.name for e in enum_cls]
    return enums


def emit_create_tables():
    pg_dialect = postgresql.dialect()
    lines = []
    lines.append("-- ============================================================")
    lines.append("--  Supabase SQL dump - Ubuntu Cultural Connect")
    lines.append("--  Generated from SQLite data.db")
    lines.append("--  Paste this entire file into the Supabase SQL Editor")
    lines.append("-- ============================================================")
    lines.append("")
    lines.append("BEGIN;")
    lines.append("")

    all_enums = collect_enum_types()

    # Clean slate: drop tables + enum types so the dump is re-runnable.
    lines.append("-- Clean slate (idempotent): safe to re-run this file any time")
    drop_tables = ", ".join(f'"{t}"' for t in reversed(TABLE_ORDER))
    lines.append(f"DROP TABLE IF EXISTS {drop_tables} CASCADE;")
    for pg_type in all_enums:
        lines.append(f"DROP TYPE IF EXISTS {pg_type} CASCADE;")
    lines.append("")

    # Create enum types first
    for pg_type, values in all_enums.items():
        vals_str = ", ".join(f"'{v}'" for v in values)
        lines.append(f"DO $$ BEGIN")
        lines.append(f"  CREATE TYPE {pg_type} AS ENUM ({vals_str});")
        lines.append(f"EXCEPTION WHEN duplicate_object THEN NULL;")
        lines.append(f"END $$;")
        lines.append("")

    # Create tables
    for table_name in TABLE_ORDER:
        model = get_model(table_name)
        if model is None:
            lines.append(f"-- WARNING: model not found for {table_name}, skipping")
            continue
        ddl = CreateTable(model.__table__).compile(dialect=pg_dialect)
        lines.append(str(ddl).rstrip(";") + ";")
        lines.append("")

    lines.append("COMMIT;")
    return "\n".join(lines)


def sql_escape(value, is_boolean_col=False):
    """Escape a Python value for a PostgreSQL SQL literal."""
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, int):
        if is_boolean_col:
            return "TRUE" if value else "FALSE"
        return str(value)
    if isinstance(value, float):
        return str(value)
    # String or anything else - escape single quotes
    s = str(value).replace("'", "''")
    return f"'{s}'"


def emit_inserts(sqlite_path):
    from sqlalchemy import Boolean as SABoolean
    conn = sqlite3.connect(str(sqlite_path))
    conn.row_factory = sqlite3.Row
    lines = []
    lines.append("")
    lines.append("-- ============================================================")
    lines.append("--  DATA")
    lines.append("-- ============================================================")
    lines.append("")

    for table_name in TABLE_ORDER:
        cur = conn.execute(f'SELECT * FROM "{table_name}"')
        rows = cur.fetchall()

        # Filter out rows referencing excluded restaurant experiences.
        if table_name == "experiences":
            rows = [r for r in rows if r["id"] not in EXCLUDE_EXPERIENCE_IDS]
        elif "experience_id" in [desc[0] for desc in cur.description]:
            rows = [r for r in rows if r["experience_id"] not in EXCLUDE_EXPERIENCE_IDS]

        if not rows:
            lines.append(f"-- {table_name}: 0 rows (skipped)")
            lines.append("")
            continue

        cols = [desc[0] for desc in cur.description]
        cols_sql = ", ".join(f'"{c}"' for c in cols)

        # Determine which columns are boolean
        model = get_model(table_name)
        bool_cols = set()
        if model:
            for col in model.__table__.columns:
                if isinstance(col.type, SABoolean):
                    bool_cols.add(col.name)

        lines.append(f"-- {table_name}: {len(rows)} rows")
        lines.append(f"INSERT INTO {table_name} ({cols_sql}) VALUES")

        val_lines = []
        for row in rows:
            vals = []
            for i, v in enumerate(row):
                is_bool = cols[i] in bool_cols
                val = sql_escape(v, is_boolean_col=is_bool)
                vals.append(val)
            val_lines.append("  (" + ", ".join(vals) + ")")

        lines.append(",\n".join(val_lines) + ";")
        lines.append("")

    conn.close()
    return "\n".join(lines)


def emit_sequences():
    lines = []
    lines.append("-- ============================================================")
    lines.append("--  RESET SEQUENCES (after inserting with explicit IDs)")
    lines.append("-- ============================================================")
    lines.append("")
    for table_name in TABLE_ORDER:
        lines.append(
            f"SELECT setval(pg_get_serial_sequence('{table_name}', 'id'), "
            f"COALESCE((SELECT MAX(id) FROM {table_name}), 1));"
        )
    lines.append("")
    return "\n".join(lines)


def emit_footer():
    return "-- Done.\n"


def main():
    parser = argparse.ArgumentParser(description="Generate PostgreSQL SQL from SQLite")
    parser.add_argument("-o", "--output", default="supabase_dump.sql")
    args = parser.parse_args()

    if not SQLITE_PATH.exists():
        print(f"ERROR: SQLite file not found at {SQLITE_PATH}")
        sys.exit(1)

    print(f"Reading from {SQLITE_PATH} ...")
    print(f"Generating {args.output} ...")
    print(f"Excluding restaurant experiences: {sorted(EXCLUDE_EXPERIENCE_IDS)}")

    ddl = emit_create_tables()
    inserts = emit_inserts(SQLITE_PATH)
    seqs = emit_sequences()
    footer = emit_footer()

    sql = f"{ddl}\n{inserts}\n{seqs}\n{footer}"

    out_path = Path(__file__).parent / args.output
    out_path.write_text(sql, encoding="utf-8")
    print(f"Done! Wrote {len(sql):,} bytes to {out_path}")
    print(f"Tables included: {TABLE_ORDER}")
    print()
    print("To import into Supabase:")
    print("  1. Open Supabase Dashboard -> SQL Editor")
    print("  2. Paste the contents of the .sql file")
    print("  3. Click 'Run'")


if __name__ == "__main__":
    main()
