from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.province import Province
from schemas.province import ProvinceResponse

router = APIRouter(prefix="/api/provinces", tags=["provinces"])


@router.get("", response_model=list[ProvinceResponse])
@router.get("/", response_model=list[ProvinceResponse])
def list_provinces(db: Session = Depends(get_db)):
    return db.query(Province).order_by(Province.name).all()


@router.get("/{slug}", response_model=ProvinceResponse)
def get_province(slug: str, db: Session = Depends(get_db)):
    province = db.query(Province).filter(Province.slug == slug).first()
    if not province:
        raise HTTPException(status_code=404, detail="Province not found")
    return province
