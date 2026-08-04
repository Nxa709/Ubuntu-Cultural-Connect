from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CommentResponse(BaseModel):
    id: int
    user_id: int
    user_name: Optional[str] = None
    experience_id: int
    experience_title: Optional[str] = None
    score: int
    comment: Optional[str] = None
    is_approved: bool
    rejected_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class HotspotResponse(BaseModel):
    id: int
    title: str
    description: str
    category: str
    location: str
    province: Optional[str] = None
    image_url: Optional[str] = None
    price: float = 0
    duration_hours: Optional[float] = None
    max_participants: Optional[int] = None
    owner_id: int
    owner_name: Optional[str] = None
    owner_email: Optional[str] = None
    owner_phone: Optional[str] = None
    is_active: bool
    is_approved: bool
    rejection_reason: Optional[str] = None
    rejected_at: Optional[datetime] = None
    rating_count: int = 0
    avg_rating: Optional[float] = None
    itinerary_adds: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


class HotspotRejectRequest(BaseModel):
    reason: str


class AdminActionResponse(BaseModel):
    message: str
    id: int
    is_approved: bool


class AdminStatsResponse(BaseModel):
    total_users: int
    total_tourists: int
    total_hosts: int
    total_admins: int
    total_experiences: int
    approved_experiences: int
    pending_experiences: int
    total_ratings: int
    pending_comments: int
    total_trips: int


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    phone_number: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserRoleUpdate(BaseModel):
    role: str


class UserActionResponse(BaseModel):
    message: str
    id: int
