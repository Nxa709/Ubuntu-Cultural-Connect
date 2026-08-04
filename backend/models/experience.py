import enum
from datetime import datetime, timezone

from sqlalchemy import (
    Column, Integer, String, Float, Text, Boolean, DateTime,
    Enum, ForeignKey, Date,
)
from sqlalchemy.orm import relationship
from database import Base


class CulturalCategory(str, enum.Enum):
    traditional_cooking = "Traditional Cooking"
    storytelling = "Storytelling"
    music_dance = "Music & Dance"
    crafts = "Crafts & Art"
    heritage_tours = "Heritage Tours"
    township_life = "Township Life"
    rural_heritage = "Rural Heritage"
    traditional_healing = "Traditional Healing"
    textile_weaving = "Textile & Weaving"
    photography = "Photography Tours"
    nature_wildlife = "Nature & Wildlife"
    accommodation = "Accommodation & Lodging"


class Experience(Base):
    __tablename__ = "experiences"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(Enum(CulturalCategory), nullable=False)
    location = Column(String, nullable=False)
    province = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    duration_hours = Column(Float, nullable=True)
    max_participants = Column(Integer, default=10)
    image_url = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    is_approved = Column(Boolean, default=False)
    rejection_reason = Column(String, nullable=True)
    rejected_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    owner = relationship("User", backref="experiences")
    ratings = relationship("Rating", back_populates="experience", cascade="all, delete-orphan")


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    categories = Column(String, nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", backref="preference")


class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", backref="trips")
    days = relationship("TripDay", back_populates="trip", cascade="all, delete-orphan")


class TripDay(Base):
    __tablename__ = "trip_days"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=False)
    day_number = Column(Integer, nullable=False)
    date = Column(Date, nullable=False)
    activity = Column(String, nullable=False)
    experience_id = Column(Integer, ForeignKey("experiences.id"), nullable=True)
    notes = Column(Text, nullable=True)

    trip = relationship("Trip", back_populates="days")
    experience = relationship("Experience")


class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    experience_id = Column(Integer, ForeignKey("experiences.id"), nullable=False)
    score = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    is_approved = Column(Boolean, default=True)
    rejected_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", backref="ratings")
    experience = relationship("Experience", back_populates="ratings")


class TravelJournal(Base):
    __tablename__ = "travel_journals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    experience_id = Column(Integer, ForeignKey("experiences.id"), nullable=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    location = Column(String, nullable=True)
    visit_date = Column(Date, nullable=True)
    mood = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", backref="journals")
    experience = relationship("Experience")
