import json
from datetime import date, datetime, timedelta, timezone
from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func, extract

from database import get_db
from models.user import User
from models.experience import (
    Experience, ExperienceEvent, UserPreference, Trip, TripDay, ItineraryAdd, Rating, CulturalCategory, TravelJournal,
)
from models.notification import Notification
from schemas.experience import (
    ExperienceCreate, ExperienceUpdate, ExperienceResponse,
    PreferenceSet, PreferenceResponse,
    TripCreate, TripUpdate, TripDayUpdate, TripDayInput, TripResponse, TripDayResponse,
    AddExperienceToTripRequest, TrackItineraryAddsRequest,
    RatingCreate, RatingResponse,
    JournalCreate, JournalUpdate, JournalResponse, ReviewHistoryItem,
    HostReviewItem, ExperiencePerformance,
    GenerateItineraryRequest, GenerateItineraryResponse, GeneratedDay, ItineraryEntry,
)
from routers.auth import get_current_user, get_optional_user
from cache import get as cache_get, set as cache_set

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
        ic = db.query(func.count(ItineraryAdd.id)).filter(
            ItineraryAdd.experience_id == exp.id).scalar()
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


# ── Lightweight event tracking helper ─────────────────────
def _record_event(db: Session, experience_id: int, event_type: str, user=None):
    """Insert an ExperienceEvent row (profile_view | search_appearance | contact_click)."""
    db.add(ExperienceEvent(
        experience_id=experience_id,
        event_type=event_type,
        user_id=user.id if user else None,
    ))
    db.flush()


# ── Itinerary-add tracking helper ──────────────────────────
def _record_itinerary_adds(trip_id: int, experience_ids, tourist: User, db: Session):
    """Record that the tourist added these experiences to this trip (deduped per trip)."""
    ids = [i for i in (experience_ids or []) if i]
    if not ids:
        return
    existing = set(r[0] for r in db.query(ItineraryAdd.experience_id).filter(
        ItineraryAdd.trip_id == trip_id,
        ItineraryAdd.experience_id.in_(ids),
    ).all())
    for eid in ids:
        if eid in existing:
            continue
        db.add(ItineraryAdd(user_id=tourist.id, experience_id=eid, trip_id=trip_id))
    db.flush()


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
        exps = db.query(Experience).options(selectinload(Experience.owner)).filter(
            Experience.is_active == True, Experience.is_approved == True,
            Experience.category.in_(cats),
        ).limit(6).all()

    if not exps:
        exps = db.query(Experience).options(selectinload(Experience.owner)).filter(
            Experience.is_active == True, Experience.is_approved == True,
        ).limit(6).all()

    ids = [e.id for e in exps]
    if ids:
        rating_rows = db.query(
            Rating.experience_id, func.avg(Rating.score), func.count(Rating.id)
        ).filter(Rating.experience_id.in_(ids), Rating.is_approved == True).group_by(Rating.experience_id).all()
        rating_agg = {r[0]: (r[1], r[2]) for r in rating_rows}
        itin_rows = db.query(ItineraryAdd.experience_id, func.count(ItineraryAdd.id)).filter(ItineraryAdd.experience_id.in_(ids)).group_by(ItineraryAdd.experience_id).all()
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


# ── Provinces ─────────────────────────────────────────────
@router.get("/provinces")
def list_provinces(db: Session = Depends(get_db)):
    cached = cache_get("provinces")
    if cached is not None:
        return cached
    rows = db.query(Experience.province).filter(
        Experience.province.isnot(None),
        Experience.is_active == True,
        Experience.is_approved == True,
    ).distinct().all()
    provinces = sorted({r[0] for r in rows if r[0].strip()})
    result = [{"value": p, "label": p} for p in provinces]
    cache_set("provinces", result, ttl_seconds=300)
    return result


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
        exps = db.query(Experience).options(selectinload(Experience.owner)).filter(Experience.is_active == True, Experience.is_approved == True).limit(6).all()
    else:
        cats = [c.strip() for c in pref.categories.split(",") if c.strip()]
        exps = db.query(Experience).options(selectinload(Experience.owner)).filter(
            Experience.is_active == True,
            Experience.is_approved == True,
            Experience.category.in_(cats),
        ).all()
        if not exps:
            exps = db.query(Experience).options(selectinload(Experience.owner)).filter(Experience.is_active == True, Experience.is_approved == True).limit(6).all()

    ids = [e.id for e in exps]
    if ids:
        rating_rows = db.query(
            Rating.experience_id, func.avg(Rating.score), func.count(Rating.id)
        ).filter(Rating.experience_id.in_(ids), Rating.is_approved == True).group_by(Rating.experience_id).all()
        rating_agg = {r[0]: (r[1], r[2]) for r in rating_rows}
        itin_rows = db.query(ItineraryAdd.experience_id, func.count(ItineraryAdd.id)).filter(ItineraryAdd.experience_id.in_(ids)).group_by(ItineraryAdd.experience_id).all()
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

    _record_itinerary_adds(trip.id, [d.experience_id for d in data.days], current_user, db)
    if any(d.experience_id for d in data.days):
        db.commit()

    db.refresh(trip)
    return _trip_to_response(trip)


# ── Experience CRUD ───────────────────────────────────────
@router.get("/", response_model=list[ExperienceResponse])
def list_experiences(
    category: str = None,
    search: str = None,
    province: str = None,
    db: Session = Depends(get_db),
):
    key = f"exps:{category}:{search}:{province}"
    cached = cache_get(key)
    if cached is not None:
        return cached

    q = db.query(Experience).options(selectinload(Experience.owner))
    if category:
        q = q.filter(Experience.category == category)
    if province:
        q = q.filter(Experience.province == province)
    if search:
        q = q.filter(Experience.title.ilike(f"%{search}%"))
    q = q.filter(Experience.is_active == True, Experience.is_approved == True)
    exps = q.all()

    # Track search appearances — how often each experience surfaces in results.
    if search and search.strip():
        for e in exps:
            _record_event(db, e.id, "search_appearance")
        db.commit()
        # Searches must count every time, so never serve a cached list.
        result_ids = [e.id for e in exps]
        if result_ids:
            rating_agg = {}
            itinerary_counts = {}
            rating_rows = db.query(
                Rating.experience_id, func.avg(Rating.score), func.count(Rating.id)
            ).filter(
                Rating.experience_id.in_(result_ids), Rating.is_approved == True
            ).group_by(Rating.experience_id).all()
            rating_agg = {r[0]: (r[1], r[2]) for r in rating_rows}

            itin_rows = db.query(
                ItineraryAdd.experience_id, func.count(ItineraryAdd.id)
            ).filter(ItineraryAdd.experience_id.in_(result_ids)).group_by(ItineraryAdd.experience_id).all()
            itinerary_counts = dict(itin_rows)

            return [_exp_to_response(e, rating_agg=rating_agg, itinerary_counts=itinerary_counts) for e in exps]
        return []

    ids = [e.id for e in exps]

    rating_agg = {}
    itinerary_counts = {}
    if ids:
        rating_rows = db.query(
            Rating.experience_id, func.avg(Rating.score), func.count(Rating.id)
        ).filter(
            Rating.experience_id.in_(ids), Rating.is_approved == True
        ).group_by(Rating.experience_id).all()
        rating_agg = {r[0]: (r[1], r[2]) for r in rating_rows}

        itin_rows = db.query(
            ItineraryAdd.experience_id, func.count(ItineraryAdd.id)
        ).filter(ItineraryAdd.experience_id.in_(ids)).group_by(ItineraryAdd.experience_id).all()
        itinerary_counts = dict(itin_rows)

    result = [_exp_to_response(e, rating_agg=rating_agg, itinerary_counts=itinerary_counts) for e in exps]
    cache_set(key, result, ttl_seconds=30)
    return result


# ── Owner: My Experiences (MUST be before /{exp_id}) ─────
@router.get("/mine", response_model=list[ExperienceResponse])
def list_my_experiences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    exps = db.query(Experience).options(selectinload(Experience.owner)).filter(Experience.owner_id == current_user.id).order_by(Experience.created_at.desc()).all()
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
        ItineraryAdd.experience_id, func.count(ItineraryAdd.id)
    ).filter(ItineraryAdd.experience_id.in_(ids)).group_by(ItineraryAdd.experience_id).all()
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

    ratings = db.query(
        func.count(Rating.id), func.avg(Rating.score)
    ).filter(Rating.experience_id.in_(my_exp_ids)).one() if my_exp_ids else (0, None)
    total_ratings = ratings[0] or 0
    avg_rating = round(ratings[1], 1) if ratings[1] is not None else None

    categories = set()
    for e in my_exps:
        cat = e.category.value if hasattr(e.category, "value") else e.category
        categories.add(cat)

    itinerary_counts = {}
    if my_exp_ids:
        itin_rows = db.query(
            ItineraryAdd.experience_id, func.count(ItineraryAdd.id)
        ).filter(ItineraryAdd.experience_id.in_(my_exp_ids)).group_by(ItineraryAdd.experience_id).all()
        itinerary_counts = {r[0]: r[1] for r in itin_rows}

    most_visited = None
    if my_exps:
        best = max(my_exps, key=lambda e: itinerary_counts.get(e.id, 0))
        visits = itinerary_counts.get(best.id, 0)
        if visits > 0:
            most_visited = {
                "id": best.id,
                "title": best.title,
                "visits": visits,
                "image_url": best.image_url,
                "category": best.category.value if hasattr(best.category, "value") else best.category,
                "location": best.location,
                "province": best.province,
            }

    return {
        "total_hotspots": total,
        "registered_hotspots": total,
        "active_hotspots": active,
        "inactive_hotspots": inactive,
        "pending_approval": pending,
        "total_ratings": total_ratings,
        "avg_rating": avg_rating,
        "total_categories": len(categories),
        "total_itinerary_adds": sum(itinerary_counts.values()),
        "most_visited_hotspot": most_visited,
    }


@router.get("/{exp_id}", response_model=ExperienceResponse)
def get_experience(exp_id: int, db: Session = Depends(get_db)):
    exp = db.query(Experience).filter(Experience.id == exp_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experience not found")
    return _exp_to_response(exp, db)


# ── Event tracking (real visitor actions for business analytics) ──
@router.post("/{exp_id}/view")
def track_profile_view(
    exp_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_user),
):
    """Record that a visitor opened this experience's profile page."""
    exp = db.query(Experience).filter(Experience.id == exp_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experience not found")
    if not (current_user and exp.owner_id == current_user.id):
        _record_event(db, exp.id, "profile_view", current_user)
        db.commit()
    return {"ok": True, "event": "profile_view"}


@router.post("/{exp_id}/contact")
def track_contact_click(
    exp_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_user),
):
    """Record that a visitor requested contact / booking details for this hotspot."""
    exp = db.query(Experience).filter(Experience.id == exp_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experience not found")
    _record_event(db, exp.id, "contact_click", current_user)
    db.commit()
    return {"ok": True, "event": "contact_click"}


def _visitor_type(user) -> str:
    """Return 'local' or 'international' using the stored field, with a phone fallback."""
    if user and user.visitor_type:
        return user.visitor_type.lower()
    phone = (user.phone_number or "").strip() if user else ""
    return "local" if phone.startswith("+27") or phone.startswith("27") or phone.startswith("0") else "international"


# ── Per-hotspot analytics ─────────────────────────────────
@router.get("/{exp_id}/analytics")
def get_experience_analytics(
    exp_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    exp = db.query(Experience).filter(Experience.id == exp_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experience not found")
    if not (current_user.role.value == "admin" or exp.owner_id == current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to view this analytics")

    adds = (
        db.query(ItineraryAdd)
        .options(selectinload(ItineraryAdd.user))
        .filter(ItineraryAdd.experience_id == exp_id)
        .all()
    )

    total_adds = len(adds)
    unique_visitors = len(set(a.user_id for a in adds))

    # Visitor type (local vs international)
    local = sum(1 for a in adds if _visitor_type(a.user) == "local")
    international = total_adds - local
    visitor_types = [
        {"type": "Local", "count": local},
        {"type": "International", "count": international},
    ]

    # Top countries (international visitors by their country)
    country_counts = defaultdict(int)
    for a in adds:
        if a.user and a.user.country and _visitor_type(a.user) == "international":
            country_counts[a.user.country] += 1
    top_countries = [
        {"country": c, "count": n}
        for c, n in sorted(country_counts.items(), key=lambda kv: kv[1], reverse=True)
    ]

    # Views over time (per day) — for the line graph
    daily_counts = defaultdict(int)
    for a in adds:
        daily_counts[a.created_at.date().isoformat()] += 1
    views_over_time = [
        {"date": d, "count": daily_counts[d]}
        for d in sorted(daily_counts.keys())
    ]

    # Views per star rating (an add counts toward the rating that visitor gave this hotspot)
    rating_views = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    if adds:
        user_ids = list(set(a.user_id for a in adds))
        rating_map = dict(
            db.query(Rating.user_id, Rating.score)
            .filter(Rating.experience_id == exp_id, Rating.user_id.in_(user_ids))
            .all()
        )
        for a in adds:
            sc = rating_map.get(a.user_id)
            if sc:
                rating_views[sc] = rating_views.get(sc, 0) + 1
    views_by_rating = [{"rating": r, "views": rating_views.get(r, 0)} for r in range(1, 6)]

    # Most active days (Mon..Sun)
    DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    dow_counts = defaultdict(int)
    for a in adds:
        dow_counts[a.created_at.weekday()] += 1
    active_days = [{"day": DAY_NAMES[i], "count": dow_counts.get(i, 0)} for i in range(7)]

    # Peak times: hourly detail + morning/afternoon/evening + heatmap grid
    hourly_counts = defaultdict(int)
    for a in adds:
        hourly_counts[a.created_at.hour] += 1
    hourly = [{"hour": h, "count": hourly_counts.get(h, 0)} for h in range(24)]
    morning = sum(hourly_counts[h] for h in range(6, 12))
    afternoon = sum(hourly_counts[h] for h in range(12, 18))
    evening = sum(hourly_counts[h] for h in range(18, 24)) + sum(hourly_counts[h] for h in range(0, 6))
    peak_times = [
        {"period": "Morning", "count": morning},
        {"period": "Afternoon", "count": afternoon},
        {"period": "Evening", "count": evening},
    ]
    period_ranges = {
        "Morning": list(range(6, 12)),
        "Afternoon": list(range(12, 18)),
        "Evening": list(range(18, 24)) + list(range(0, 6)),
    }
    peak_heatmap = [
        {
            "period": p,
            "values": [hourly_counts.get(h, 0) if h in hours else 0 for h in range(24)],
        }
        for p, hours in period_ranges.items()
    ]

    # Top performing services (owner's experiences ranked by itinerary adds)
    owner_exp_rows = db.query(Experience.id).filter(Experience.owner_id == current_user.id).all()
    owner_exp_ids = [r[0] for r in owner_exp_rows]
    top_services = []
    if owner_exp_ids:
        adds_by_exp = dict(
            db.query(ItineraryAdd.experience_id, func.count(ItineraryAdd.id))
            .filter(ItineraryAdd.experience_id.in_(owner_exp_ids))
            .group_by(ItineraryAdd.experience_id)
            .all()
        )
        exp_map = {
            e.id: e
            for e in db.query(Experience).filter(Experience.id.in_(owner_exp_ids)).all()
        }
        ranked = sorted(owner_exp_ids, key=lambda i: adds_by_exp.get(i, 0), reverse=True)
        top_services = [
            {"id": i, "title": exp_map[i].title, "views": adds_by_exp.get(i, 0)}
            for i in ranked[:6] if adds_by_exp.get(i, 0) > 0
        ]

    return {
        "experience_id": exp.id,
        "title": exp.title,
        "total_itinerary_adds": total_adds,
        "unique_visitors": unique_visitors,
        "visitor_types": visitor_types,
        "top_countries": top_countries,
        "views_over_time": views_over_time,
        "views_by_rating": views_by_rating,
        "active_days": active_days,
        "hourly": hourly,
        "peak_times": peak_times,
        "peak_heatmap": peak_heatmap,
        "top_services": top_services,
    }


@router.post("/", response_model=ExperienceResponse, status_code=201)
def create_experience(
    data: ExperienceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Each business owner may register at most 3 hotspots.
    owner_count = db.query(Experience).filter(Experience.owner_id == current_user.id).count()
    if owner_count >= 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can register a maximum of 3 hotspots. Delete or deactivate one before adding another.",
        )

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
    _record_itinerary_adds(trip.id, [exp.id], current_user, db)
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
        _record_itinerary_adds(trip.id, [data.experience_id], current_user, db)
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


# ── Itinerary generation (uses existing preferences + real experiences) ──
def _fmt_minutes(mins: int) -> str:
    return f"{mins // 60:02d}:{mins % 60:02d}"


def _break_entry(name: str, start: int, end: int, cost: float = 0):
    return ItineraryEntry(
        type="break",
        name=name,
        start_time=_fmt_minutes(start),
        end_time=_fmt_minutes(end),
        cost=cost,
        duration_hours=round((end - start) / 60, 2),
    )


def _travel_hours(a: str, b: str) -> float:
    if not a or not b:
        return 0
    return 0.5 if a.strip().lower() != b.strip().lower() else 0


@router.post("/trips/generate", response_model=GenerateItineraryResponse)
def generate_itinerary(
    data: GenerateItineraryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if data.end_date < data.start_date:
        raise HTTPException(status_code=400, detail="End date must be after start date")
    if not (data.destination or "").strip():
        raise HTTPException(status_code=400, detail="Destination is required")
    days_count = (data.end_date - data.start_date).days + 1
    if days_count > 30:
        raise HTTPException(status_code=400, detail="Itinerary is too long (max 30 days)")

    # Reuse the traveller's already-saved preferences (no new onboarding step).
    pref = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    prefs = [c.strip() for c in (pref.categories.split(",") if pref and pref.categories else []) if c.strip()]

    q = db.query(Experience).options(selectinload(Experience.owner)).filter(Experience.is_active == True, Experience.is_approved == True)
    if data.exclude_ids:
        q = q.filter(~Experience.id.in_(data.exclude_ids))
    exps = q.all()

    dest = data.destination.strip().lower()
    matched = [
        e for e in exps
        if (e.province and e.province.lower() == dest)
        or (e.location and e.location.lower() == dest)
        or (e.province and dest in e.province.lower())
        or (e.location and dest in e.location.lower())
    ]
    if matched:
        exps = matched
    if not exps:
        # No experiences in that area yet: fall back to all live listings (still real data).
        exps = db.query(Experience).options(selectinload(Experience.owner)).filter(Experience.is_active == True, Experience.is_approved == True).all()

    ids = [e.id for e in exps]
    rating_agg = {}
    itinerary_counts = {}
    if ids:
        rating_agg = dict(
            db.query(Rating.experience_id, func.avg(Rating.score))
            .filter(Rating.experience_id.in_(ids), Rating.is_approved == True)
            .group_by(Rating.experience_id).all()
        )
        itinerary_counts = dict(
            db.query(ItineraryAdd.experience_id, func.count(ItineraryAdd.id))
            .filter(ItineraryAdd.experience_id.in_(ids))
            .group_by(ItineraryAdd.experience_id).all()
        )

    scored = []
    for e in exps:
        cat = e.category.value if hasattr(e.category, "value") else e.category
        pref_match = 2 if cat in prefs else (1 if any(p in cat or cat in p for p in prefs) else 0)
        rating = rating_agg.get(e.id) or 0
        popularity = itinerary_counts.get(e.id) or 0
        score = pref_match * 3.0 + rating * 2.0 + min(popularity, 20) * 0.3
        scored.append({"exp": e, "cat": cat, "pref": pref_match, "rating": rating, "score": score})
    scored.sort(key=lambda x: -x["score"])

    used_ids = set(data.exclude_ids or [])

    # Traditional Cooking spots are reserved for meals only — never scheduled as
    # standalone activities. Everything else is a normal activity.
    activity_pool = [c for c in scored if c["cat"] != "Traditional Cooking"]
    meal_pool = [c for c in scored if c["cat"] == "Traditional Cooking"]

    def build_day(day_index: int):
        entries = []
        cursor = 9 * 60  # 09:00
        last_loc = None
        day_cats = set()
        lunch_added = False
        day_cost = 0
        placed = 0

        def meal_entry(meal_label: str, start: int, end: int):
            for c in meal_pool:
                e = c["exp"]
                if e.id in used_ids:
                    continue
                used_ids.add(e.id)
                return ItineraryEntry(
                    type="meal",
                    name=e.title,
                    meal=meal_label,
                    location=e.location,
                    province=e.province,
                    category="Traditional Cooking",
                    start_time=_fmt_minutes(start),
                    end_time=_fmt_minutes(end),
                    cost=e.price,
                    duration_hours=e.duration_hours,
                    description=e.description,
                    experience_id=e.id,
                    reason=f"Suggested {meal_label} at a Traditional Cooking spot that matches your interests.",
                )
            return _break_entry(meal_label, start, end)

        entries.append(meal_entry("Breakfast", cursor, cursor + 30))
        cursor += 30

        def pick_next():
            for c in activity_pool:
                if c["exp"].id in used_ids:
                    continue
                if c["cat"] in day_cats:
                    continue
                return c
            for c in activity_pool:
                if c["exp"].id not in used_ids:
                    return c
            return None

        while placed < 4:
            cand = pick_next()
            if not cand:
                break
            e = cand["exp"]
            dur = e.duration_hours or 2.0
            dur_min = int(round(dur * 60))
            travel = _travel_hours(last_loc, e.location)
            travel_min = int(travel * 60)

            # Insert lunch if we are crossing the lunch window.
            if not lunch_added and 12 * 60 <= cursor + travel_min <= 14 * 60:
                entries.append(meal_entry("Lunch", cursor, cursor + 60))
                cursor += 60
                lunch_added = True

            start = cursor + travel_min
            end = start + dur_min
            if end > 20 * 60:  # don't run past 20:00
                break
            if travel_min > 0:
                entries.append(_break_entry("Free Time", cursor, cursor + travel_min))

            if cand["pref"] >= 2:
                reason = f"Recommended because it matches your interest in {cand['cat']}."
            elif cand["rating"] and cand["rating"] >= 4.5:
                reason = "Selected for its high rating from other travellers."
            else:
                reason = "Selected as a well-rated cultural experience near your destination."

            entries.append(ItineraryEntry(
                type="experience",
                name=e.title,
                location=e.location,
                province=e.province,
                category=cand["cat"],
                start_time=_fmt_minutes(start),
                end_time=_fmt_minutes(end),
                cost=e.price,
                duration_hours=dur,
                description=e.description,
                experience_id=e.id,
                reason=reason,
            ))
            used_ids.add(e.id)
            day_cats.add(cand["cat"])
            last_loc = e.location
            cursor = end
            placed += 1
            day_cost += e.price

        if cursor < 17 * 60:
            entries.append(_break_entry("Free Time", cursor, 17 * 60))
            cursor = 17 * 60
        if placed >= 1 and cursor <= 19 * 60:
            entries.append(meal_entry("Dinner", cursor, cursor + 60))
        return entries, day_cost

    days_out = []
    total_cost = 0
    activity_count = 0

    if data.day_number is not None:
        if data.day_number < 1 or data.day_number > days_count:
            raise HTTPException(status_code=400, detail="Invalid day number")
        entries, day_cost = build_day(data.day_number - 1)
        days_out.append(GeneratedDay(
            day_number=data.day_number,
            date=date.fromordinal(data.start_date.toordinal() + data.day_number - 1),
            entries=entries,
        ))
        total_cost = day_cost
        activity_count = sum(1 for en in entries if en.type in ("experience", "meal"))
    else:
        for i in range(days_count):
            entries, day_cost = build_day(i)
            days_out.append(GeneratedDay(
                day_number=i + 1,
                date=date.fromordinal(data.start_date.toordinal() + i),
                entries=entries,
            ))
            total_cost += day_cost
            activity_count += sum(1 for en in entries if en.type in ("experience", "meal"))

    return GenerateItineraryResponse(days=days_out, total_cost=total_cost, activity_count=activity_count)


@router.post("/trips/{trip_id}/track-itinerary-adds")
def track_itinerary_adds(
    trip_id: int,
    data: TrackItineraryAddsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == current_user.id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    _record_itinerary_adds(trip_id, data.experience_ids, current_user, db)
    db.commit()
    return {"message": "Itinerary adds recorded", "count": len(data.experience_ids)}


# ── Ratings ───────────────────────────────────────────────
@router.get("/{exp_id}/ratings", response_model=list[RatingResponse])
def get_ratings(exp_id: int, db: Session = Depends(get_db)):
    ratings = (
        db.query(Rating)
        .options(selectinload(Rating.user))
        .filter(Rating.experience_id == exp_id, Rating.is_approved == True)
        .all()
    )
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
PERIOD_DAYS = {"7d": 7, "30d": 30, "90d": 90, "180d": 180, "365d": 365, "12m": 365}


def _perf_status(avg):
    if avg is None:
        return "No reviews"
    if avg >= 4.5:
        return "Excellent"
    if avg >= 3.5:
        return "Good"
    if avg >= 2.5:
        return "Needs attention"
    return "Critical"


@router.get("/analytics/overview")
def get_analytics_overview(
    range: str = "all",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    my_exp_ids = [e.id for e in db.query(Experience.id).filter(Experience.owner_id == current_user.id).all()]

    def _empty_overview():
        return {
            "total_customers": 0,
            "total_reviews": 0,
            "prev_total_reviews": 0,
            "avg_rating": 0,
            "prev_avg_rating": 0,
            "positive_review_pct": 0,
            "prev_positive_review_pct": 0,
            "total_views": 0,
            "prev_total_views": 0,
            "unique_visitors": 0,
            "prev_unique_visitors": 0,
            "total_profile_views": 0,
            "prev_total_profile_views": 0,
            "total_searches": 0,
            "prev_total_searches": 0,
            "total_contacts": 0,
            "prev_total_contacts": 0,
            "star_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
            "monthly_customers": [],
            "monthly_ratings": [],
            "interest_over_time": [],
            "interest_granularity": "day",
            "profile_views_over_time": [],
            "experience_performance": [],
            "recent_reviews": [],
        }

    if not my_exp_ids:
        return _empty_overview()

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    days = PERIOD_DAYS.get(range)
    cutoff = now - timedelta(days=days) if days else None
    prev_cutoff = now - timedelta(days=days * 2) if days else None

    def _ratings_between(start, end=None):
        q = db.query(Rating).filter(Rating.experience_id.in_(my_exp_ids))
        if start:
            q = q.filter(Rating.created_at >= start)
        if end:
            q = q.filter(Rating.created_at < end)
        return q.all()

    ratings = _ratings_between(cutoff)
    prev_ratings = _ratings_between(prev_cutoff, cutoff) if prev_cutoff else []

    total_reviews = len(ratings)
    prev_total_reviews = len(prev_ratings)
    total_customers = len(set(r.user_id for r in ratings))
    avg_rating = round(sum(r.score for r in ratings) / len(ratings), 1) if ratings else 0
    prev_avg_rating = round(sum(r.score for r in prev_ratings) / len(prev_ratings), 1) if prev_ratings else 0
    positive_review_pct = round(
        sum(1 for r in ratings if r.score >= 4) / len(ratings) * 100) if ratings else 0
    prev_positive_review_pct = round(
        sum(1 for r in prev_ratings if r.score >= 4) / len(prev_ratings) * 100) if prev_ratings else 0

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

    # ── Interest ("views") — measured through itinerary adds ──
    def _adds_between(start, end=None):
        q = db.query(ItineraryAdd).filter(ItineraryAdd.experience_id.in_(my_exp_ids))
        if start:
            q = q.filter(ItineraryAdd.created_at >= start)
        if end:
            q = q.filter(ItineraryAdd.created_at < end)
        return q.all()

    itin_adds = _adds_between(cutoff)
    prev_itin_adds = _adds_between(prev_cutoff, cutoff) if prev_cutoff else []

    total_views = len(itin_adds)
    prev_total_views = len(prev_itin_adds)
    unique_visitors = len(set(a.user_id for a in itin_adds))
    prev_unique_visitors = len(set(a.user_id for a in prev_itin_adds))

    # Interest over time — always daily so the frontend can re-bucket to day/week/month.
    daily_interest = defaultdict(int)
    for a in itin_adds:
        daily_interest[a.created_at.strftime("%Y-%m-%d")] += 1
    interest_over_time = [{"period": k, "count": c} for k, c in sorted(daily_interest.items())]
    interest_granularity = "day"

    # ── Tracked events: profile views, search appearances, contact clicks ──
    def _events_between(event_type, start, end=None):
        q = db.query(ExperienceEvent).filter(
            ExperienceEvent.experience_id.in_(my_exp_ids),
            ExperienceEvent.event_type == event_type,
        )
        if start:
            q = q.filter(ExperienceEvent.created_at >= start)
        if end:
            q = q.filter(ExperienceEvent.created_at < end)
        return q.all()

    prof_events = _events_between("profile_view", cutoff)
    prev_prof_events = _events_between("profile_view", prev_cutoff, cutoff) if prev_cutoff else []
    search_events = _events_between("search_appearance", cutoff)
    prev_search_events = _events_between("search_appearance", prev_cutoff, cutoff) if prev_cutoff else []
    contact_events = _events_between("contact_click", cutoff)
    prev_contact_events = _events_between("contact_click", prev_cutoff, cutoff) if prev_cutoff else []

    total_profile_views = len(prof_events)
    prev_total_profile_views = len(prev_prof_events)
    total_searches = len(search_events)
    prev_total_searches = len(prev_search_events)
    total_contacts = len(contact_events)
    prev_total_contacts = len(prev_contact_events)

    daily_profile_views = defaultdict(int)
    for ev in prof_events:
        daily_profile_views[ev.created_at.strftime("%Y-%m-%d")] += 1
    profile_views_over_time = [{"period": k, "count": c} for k, c in sorted(daily_profile_views.items())]

    # ── Per-experience performance within the selected period ──
    views_by_exp = defaultdict(int)
    for a in itin_adds:
        views_by_exp[a.experience_id] += 1
    prev_views_by_exp = defaultdict(int)
    for a in prev_itin_adds:
        prev_views_by_exp[a.experience_id] += 1

    searches_by_exp = defaultdict(int)
    for ev in search_events:
        searches_by_exp[ev.experience_id] += 1
    contacts_by_exp = defaultdict(int)
    for ev in contact_events:
        contacts_by_exp[ev.experience_id] += 1

    scores_by_exp = defaultdict(list)
    for r in ratings:
        scores_by_exp[r.experience_id].append(r.score)
    prev_scores_by_exp = defaultdict(list)
    for r in prev_ratings:
        prev_scores_by_exp[r.experience_id].append(r.score)

    exps = db.query(Experience).filter(Experience.id.in_(my_exp_ids)).all()
    experience_performance = []
    for e in exps:
        scores = scores_by_exp.get(e.id, [])
        prev_scores = prev_scores_by_exp.get(e.id, [])
        cur_avg = round(sum(scores) / len(scores), 1) if scores else None
        prev_avg = round(sum(prev_scores) / len(prev_scores), 1) if prev_scores else None
        trend = "stable"
        if cur_avg is not None and prev_avg is not None and abs(cur_avg - prev_avg) >= 0.5:
            trend = "improving" if cur_avg > prev_avg else "declining"
        elif cur_avg is None and prev_avg is not None:
            trend = "no ratings"
        experience_performance.append({
            "id": e.id,
            "title": e.title,
            "image_url": e.image_url,
            "category": e.category.value if hasattr(e.category, "value") else e.category,
            "views": views_by_exp.get(e.id, 0),
            "searches": searches_by_exp.get(e.id, 0),
            "contacts": contacts_by_exp.get(e.id, 0),
            "reviews": len(scores),
            "avg_rating": cur_avg,
            "status": _perf_status(cur_avg),
            "trend": trend,
        })
    experience_performance.sort(key=lambda x: (x["views"], x["avg_rating"] or 0), reverse=True)

    recent_q = db.query(Rating).options(selectinload(Rating.user)).filter(Rating.experience_id.in_(my_exp_ids))
    if cutoff:
        recent_q = recent_q.filter(Rating.created_at >= cutoff)
    recent = recent_q.order_by(Rating.created_at.desc()).limit(10).all()
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
        "prev_total_reviews": prev_total_reviews,
        "avg_rating": avg_rating,
        "prev_avg_rating": prev_avg_rating,
        "positive_review_pct": positive_review_pct,
        "prev_positive_review_pct": prev_positive_review_pct,
        "total_views": total_views,
        "prev_total_views": prev_total_views,
        "unique_visitors": unique_visitors,
        "prev_unique_visitors": prev_unique_visitors,
        "total_profile_views": total_profile_views,
        "prev_total_profile_views": prev_total_profile_views,
        "total_searches": total_searches,
        "prev_total_searches": prev_total_searches,
        "total_contacts": total_contacts,
        "prev_total_contacts": prev_total_contacts,
        "star_distribution": star_dist,
        "monthly_customers": mc_list,
        "monthly_ratings": mr_list,
        "interest_over_time": interest_over_time,
        "interest_granularity": interest_granularity,
        "profile_views_over_time": profile_views_over_time,
        "experience_performance": experience_performance,
        "recent_reviews": recent_reviews,
    }


# ── Travel Journal ───────────────────────────────────────

@router.get("/journals/mine", response_model=list[JournalResponse])
def list_my_journals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    journals = db.query(TravelJournal).options(selectinload(TravelJournal.experience)).filter(
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
