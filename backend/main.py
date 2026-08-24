import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from database import engine, Base, is_sqlite
from routers.auth import router as auth_router
from routers.experience import router as experience_router
from routers.admin import router as admin_router
from routers.notification import router as notification_router
from routers.upload import router as upload_router

# Create tables
Base.metadata.create_all(bind=engine)


def _migrate_sqlite():
    """SQLite cannot ALTER via create_all; add new columns idempotently."""
    if not is_sqlite:
        return
    from sqlalchemy import text
    with engine.begin() as conn:
        cols = {row[1] for row in conn.execute(text("PRAGMA table_info(users)"))}
        if "visitor_type" not in cols:
            conn.execute(text("ALTER TABLE users ADD COLUMN visitor_type VARCHAR"))
        if "country" not in cols:
            conn.execute(text("ALTER TABLE users ADD COLUMN country VARCHAR"))


_migrate_sqlite()

app = FastAPI(
    title="Ubuntu Cultural Connect API",
    description="Backend API for Ubuntu Cultural Connect — South African cultural tourism platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(experience_router)
app.include_router(admin_router)
app.include_router(notification_router)
app.include_router(upload_router)


@app.get("/api/health")
def health():
    return {"message": "Ubuntu Cultural Connect API is running"}


# ── Serve the built frontend (Vue SPA) ────────────────────
STATIC_DIR = Path(__file__).parent / "static"

if STATIC_DIR.exists():
    # Static assets (JS/CSS/images) from /assets and /img
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")
    app.mount("/img", StaticFiles(directory=STATIC_DIR / "img"), name="img")
    app.mount("/uploads", StaticFiles(directory=STATIC_DIR / "uploads"), name="uploads")

    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_spa(full_path: str):
        if full_path.startswith("api/"):
            return JSONResponse({"detail": "Not Found"}, status_code=404)
        file_path = STATIC_DIR / full_path
        if full_path and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(STATIC_DIR / "index.html")
