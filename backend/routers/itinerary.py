"""Smart Itinerary Planner API.

All routes require authentication and are scoped to the owning tourist.
Business logic lives in services/itinerary_service.py.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from models.experience import Experience, Itinerary, ItineraryItem
from routers.auth import get_current_user
from schemas.itinerary import (
    GenerateItineraryRequest, ItineraryResponse, ItinerarySummary,
    UpdateItineraryRequest, ReplaceItemRequest, AlternativeExperience,
)
from services import itinerary_service as svc

router = APIRouter(prefix="/api/itinerary", tags=["itinerary"])

PACES = {"relaxed", "balanced", "packed"}
BUDGET_PREFS = {"budget", "mid", "luxury"}


def _validate_prefs(data: GenerateItineraryRequest):
    pace = (data.pace or "balanced").lower()
    if pace not in PACES:
        raise HTTPException(status_code=400, detail="Invalid pace. Use relaxed, balanced or packed.")
    bp = (data.budget_preference or "mid").lower()
    if bp not in BUDGET_PREFS:
        raise HTTPException(status_code=400, detail="Invalid budget preference.")
    if data.budget is not None and data.budget < 0:
        raise HTTPException(status_code=400, detail="Budget cannot be negative.")


def _prefs_from_request(data: GenerateItineraryRequest):
    return {
        "province": (data.province or "").strip() or None,
        "num_days": int(data.num_days),
        "budget": data.budget,
        "pace": (data.pace or "balanced").lower(),
        "interests": [i for i in (data.interests or []) if i in svc.INTEREST_LABELS],
        "experience_type": data.experience_type,
        "min_rating": float(data.min_rating or 0),
        "budget_preference": (data.budget_preference or "mid").lower(),
    }


def _owned(db: Session, user: User, itinerary_id: int) -> Itinerary:
    itin = db.query(Itinerary).filter(
        Itinerary.id == itinerary_id, Itinerary.user_id == user.id
    ).first()
    if not itin:
        raise HTTPException(status_code=404, detail="Itinerary not found.")
    return itin


def _parse_time(value, default):
    if not value:
        return default
    try:
        hh, mm = value.split(":")[:2]
        return int(hh) * 60 + int(mm)
    except (ValueError, AttributeError):
        return default


# ── Generate ──────────────────────────────────────────────────────

@router.post("/generate", response_model=ItineraryResponse, status_code=201)
def generate_itinerary(
    data: GenerateItineraryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _validate_prefs(data)
    prefs = _prefs_from_request(data)
    days_out, total_cost, activity_count, warning = svc.generate_plan(db, prefs)
    if not days_out:
        raise HTTPException(
            status_code=422,
            detail=warning or "We couldn't build an itinerary from those preferences.",
        )
    itin = svc.save_plan(db, current_user, prefs, days_out, total_cost, activity_count, title=data.title)
    resp = svc.to_response(itin, db)
    resp["warning"] = warning
    return resp


# ── List / read ───────────────────────────────────────────────────

@router.get("", response_model=list[ItinerarySummary])
def list_itineraries(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    itins = (
        db.query(Itinerary)
        .filter(Itinerary.user_id == current_user.id)
        .order_by(Itinerary.updated_at.desc(), Itinerary.created_at.desc())
        .all()
    )
    out = []
    for it in itins:
        out.append({
            "id": it.id,
            "title": it.title,
            "province": it.province,
            "num_days": it.num_days,
            "estimated_cost": it.estimated_cost or 0,
            "budget": it.budget,
            "activity_count": sum(1 for i in it.items if i.experience_id),
            "created_at": it.created_at,
            "updated_at": it.updated_at,
        })
    return out


@router.get("/{itinerary_id}", response_model=ItineraryResponse)
def get_itinerary(
    itinerary_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    itin = _owned(db, current_user, itinerary_id)
    return svc.to_response(itin, db)


# ── Update / delete ───────────────────────────────────────────────

@router.put("/{itinerary_id}", response_model=ItineraryResponse)
def update_itinerary(
    itinerary_id: int,
    data: UpdateItineraryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    itin = _owned(db, current_user, itinerary_id)
    if data.title is not None:
        itin.title = data.title

    if data.items is not None:
        exp_ids = [i.experience_id for i in data.items]
        exps = {e.id: e for e in db.query(Experience).filter(Experience.id.in_(exp_ids)).all()} if exp_ids else {}
        for i in data.items:
            e = exps.get(i.experience_id)
            if not e:
                raise HTTPException(status_code=400, detail=f"Experience {i.experience_id} was not found.")
            if not (e.is_active and e.is_approved):
                raise HTTPException(status_code=400, detail=f"'{e.title}' is no longer available.")
        db.query(ItineraryItem).filter(ItineraryItem.itinerary_id == itin.id).delete()
        for order, i in enumerate(data.items):
            e = exps[i.experience_id]
            dur = int(max(0.75, min(float(e.duration_hours or svc.DEFAULT_DURATION), 6.0)) * 60)
            start = _parse_time(i.start_time, 9 * 60)
            end = _parse_time(i.end_time, start + dur)
            db.add(ItineraryItem(
                itinerary_id=itin.id, experience_id=e.id, item_type="experience",
                title=e.title, day_number=i.day_number, start_time=svc._fmt(start),
                end_time=svc._fmt(end), sort_order=i.sort_order if i.sort_order else order,
                estimated_cost=float(e.price or 0), recommendation_score=0,
                reason="Added by you",
            ))
        itin.estimated_cost = round(sum(float(exps[i.experience_id].price or 0) for i in data.items), 2)

    db.commit()
    db.refresh(itin)
    return svc.to_response(itin, db)


@router.delete("/{itinerary_id}")
def delete_itinerary(
    itinerary_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    itin = _owned(db, current_user, itinerary_id)
    db.delete(itin)
    db.commit()
    return {"message": "Itinerary deleted."}


# ── Regenerate ────────────────────────────────────────────────────

@router.post("/{itinerary_id}/regenerate", response_model=ItineraryResponse)
def regenerate_itinerary(
    itinerary_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    itin = _owned(db, current_user, itinerary_id)
    prefs = svc._prefs_from_itinerary(itin)
    days_out, total_cost, activity_count, warning = svc.generate_plan(db, prefs)
    if not days_out:
        raise HTTPException(status_code=422, detail=warning or "Could not regenerate the itinerary.")
    db.query(ItineraryItem).filter(ItineraryItem.itinerary_id == itin.id).delete()
    db.flush()
    for day in days_out:
        for order, entry in enumerate(day["items"]):
            kind, label, start, end, cost, score, reason = entry[:7]
            exp = entry[7] if kind == "experience" else None
            db.add(ItineraryItem(
                itinerary_id=itin.id, experience_id=exp.id if exp else None,
                item_type=kind, title=label, day_number=day["day_number"],
                start_time=svc._fmt(start), end_time=svc._fmt(end), sort_order=order,
                estimated_cost=cost, recommendation_score=score, reason=reason,
            ))
    itin.estimated_cost = total_cost
    db.commit()
    db.refresh(itin)
    resp = svc.to_response(itin, db)
    resp["warning"] = warning
    return resp


@router.post("/{itinerary_id}/days/{day_number}/regenerate", response_model=ItineraryResponse)
def regenerate_day(
    itinerary_id: int,
    day_number: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    itin = _owned(db, current_user, itinerary_id)
    if day_number < 1 or day_number > itin.num_days:
        raise HTTPException(status_code=400, detail="Invalid day number.")
    entries = svc.regenerate_day(db, itin, day_number)
    if not entries:
        raise HTTPException(status_code=422, detail="No alternative experiences are available for that day.")
    db.query(ItineraryItem).filter(
        ItineraryItem.itinerary_id == itin.id, ItineraryItem.day_number == day_number
    ).delete()
    for order, entry in enumerate(entries):
        kind, label, start, end, cost, score, reason = entry[:7]
        exp = entry[7] if kind == "experience" else None
        db.add(ItineraryItem(
            itinerary_id=itin.id, experience_id=exp.id if exp else None,
            item_type=kind, title=label, day_number=day_number,
            start_time=svc._fmt(start), end_time=svc._fmt(end), sort_order=order,
            estimated_cost=cost, recommendation_score=score, reason=reason,
        ))
    itin.estimated_cost = round(sum(i.estimated_cost or 0 for i in itin.items if i.experience_id), 2)
    db.commit()
    db.refresh(itin)
    return svc.to_response(itin, db)


# ── Item operations ───────────────────────────────────────────────

@router.get("/{itinerary_id}/items/{item_id}/alternatives", response_model=list[AlternativeExperience])
def item_alternatives(
    itinerary_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    itin = _owned(db, current_user, itinerary_id)
    item = db.query(ItineraryItem).filter(
        ItineraryItem.id == item_id, ItineraryItem.itinerary_id == itin.id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found.")
    return svc.alternatives_for(db, itin, item)


@router.post("/{itinerary_id}/items/{item_id}/replace", response_model=ItineraryResponse)
def replace_item(
    itinerary_id: int,
    item_id: int,
    data: ReplaceItemRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    itin = _owned(db, current_user, itinerary_id)
    item = db.query(ItineraryItem).filter(
        ItineraryItem.id == item_id, ItineraryItem.itinerary_id == itin.id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found.")

    used = {i.experience_id for i in itin.items if i.experience_id and i.id != item.id}
    if data.experience_id:
        exp = db.query(Experience).filter(Experience.id == data.experience_id).first()
        if not exp or not (exp.is_active and exp.is_approved):
            raise HTTPException(status_code=400, detail="That experience is not available.")
        score, reason = 0.0, "Replaced by you"
    else:
        alts = svc.alternatives_for(db, itin, item, limit=25)
        alt = next((a for a in alts if a["experience_id"] not in used), (alts[0] if alts else None))
        if not alt:
            raise HTTPException(status_code=422, detail="No alternative experiences are available.")
        exp = db.query(Experience).filter(Experience.id == alt["experience_id"]).first()
        score, reason = alt["score"], alt["reason"]

    dur = int(max(0.75, min(float(exp.duration_hours or svc.DEFAULT_DURATION), 6.0)) * 60)
    start = _parse_time(item.start_time, 9 * 60)
    item.experience_id = exp.id
    item.item_type = "experience"
    item.title = exp.title
    item.end_time = svc._fmt(start + dur)
    item.estimated_cost = float(exp.price or 0)
    item.recommendation_score = score
    item.reason = reason
    itin.estimated_cost = round(sum(i.estimated_cost or 0 for i in itin.items if i.experience_id), 2)
    db.commit()
    db.refresh(itin)
    return svc.to_response(itin, db)


@router.delete("/{itinerary_id}/items/{item_id}", response_model=ItineraryResponse)
def remove_item(
    itinerary_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    itin = _owned(db, current_user, itinerary_id)
    item = db.query(ItineraryItem).filter(
        ItineraryItem.id == item_id, ItineraryItem.itinerary_id == itin.id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found.")
    db.delete(item)
    db.flush()
    itin.estimated_cost = round(sum(i.estimated_cost or 0 for i in itin.items if i.experience_id), 2)
    db.commit()
    db.refresh(itin)
    return svc.to_response(itin, db)


@router.post("/{itinerary_id}/items", response_model=ItineraryResponse, status_code=201)
def add_item(
    itinerary_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    itin = _owned(db, current_user, itinerary_id)
    experience_id = payload.get("experience_id")
    day_number = int(payload.get("day_number") or 1)
    if day_number < 1 or day_number > itin.num_days:
        raise HTTPException(status_code=400, detail="Invalid day number.")
    exp = db.query(Experience).filter(Experience.id == experience_id).first()
    if not exp or not (exp.is_active and exp.is_approved):
        raise HTTPException(status_code=400, detail="That experience is not available.")
    if any(i.experience_id == exp.id for i in itin.items):
        raise HTTPException(status_code=400, detail="That experience is already in your itinerary.")

    day_items = [i for i in itin.items if i.day_number == day_number]
    last_end = max((_parse_time(i.end_time, 9 * 60) for i in day_items), default=9 * 60 - svc.TRAVEL_MIN)
    start = last_end + svc.TRAVEL_MIN
    dur = int(max(0.75, min(float(exp.duration_hours or svc.DEFAULT_DURATION), 6.0)) * 60)
    if start + dur > svc.CLOSE_MIN:
        start = 9 * 60  # fall back to the start of the day
    db.add(ItineraryItem(
        itinerary_id=itin.id, experience_id=exp.id, item_type="experience", title=exp.title,
        day_number=day_number, start_time=svc._fmt(start), end_time=svc._fmt(start + dur),
        sort_order=len(day_items), estimated_cost=float(exp.price or 0),
        recommendation_score=0, reason="Added by you",
    ))
    itin.estimated_cost = round(sum(i.estimated_cost or 0 for i in itin.items if i.experience_id) + float(exp.price or 0), 2)
    db.commit()
    db.refresh(itin)
    return svc.to_response(itin, db)
