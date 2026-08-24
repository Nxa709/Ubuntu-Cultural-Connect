from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from models.user import User, UserRole
from schemas.user import UserRegister, UserLogin, UserResponse, Token
from services.auth_service import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
optional_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user


def get_optional_user(
    token: str = Depends(optional_oauth2_scheme),
    db: Session = Depends(get_db),
):
    """Returns the current user when a valid token is supplied, else None.

    Used by lightweight tracking endpoints so anonymous visitors can still
    contribute analytics without being forced to authenticate."""
    if not token:
        return None
    payload = decode_access_token(token)
    if payload is None or payload.get("sub") is None:
        return None
    return db.query(User).filter(User.id == int(payload["sub"])).first()


# ── Register ──────────────────────────────────────────────
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    email = user_in.email.strip().lower()
    existing = db.query(User).filter(func.lower(User.email) == email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    if user_in.role not in [r.value for r in UserRole]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {[r.value for r in UserRole]}",
        )

    user = User(
        email=email,
        hashed_password=hash_password(user_in.password),
        full_name=user_in.full_name,
        phone_number=user_in.phone_number,
        role=user_in.role,
        visitor_type=user_in.visitor_type if user_in.role == "tourist" else None,
        country=user_in.country if user_in.role == "tourist" else None,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ── Login ─────────────────────────────────────────────────
@router.post("/login", response_model=Token)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    email = user_in.email.strip().lower()
    user = db.query(User).filter(func.lower(User.email) == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email not found. Please register first.",
        )

    if not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password. Please try again.",
        )

    token = create_access_token(data={"sub": str(user.id), "role": user.role})
    return Token(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


# ── Verify User Info (get current user) ──────────────────
@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


# ── Update profile ────────────────────────────────────────
@router.put("/me", response_model=UserResponse)
def update_me(
    full_name: str | None = None,
    phone_number: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if full_name is not None:
        current_user.full_name = full_name
    if phone_number is not None:
        current_user.phone_number = phone_number
    db.commit()
    db.refresh(current_user)
    return current_user


# ── Logout ────────────────────────────────────────────────
@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    return {"message": "Successfully logged out"}


# ── Deregister ────────────────────────────────────────────
@router.delete("/deregister")
def deregister(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db.delete(current_user)
    db.commit()
    return {"message": "Account successfully deleted"}
