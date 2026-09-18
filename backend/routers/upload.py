from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from models.image import Image
from routers.auth import get_current_user

router = APIRouter(prefix="/api/upload", tags=["upload"])

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg"}
MAX_SIZE = 5 * 1024 * 1024  # 5 MB


@router.post("/image")
async def upload_image(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
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

    # Store the bytes in the database so uploads survive redeploys
    # (Render's local filesystem is ephemeral and wipes uploads).
    image = Image(
        filename=file.filename,
        content_type=file.content_type or "application/octet-stream",
        data=content,
    )
    db.add(image)
    db.commit()
    db.refresh(image)

    base = str(request.base_url).rstrip("/")
    return {"url": f"{base}/api/images/{image.id}"}
