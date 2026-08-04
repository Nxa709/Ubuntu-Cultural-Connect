import json
from datetime import date, datetime
from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, extract

from database import get_db
from models.user import User
from models.experience import (
    Experience, UserPreference, Trip, TripDay, Rating, CulturalCategory, TravelJournal,
)
from models.notification import Notification
from schemas.experience import (
    ExperienceCreate, ExperienceUpdate, ExperienceResponse,
    PreferenceSet, PreferenceResponse,
    TripCreate, TripUpdate, TripDayUpdate, TripDayInput, TripResponse, TripDayResponse,
    AddExperienceToTripRequest,
    RatingCreate, RatingResponse,
    JournalCreate, JournalUpdate, JournalResponse, ReviewHistoryItem,
    HostReviewItem, ExperiencePerformance,
)
from routers.auth import get_current_user

router = APIRouter(prefix="/api/experiences", tags=["experiences"])


# ── helpers ───────────────────────────────────────────────
def _exp_to_response(exp, db=None, rating_agg=None, itinerary_counts=None):
    if rating_agg and exp.id in rating_agg:
        avg, cnt = rating_agg[exp.id]
    elif db:
        avg = db.query(func.avg(Rating.score)).filter(
            Rating.experience_id == exp.id, Rating.is_approved == True).scalar()
        cnt = db.query(func.count(Rating.id)).filter(
            Rating.experience_id == exp.id, Rating.is_approved == True).scalar()
    else:
        avg, cnt = None, 0

    if itinerary_counts and exp.id in itinerary_counts:
        ic = itinerary_counts[exp.id]
    elif db:
        ic = db.query(func.count(TripDay.id)).filter(
            TripDay.experience_id == exp.id).scalar()
    else:
        ic = 0

    return ExperienceResponse(
        id=exp.id,
        title=exp.title,
        description=exp.description,
        category=exp.category.value if hasattr(exp.category, "value") else exp.category,
        location=exp.location,
        province=exp.province,
        price=exp.price,
        duration_hours=exp.duration_hours,
        max_participants=exp.max_participants,
        image_url=exp.image_url,
        owner_id=exp.owner_id,
        is_active=exp.is_active,
        is_approved=exp.is_approved,
        rejection_reason=exp.rejection_reason,
        rejected_at=exp.rejected_at,
        created_at=exp.created_at,
        avg_rating=round(float(avg), 1) if avg else None,
        rating_count=cnt or 0,
        owner_name=exp.owner.full_name if exp.owner else None,
        itinerary_adds=ic or 0,
    )


def _trip_to_response(trip: Trip) -> TripResponse:
    days = []
    for d in sorted(trip.days, key=lambda x: x.day_number):
        days.append(TripDayResponse(
            id=d.id,
            day_number=d.day_number,
            date=d.date,
            activity=d.activity,
            experience_id=d.experience_id,
            notes=d.notes,
            experience_title=d.experience.title if d.experience else None,
        ))
    return TripResponse(
        id=trip.id,
        title=trip.title,
        destination=trip.destination,
        start_date=trip.start_date,
        end_date=trip.end_date,
        notes=trip.notes,
        created_at=trip.created_at,
        days=days,
    )


# ── Notification helper ────────────────────────────────────
def _notify_owner_on_itinerary_add(experience_id: int, tourist: User, db: Session, visit_date: str = "", visit_time: str = ""):
    exp = db.query(Experience).filter(Experience.id == experience_id).first()
    if not exp or exp.owner_id == tourist.id:
        return
    existing = db.query(Notification).filter(
        Notification.user_id == exp.owner_id,
        Notification.experience_id == experience_id,
        Notification.type == "itinerary_add",
        Notification.is_read == False,
    ).first()
    if existing:
        return
    lines = [
        f"New Itinerary Addition",
        f"",
        f"Tourist: {tourist.full_name}",
        f"Hotspot: {exp.title}",
    ]
    if visit_date:
        lines.append(f"Visit Date: {visit_date}")
    if visit_time:
        lines.append(f"Visit Time: {visit_time}")
    message = "\n".join(lines)
    notif = Notification(
        user_id=exp.owner_id,
        type="itinerary_add",
        message=message,
        experience_id=exp.id,
        tourist_name=tourist.full_name,
    )
    db.add(notif)
    db.flush()


# ── Combined home data (single round-trip) ────────────────
@router.get("/home")
def get_home_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    pref = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    prefs = []
    exps = []

    if pref and pref.categories:
        cats = [c.strip() for c in pref.categories.split(",") if c.strip()]
        prefs = cats
        exps = db.query(Experience).filter(
            Experience.is_active == True, Experience.is_approved == True,
            Experience.category.in_(cats),
        ).limit(6).all()

    if not exps:
        exps = db.query(Experience).filter(
            Experience.is_active == True, Experience.is_approved == True,
        ).limit(6).all()

    ids = [e.id for e in exps]
    if ids:
        rating_rows = db.query(
            Rating.experience_id, func.avg(Rating.score), func.count(Rating.id)
        ).filter(Rating.experience_id.in_(ids), Rating.is_approved == True).group_by(Rating.experience_id).all()
        rating_agg = {r[0]: (r[1], r[2]) for r in rating_rows}
        itin_rows = db.query(TripDay.experience_id, func.count(TripDay.id)).filter(TripDay.experience_id.in_(ids)).group_by(TripDay.experience_id).all()
        itinerary_counts = dict(itin_rows)
    else:
        rating_agg, itinerary_counts = {}, {}

    return {
        "preferences": prefs,
        "recommended": [_exp_to_response(e, rating_agg=rating_agg, itinerary_counts=itinerary_counts) for e in exps],
    }


# ── Categories ────────────────────────────────────────────
@router.get("/categories")
def list_categories():
    return [{"value": c.value, "label": c.value} for c in CulturalCategory]


# ── Preferences (must be before /{exp_id}) ────────────────
@router.get("/prefs/me", response_model=PreferenceResponse)
def get_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    pref = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    if not pref:
        return PreferenceResponse(categories=[], updated_at=None)
    cats = [c.strip() for c in pref.categories.split(",") if c.strip()]
    return PreferenceResponse(categories=cats, updated_at=pref.updated_at)


@router.post("/prefs", response_model=PreferenceResponse)
def set_preferences(
    data: PreferenceSet,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not data.categories:
        raise HTTPException(status_code=400, detail="Select at least one category")

    cats_str = ",".join(data.categories)
    pref = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    if pref:
        pref.categories = cats_str
    else:
        pref = UserPreference(user_id=current_user.id, categories=cats_str)
        db.add(pref)
    db.commit()
    db.refresh(pref)

    cats = [c.strip() for c in pref.categories.split(",") if c.strip()]
    return PreferenceResponse(categories=cats, updated_at=pref.updated_at)


# ── Recommended (must be before /{exp_id}) ─────────────────
@router.get("/recommended", response_model=list[ExperienceResponse])
def get_recommended(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    pref = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    if not pref or not pref.categories:
        exps = db.query(Experience).filter(Experience.is_active == True, Experience.is_approved == True).limit(6).all()
    else:
        cats = [c.strip() for c in pref.categories.split(",") if c.strip()]
        exps = db.query(Experience).filter(
            Experience.is_active == True,
            Experience.is_approved == True,
            Experience.category.in_(cats),
        ).all()
        if not exps:
            exps = db.query(Experience).filter(Experience.is_active == True, Experience.is_approved == True).limit(6).all()

    ids = [e.id for e in exps]
    if ids:
        rating_rows = db.query(
            Rating.experience_id, func.avg(Rating.score), func.count(Rating.id)
        ).filter(Rating.experience_id.in_(ids), Rating.is_approved == True).group_by(Rating.experience_id).all()
        rating_agg = {r[0]: (r[1], r[2]) for r in rating_rows}
        itin_rows = db.query(TripDay.experience_id, func.count(TripDay.id)).filter(TripDay.experience_id.in_(ids)).group_by(TripDay.experience_id).all()
        itinerary_counts = dict(itin_rows)
    else:
        rating_agg, itinerary_counts = {}, {}

    return [_exp_to_response(e, rating_agg=rating_agg, itinerary_counts=itinerary_counts) for e in exps]


# ── Trips (must be before /{exp_id}) ──────────────────────
@router.get("/trips/me", response_model=list[TripResponse])
def list_my_trips(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    trips = db.query(Trip).filter(Trip.user_id == current_user.id).all()
    return [_trip_to_response(t) for t in trips]


@router.post("/trips", response_model=TripResponse, status_code=201)
def create_trip(
    data: TripCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if data.end_date < data.start_date:
        raise HTTPException(status_code=400, detail="End date must be after start date")

    trip = Trip(
        user_id=current_user.id,
        title=data.title,
        destination=data.destination,
        start_date=data.start_date,
        end_date=data.end_date,
        notes=data.notes,
    )
    db.add(trip)
    db.flush()

    for day in data.days:
        td = TripDay(
            trip_id=trip.id,
            day_number=day.day_number,
            date=day.date,
            activity=day.activity,
            experience_id=day.experience_id,
            notes=day.notes,
        )
        db.add(td)

    db.commit()

    for day in data.days:
        if day.experience_id:
            _notify_owner_on_itinerary_add(day.experience_id, current_user, db, visit_date=day.date.isoformat())
    if any(d.experience_id for d in data.days):
        db.commit()

    db.refresh(trip)
    return _trip_to_response(trip)


# ── Experience CRUD ───────────────────────────────────────
@router.get("/", response_model=list[ExperienceResponse])
def list_experiences(
    category: str = None,
    search: str = None,
    db: Session = Depends(get_db),
):
    q = db.query(Experience).filter(Experience.is_active == True, Experience.is_approved == True)
    if category:
        q = q.filter(Experience.category == category)
    if search:
        q = q.filter(Experience.title.ilike(f"%{search}%"))
    exps = q.all()
    if not exps:
        return []

    ids = [e.id for e in exps]

    rating_rows = db.query(
        Rating.experience_id, func.avg(Rating.score), func.count(Rating.id)
    ).filter(
        Rating.experience_id.in_(ids), Rating.is_approved == True
    ).group_by(Rating.experience_id).all()
    rating_agg = {r[0]: (r[1], r[2]) for r in rating_rows}

    itin_rows = db.query(
        TripDay.experience_id, func.count(TripDay.id)
    ).filter(TripDay.experience_id.in_(ids)).group_by(TripDay.experience_id).all()
    itinerary_counts = dict(itin_rows)

    return [_exp_to_response(e, rating_agg=rating_agg, itinerary_counts=itinerary_counts) for e in exps]


# ── Owner: My Experiences (MUST be before /{exp_id}) ─────
@router.get("/mine", response_model=list[ExperienceResponse])
def list_my_experiences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    exps = db.query(Experience).filter(Experience.owner_id == current_user.id).order_by(Experience.created_at.desc()).all()
    if not exps:
        return []
    ids = [e.id for e in exps]
    rating_rows = db.query(
        Rating.experience_id, func.avg(Rating.score), func.count(Rating.id)
    ).filter(
        Rating.experience_id.in_(ids), Rating.is_approved == True
    ).group_by(Rating.experience_id).all()
    rating_agg = {r[0]: (r[1], r[2]) for r in rating_rows}

    itin_rows = db.query(
        TripDay.experience_id, func.count(TripDay.id)
    ).filter(TripDay.experience_id.in_(ids)).group_by(TripDay.experience_id).all()
    itinerary_counts = dict(itin_rows)
    return [_exp_to_response(e, rating_agg=rating_agg, itinerary_counts=itinerary_counts) for e in exps]


# ── Owner: Stats (MUST be before /{exp_id}) ──────────────
@router.get("/owner/stats")
def get_owner_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    my_exps = db.query(Experience).filter(Experience.owner_id == current_user.id).all()
    my_exp_ids = [e.id for e in my_exps]
    total = len(my_exps)
    active = sum(1 for e in my_exps if e.is_active and e.is_approved)
    inactive = sum(1 for e in my_exps if not e.is_active)
    pending = sum(1 for e in my_exps if not e.is_approved)

    ratings = db.query(Rating).filter(Rating.experience_id.in_(my_exp_ids)).all() if my_exp_ids else []
    total_ratings = len(ratings)
    avg_rating = round(sum(r.score for r in ratings) / len(ratings), 1) if ratings else None

    categories = set()
    for e in my_exps:
        cat = e.category.value if hasattr(e.category, "value") else e.category
        categories.add(cat)

    return {
        "total_hotspots": total,
        "active_hotspots": active,
        "inactive_hotspots": inactive,
        "pending_approval": pending,
        "total_ratings": total_ratings,
        "avg_rating": avg_rating,
        "total_categories": len(categories),
    }


@router.get("/{exp_id}", response_model=ExperienceResponse)
def get_experience(exp_id: int, db: Session = Depends(get_db)):
    exp = db.query(Experience).filter(Experience.id == exp_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experience not found")
    return _exp_to_response(exp, db)


@router.post("/", response_model=ExperienceResponse, status_code=201)
def create_experience(
    data: ExperienceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    exp = Experience(
        title=data.title,
        description=data.description,
        category=data.category,
        location=data.location,
        province=data.province,
        price=data.price,
        duration_hours=data.duration_hours,
        max_participants=data.max_participants,
        image_url=data.image_url,
        owner_id=current_user.id,
    )
    db.add(exp)
    db.commit()
    db.refresh(exp)
    return _exp_to_response(exp, db)


# ── Owner: Update Experience ─────────────────────────────
@router.put("/{exp_id}", response_model=ExperienceResponse)
def update_experience(
    exp_id: int,
    data: ExperienceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    exp = db.query(Experience).filter(Experience.id == exp_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experience not found")
    if exp.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only edit your own hotspots")

    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    for field, value in update_data.items():
        setattr(exp, field, value)

    exp.is_approved = False
    exp.is_active = True
    exp.rejection_reason = None
    exp.rejected_at = None
    db.commit()
    db.refresh(exp)
    return _exp_to_response(exp, db)


# ── Owner: Delete Experience ─────────────────────────────
@router.delete("/{exp_id}")
def delete_experience(
    exp_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    exp = db.query(Experience).filter(Experience.id == exp_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experience not found")
    if exp.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own hotspots")

    db.delete(exp)
    db.commit()
    return {"message": "Hotspot deleted successfully", "id": exp_id}


# ── Owner: Toggle Active Status ──────────────────────────
@router.put("/{exp_id}/toggle-active")
def toggle_active(
    exp_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    exp = db.query(Experience).filter(Experience.id == exp_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experience not found")
    if exp.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only modify your own hotspots")

    exp.is_active = not exp.is_active
    db.commit()
    db.refresh(exp)
    return {
        "message": f"Hotspot {'activated' if exp.is_active else 'deactivated'}",
        "is_active": exp.is_active,
    }


# ── Trip itinerary ────────────────────────────────────────
@router.get("/trips/{trip_id}/itinerary", response_model=TripResponse)
def get_itinerary(
    trip_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == current_user.id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return _trip_to_response(trip)


@router.delete("/trips/{trip_id}")
def delete_trip(
    trip_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == current_user.id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    db.delete(trip)
    db.commit()
    return {"message": "Trip deleted"}


@router.put("/trips/{trip_id}", response_model=TripResponse)
def update_trip(
    trip_id: int,
    data: TripUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == current_user.id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    if data.title is not None:
        trip.title = data.title
    if data.destination is not None:
        trip.destination = data.destination
    if data.start_date is not None:
        trip.start_date = data.start_date
    if data.end_date is not None:
        trip.end_date = data.end_date
    if data.notes is not None:
        trip.notes = data.notes

    if trip.end_date < trip.start_date:
        raise HTTPException(status_code=400, detail="End date must be after start date")

    db.commit()
    db.refresh(trip)
    return _trip_to_response(trip)


# ── Add experience to trip ────────────────────────────────
@router.post("/trips/add-experience/{experience_id}", response_model=TripResponse, status_code=201)
def add_experience_to_trip(
    experience_id: int,
    data: AddExperienceToTripRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    exp = db.query(Experience).filter(Experience.id == experience_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experience not found")

    destination = data.destination or exp.province or exp.location
    province_name = exp.province or ""

    # Build initial itinerary data with the experience as first entry
    itinerary_entry = {
        "day_number": 1,
        "date": data.start_date.isoformat(),
        "entries": [
            {
                "type": "experience",
                "name": exp.title,
                "location": exp.location,
                "start_time": "",
                "end_time": "",
                "cost": exp.price,
                "description": exp.description,
                "province": exp.province,
                "experience_id": exp.id,
            }
        ],
    }

    trip = Trip(
        user_id=current_user.id,
        title=f"{province_name} Vacation" if province_name else f"{exp.title} - Trip",
        destination=destination,
        start_date=data.start_date,
        end_date=data.end_date,
        notes=json.dumps([itinerary_entry]),
    )
    db.add(trip)
    db.flush()

    td = TripDay(
        trip_id=trip.id,
        day_number=1,
        date=data.start_date,
        activity=exp.title,
        experience_id=exp.id,
        notes=f"Added from experience: {exp.title}",
    )
    db.add(td)

    db.commit()

    _notify_owner_on_itinerary_add(exp.id, current_user, db, visit_date=data.start_date.isoformat())
    db.commit()

    db.refresh(trip)
    return _trip_to_response(trip)


@router.put("/trips/{trip_id}/days/{day_id}", response_model=TripDayResponse)
def update_trip_day(
    trip_id: int,
    day_id: int,
    data: TripDayUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == current_user.id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    day = db.query(TripDay).filter(TripDay.id == day_id, TripDay.trip_id == trip_id).first()
    if not day:
        raise HTTPException(status_code=404, detail="Trip day not found")

    if data.day_number is not None:
        day.day_number = data.day_number
    if data.date is not None:
        day.date = data.date
    if data.activity is not None:
        day.activity = data.activity
    if data.experience_id is not None:
        day.experience_id = data.experience_id
    if data.notes is not None:
        day.notes = data.notes

    db.commit()
    db.refresh(day)

    return TripDayResponse(
        id=day.id,
        day_number=day.day_number,
        date=day.date,
        activity=day.activity,
        experience_id=day.experience_id,
        notes=day.notes,
        experience_title=day.experience.title if day.experience else None,
    )


@router.delete("/trips/{trip_id}/days/{day_id}")
def delete_trip_day(
    trip_id: int,
    day_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == current_user.id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    day = db.query(TripDay).filter(TripDay.id == day_id, TripDay.trip_id == trip_id).first()
    if not day:
        raise HTTPException(status_code=404, detail="Trip day not found")

    db.delete(day)
    db.commit()
    return {"message": "Day deleted"}


@router.post("/trips/{trip_id}/days", response_model=TripDayResponse, status_code=201)
def add_trip_day(
    trip_id: int,
    data: TripDayInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == current_user.id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    td = TripDay(
        trip_id=trip.id,
        day_number=data.day_number,
        date=data.date,
        activity=data.activity,
        experience_id=data.experience_id,
        notes=data.notes,
    )
    db.add(td)
    db.commit()

    if data.experience_id:
        _notify_owner_on_itinerary_add(data.experience_id, current_user, db, visit_date=data.date.isoformat())
        db.commit()

    db.refresh(td)

    return TripDayResponse(
        id=td.id,
        day_number=td.day_number,
        date=td.date,
        activity=td.activity,
        experience_id=td.experience_id,
        notes=td.notes,
        experience_title=td.experience.title if td.experience else None,
    )


# ── Ratings ───────────────────────────────────────────────
@router.get("/{exp_id}/ratings", response_model=list[RatingResponse])
def get_ratings(exp_id: int, db: Session = Depends(get_db)):
    ratings = db.query(Rating).filter(Rating.experience_id == exp_id, Rating.is_approved == True).all()
    result = []
    for r in ratings:
        resp = RatingResponse(
            id=r.id,
            user_id=r.user_id,
            experience_id=r.experience_id,
            score=r.score,
            comment=r.comment,
            created_at=r.created_at,
            user_name=r.user.full_name if r.user else None,
        )
        result.append(resp)
    return result


@router.post("/{exp_id}/ratings", response_model=RatingResponse, status_code=201)
def rate_experience(
    exp_id: int,
    data: RatingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    exp = db.query(Experience).filter(Experience.id == exp_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experience not found")

    if current_user.role.value == "tourist":
        in_itinerary = db.query(TripDay).join(Trip).filter(
            Trip.user_id == current_user.id,
            TripDay.experience_id == exp_id,
        ).first()
        if not in_itinerary:
            raise HTTPException(
                status_code=403,
                detail="You can only rate an experience after adding it to your trip itinerary",
            )

    if data.comment and len(data.comment) > 500:
        raise HTTPException(status_code=400, detail="Comment must be 500 characters or fewer")

    existing = db.query(Rating).filter(
        Rating.user_id == current_user.id,
        Rating.experience_id == exp_id,
    ).first()

    if existing:
        existing.score = data.score
        existing.comment = data.comment
        db.commit()
        db.refresh(existing)
        return RatingResponse(
            id=existing.id,
            user_id=existing.user_id,
            experience_id=existing.experience_id,
            score=existing.score,
            comment=existing.comment,
            created_at=existing.created_at,
            user_name=current_user.full_name,
        )

    rating = Rating(
        user_id=current_user.id,
        experience_id=exp_id,
        score=data.score,
        comment=data.comment,
    )
    db.add(rating)
    db.commit()
    db.refresh(rating)
    return RatingResponse(
        id=rating.id,
        user_id=rating.user_id,
        experience_id=rating.experience_id,
        score=rating.score,
        comment=rating.comment,
        created_at=rating.created_at,
        user_name=current_user.full_name,
    )


# ── Business Analytics ────────────────────────────────────
@router.get("/analytics/overview")
def get_analytics_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    my_exp_ids = [e.id for e in db.query(Experience.id).filter(Experience.owner_id == current_user.id).all()]

    if not my_exp_ids:
        return {
            "total_customers": 0,
            "total_reviews": 0,
            "avg_rating": 0,
            "star_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
            "monthly_customers": [],
            "monthly_ratings": [],
            "recent_reviews": [],
        }

    ratings = db.query(Rating).filter(Rating.experience_id.in_(my_exp_ids)).all()

    total_customers = len(set(r.user_id for r in ratings))
    total_reviews = len(ratings)
    avg_rating = round(sum(r.score for r in ratings) / len(ratings), 1) if ratings else 0

    star_dist = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for r in ratings:
        star_dist[r.score] = star_dist.get(r.score, 0) + 1

    monthly_customers = defaultdict(set)
    monthly_rating_scores = defaultdict(list)
    for r in ratings:
        month_key = r.created_at.strftime("%Y-%m")
        monthly_customers[month_key].add(r.user_id)
        monthly_rating_scores[month_key].append(r.score)

    mc_list = []
    mr_list = []
    all_months = sorted(set(list(monthly_customers.keys()) + list(monthly_rating_scores.keys())))
    for m in all_months:
        mc_list.append({"month": m, "count": len(monthly_customers.get(m, set()))})
        scores = monthly_rating_scores.get(m, [])
        mr_list.append({"month": m, "avg_rating": round(sum(scores) / len(scores), 1) if scores else 0, "count": len(scores)})

    recent = db.query(Rating).filter(Rating.experience_id.in_(my_exp_ids)).order_by(Rating.created_at.desc()).limit(10).all()
    recent_exp_ids = list(set(r.experience_id for r in recent))
    recent_exp_map = {}
    if recent_exp_ids:
        for exp in db.query(Experience).filter(Experience.id.in_(recent_exp_ids)).all():
            recent_exp_map[exp.id] = exp
    recent_reviews = []
    for r in recent:
        exp = recent_exp_map.get(r.experience_id)
        recent_reviews.append({
            "id": r.id,
            "user_name": r.user.full_name if r.user else "Anonymous",
            "experience_title": exp.title if exp else "Unknown",
            "score": r.score,
            "comment": r.comment,
            "created_at": r.created_at.isoformat(),
        })

    return {
        "total_customers": total_customers,
        "total_reviews": total_reviews,
        "avg_rating": avg_rating,
        "star_distribution": star_dist,
        "monthly_customers": mc_list,
        "monthly_ratings": mr_list,
        "recent_reviews": recent_reviews,
    }


# ── Travel Journal ───────────────────────────────────────

@router.get("/journals/mine", response_model=list[JournalResponse])
def list_my_journals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    journals = db.query(TravelJournal).filter(
        TravelJournal.user_id == current_user.id
    ).order_by(TravelJournal.created_at.desc()).all()

    return [
        JournalResponse(
            id=j.id,
            user_id=j.user_id,
            experience_id=j.experience_id,
            experience_title=j.experience.title if j.experience else None,
            title=j.title,
            content=j.content,
            location=j.location,
            visit_date=j.visit_date,
            mood=j.mood,
            created_at=j.created_at,
            updated_at=j.updated_at,
        )
        for j in journals
    ]


@router.post("/journals", response_model=JournalResponse, status_code=201)
def create_journal(
    data: JournalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if data.experience_id:
        exp = db.query(Experience).filter(Experience.id == data.experience_id).first()
        if not exp:
            raise HTTPException(status_code=404, detail="Experience not found")

    journal = TravelJournal(
        user_id=current_user.id,
        experience_id=data.experience_id,
        title=data.title,
        content=data.content,
        location=data.location,
        visit_date=data.visit_date,
        mood=data.mood,
    )
    db.add(journal)
    db.commit()
    db.refresh(journal)

    return JournalResponse(
        id=journal.id,
        user_id=journal.user_id,
        experience_id=journal.experience_id,
        experience_title=journal.experience.title if journal.experience else None,
        title=journal.title,
        content=journal.content,
        location=journal.location,
        visit_date=journal.visit_date,
        mood=journal.mood,
        created_at=journal.created_at,
        updated_at=journal.updated_at,
    )


@router.put("/journals/{journal_id}", response_model=JournalResponse)
def update_journal(
    journal_id: int,
    data: JournalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    journal = db.query(TravelJournal).filter(
        TravelJournal.id == journal_id,
        TravelJournal.user_id == current_user.id,
    ).first()
    if not journal:
        raise HTTPException(status_code=404, detail="Journal entry not found")

    if data.experience_id is not None:
        if data.experience_id != journal.experience_id:
            exp = db.query(Experience).filter(Experience.id == data.experience_id).first()
            if not exp:
                raise HTTPException(status_code=404, detail="Experience not found")
        journal.experience_id = data.experience_id

    if data.title is not None:
        journal.title = data.title
    if data.content is not None:
        journal.content = data.content
    if data.location is not None:
        journal.location = data.location
    if data.visit_date is not None:
        journal.visit_date = data.visit_date
    if data.mood is not None:
        journal.mood = data.mood

    db.commit()
    db.refresh(journal)

    return JournalResponse(
        id=journal.id,
        user_id=journal.user_id,
        experience_id=journal.experience_id,
        experience_title=journal.experience.title if journal.experience else None,
        title=journal.title,
        content=journal.content,
        location=journal.location,
        visit_date=journal.visit_date,
        mood=journal.mood,
        created_at=journal.created_at,
        updated_at=journal.updated_at,
    )


@router.delete("/journals/{journal_id}")
def delete_journal(
    journal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    journal = db.query(TravelJournal).filter(
        TravelJournal.id == journal_id,
        TravelJournal.user_id == current_user.id,
    ).first()
    if not journal:
        raise HTTPException(status_code=404, detail="Journal entry not found")

    db.delete(journal)
    db.commit()

    return {"message": "Journal entry deleted", "id": journal_id}


# ── Review History ───────────────────────────────────────

@router.get("/reviews/mine", response_model=list[ReviewHistoryItem])
def list_my_reviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ratings = db.query(Rating).filter(
        Rating.user_id == current_user.id
    ).order_by(Rating.created_at.desc()).all()

    return [
        ReviewHistoryItem(
            id=r.id,
            experience_id=r.experience_id,
            experience_title=r.experience.title if r.experience else None,
            experience_location=r.experience.location if r.experience else None,
            score=r.score,
            comment=r.comment,
            is_approved=r.is_approved,
            rejected_at=r.rejected_at,
            created_at=r.created_at,
        )
        for r in ratings
    ]


# ── Host Reviews ────────────────────────────────────────

@router.get("/owner/reviews", response_model=list[HostReviewItem])
def list_owner_reviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    my_exp_ids = [e.id for e in db.query(Experience.id).filter(Experience.owner_id == current_user.id).all()]
    if not my_exp_ids:
        return []

    ratings = db.query(Rating).filter(
        Rating.experience_id.in_(my_exp_ids)
    ).order_by(Rating.created_at.desc()).all()

    return [
        HostReviewItem(
            id=r.id,
            user_name=r.user.full_name if r.user else "Anonymous",
            experience_id=r.experience_id,
            experience_title=r.experience.title if r.experience else "Unknown",
            score=r.score,
            comment=r.comment,
            is_approved=r.is_approved,
            created_at=r.created_at,
        )
        for r in ratings
    ]


# ── Host Performance ────────────────────────────────────

@router.get("/owner/performance", response_model=list[ExperiencePerformance])
def get_owner_performance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    my_exps = db.query(Experience).filter(Experience.owner_id == current_user.id).all()
    if not my_exps:
        return []

    ids = [e.id for e in my_exps]
    all_ratings = db.query(Rating).filter(Rating.experience_id.in_(ids)).order_by(Rating.created_at).all()

    ratings_by_exp = {}
    for r in all_ratings:
        ratings_by_exp.setdefault(r.experience_id, []).append(r)

    result = []
    for exp in my_exps:
        ratings = ratings_by_exp.get(exp.id, [])
        total = len(ratings)
        avg = round(sum(r.score for r in ratings) / total, 1) if total else 0
        unique = len(set(r.user_id for r in ratings))

        star_dist = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for r in ratings:
            star_dist[r.score] = star_dist.get(r.score, 0) + 1

        trend = "stable"
        if total >= 4:
            mid = total // 2
            first_half = sum(r.score for r in ratings[:mid]) / mid
            second_half = sum(r.score for r in ratings[mid:]) / (total - mid)
            if second_half - first_half > 0.5:
                trend = "improving"
            elif first_half - second_half > 0.5:
                trend = "declining"

        result.append(ExperiencePerformance(
            experience_id=exp.id,
            title=exp.title,
            category=exp.category.value if hasattr(exp.category, "value") else exp.category,
            location=exp.location,
            total_ratings=total,
            avg_rating=avg,
            star_distribution=star_dist,
            unique_reviewers=unique,
            trend=trend,
        ))

    return sorted(result, key=lambda x: x.avg_rating or 0, reverse=True)
