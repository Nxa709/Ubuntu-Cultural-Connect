from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


# ── Experience ────────────────────────────────────────────
class ExperienceCreate(BaseModel):
    title: str = Field(min_length=3, max_length=120)
    description: str = Field(min_length=10, max_length=2000)
    category: str
    location: str = Field(min_length=2, max_length=120)
    province: Optional[str] = None
    price: float = Field(gt=0)
    duration_hours: Optional[float] = Field(None, gt=0)
    max_participants: int = Field(10, ge=1, le=100)
    image_url: Optional[str] = None


class ExperienceUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=120)
    description: Optional[str] = Field(None, min_length=10, max_length=2000)
    category: Optional[str] = None
    location: Optional[str] = Field(None, min_length=2, max_length=120)
    province: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    duration_hours: Optional[float] = Field(None, gt=0)
    max_participants: Optional[int] = Field(None, ge=1, le=100)
    image_url: Optional[str] = None


class ExperienceResponse(BaseModel):
    id: int
    title: str
    description: str
    category: str
    location: str
    province: Optional[str] = None
    price: float
    duration_hours: Optional[float] = None
    max_participants: int
    image_url: Optional[str] = None
    owner_id: int
    is_active: bool
    is_approved: bool = False
    rejection_reason: Optional[str] = None
    rejected_at: Optional[datetime] = None
    created_at: datetime
    avg_rating: Optional[float] = None
    rating_count: int = 0
    owner_name: Optional[str] = None
    itinerary_adds: int = 0

    model_config = {"from_attributes": True}


# ── Preferences ───────────────────────────────────────────
class PreferenceSet(BaseModel):
    categories: list[str]


class PreferenceResponse(BaseModel):
    categories: list[str]
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ── Trip ──────────────────────────────────────────────────
class TripDayInput(BaseModel):
    day_number: int
    date: date
    activity: str
    experience_id: Optional[int] = None
    notes: Optional[str] = None


class TripCreate(BaseModel):
    title: str
    destination: str
    start_date: date
    end_date: date
    notes: Optional[str] = None
    days: list[TripDayInput] = []


class TripUpdate(BaseModel):
    title: Optional[str] = None
    destination: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    notes: Optional[str] = None


class AddExperienceToTripRequest(BaseModel):
    start_date: date
    end_date: date
    destination: Optional[str] = None


class TripDayUpdate(BaseModel):
    day_number: Optional[int] = None
    date: Optional[date] = None
    activity: Optional[str] = None
    experience_id: Optional[int] = None
    notes: Optional[str] = None


class TripDayResponse(BaseModel):
    id: int
    day_number: int
    date: date
    activity: str
    experience_id: Optional[int] = None
    notes: Optional[str] = None
    experience_title: Optional[str] = None

    model_config = {"from_attributes": True}


class TripResponse(BaseModel):
    id: int
    title: str
    destination: str
    start_date: date
    end_date: date
    notes: Optional[str] = None
    created_at: datetime
    days: list[TripDayResponse] = []

    model_config = {"from_attributes": True}


# ── Rating ────────────────────────────────────────────────
class RatingCreate(BaseModel):
    score: int = Field(ge=1, le=5)
    comment: Optional[str] = None


class RatingResponse(BaseModel):
    id: int
    user_id: int
    experience_id: int
    score: int
    comment: Optional[str] = None
    created_at: datetime
    user_name: Optional[str] = None

    model_config = {"from_attributes": True}


# ── Owner Stats ──────────────────────────────────────────
class OwnerStats(BaseModel):
    total_hotspots: int
    active_hotspots: int
    inactive_hotspots: int
    pending_approval: int
    total_ratings: int
    avg_rating: Optional[float] = None
    total_categories: int


# ── Travel Journal ────────────────────────────────────────
class JournalCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1, max_length=5000)
    experience_id: Optional[int] = None
    location: Optional[str] = None
    visit_date: Optional[date] = None
    mood: Optional[str] = None


class JournalUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1, max_length=5000)
    experience_id: Optional[int] = None
    location: Optional[str] = None
    visit_date: Optional[date] = None
    mood: Optional[str] = None


class JournalResponse(BaseModel):
    id: int
    user_id: int
    experience_id: Optional[int] = None
    experience_title: Optional[str] = None
    title: str
    content: str
    location: Optional[str] = None
    visit_date: Optional[date] = None
    mood: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ── Review History ────────────────────────────────────────
class ReviewHistoryItem(BaseModel):
    id: int
    experience_id: int
    experience_title: Optional[str] = None
    experience_location: Optional[str] = None
    score: int
    comment: Optional[str] = None
    is_approved: bool
    rejected_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Host Reviews & Performance ───────────────────────────
class HostReviewItem(BaseModel):
    id: int
    user_name: Optional[str] = None
    experience_id: int
    experience_title: Optional[str] = None
    score: int
    comment: Optional[str] = None
    is_approved: bool
    created_at: datetime


class ExperiencePerformance(BaseModel):
    experience_id: int
    title: str
    category: str
    location: str
    total_ratings: int
    avg_rating: Optional[float] = None
    star_distribution: dict = {}
    unique_reviewers: int = 0
    trend: str = "stable"
