from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


# ── Generation input ──────────────────────────────────────────────

class GenerateItineraryRequest(BaseModel):
    title: Optional[str] = None
    province: Optional[str] = None
    num_days: int = Field(1, ge=1, le=14)
    budget: Optional[float] = Field(None, ge=0)
    pace: str = "balanced"                      # relaxed | balanced | packed
    interests: list[str] = []                   # cultural interest keys
    experience_type: Optional[str] = None       # 'any' or a CulturalCategory value
    min_rating: float = Field(0, ge=0, le=5)
    budget_preference: str = "mid"              # budget | mid | luxury


# ── Item / day / itinerary output ─────────────────────────────────

class ItineraryItemResponse(BaseModel):
    id: int
    experience_id: Optional[int] = None
    day_number: int
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    sort_order: int = 0
    estimated_cost: float = 0
    recommendation_score: float = 0
    reason: Optional[str] = None

    # Joined experience details (so the UI can render a full card)
    title: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    province: Optional[str] = None
    price: float = 0
    duration_hours: Optional[float] = None
    image_url: Optional[str] = None
    avg_rating: Optional[float] = None


class ItineraryDay(BaseModel):
    day_number: int
    date: Optional[date] = None
    items: list[ItineraryItemResponse] = []
    estimated_cost: float = 0


class ItineraryResponse(BaseModel):
    id: int
    title: Optional[str] = None
    province: Optional[str] = None
    num_days: int
    budget: Optional[float] = None
    estimated_cost: float = 0
    remaining_budget: Optional[float] = None
    pace: str = "balanced"
    interests: list[str] = []
    experience_type: Optional[str] = None
    min_rating: float = 0
    budget_preference: str = "mid"
    summary: Optional[str] = None
    activity_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    days: list[ItineraryDay] = []
    warning: Optional[str] = None


class ItinerarySummary(BaseModel):
    id: int
    title: Optional[str] = None
    province: Optional[str] = None
    num_days: int
    estimated_cost: float = 0
    budget: Optional[float] = None
    activity_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ── Editing input ─────────────────────────────────────────────────

class ItineraryItemUpdate(BaseModel):
    item_id: Optional[int] = None
    experience_id: int
    day_number: int
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    sort_order: int = 0


class UpdateItineraryRequest(BaseModel):
    title: Optional[str] = None
    items: Optional[list[ItineraryItemUpdate]] = None


class ReplaceItemRequest(BaseModel):
    experience_id: Optional[int] = None  # None => auto-pick the best alternative


class AlternativeExperience(BaseModel):
    experience_id: int
    title: str
    category: Optional[str] = None
    location: Optional[str] = None
    province: Optional[str] = None
    price: float = 0
    duration_hours: Optional[float] = None
    image_url: Optional[str] = None
    avg_rating: Optional[float] = None
    score: float = 0
    reason: Optional[str] = None
