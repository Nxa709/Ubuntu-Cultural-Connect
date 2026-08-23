import secrets
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from models.user import User
from routers.auth import get_current_user

router = APIRouter(prefix="/api/upload", tags=["upload"])

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "static" / "uploads"
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg"}
MAX_SIZE = 5 * 1024 * 1024  # 5 MB


@router.post("/image")
async def upload_image(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="Image must be 5 MB or smaller")

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    name = f"{secrets.token_hex(8)}{ext}"
    dest = UPLOAD_DIR / name
    with open(dest, "wb") as f:
        f.write(content)

    url = str(request.base_url).rstrip("/") + f"/uploads/{name}"
    return {"url": url}
