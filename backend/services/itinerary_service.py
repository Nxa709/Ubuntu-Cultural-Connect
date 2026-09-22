"""Smart cultural itinerary recommendation + generation.

The scoring weights below follow the project brief:
    interests 30 · category 20 · budget 15 · province 10 · rating 10 ·
    duration/time 10 · other tag matches 5

Business rules:
  * only active + approved experiences are ever considered;
  * a stop is never scheduled outside 08:00-18:00;
  * the daily schedule never overlaps (travel gap between stops);
  * the estimated cost stays within the tourist's budget where possible;
  * the itinerary is varied (the same category is capped per trip);
  * every stop carries a human-readable "why it was recommended" reason.
"""
from collections import defaultdict
from datetime import datetime, timezone
from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from models.experience import Experience, Rating, Itinerary, ItineraryItem

# ── Interest taxonomy (keys must match the frontend) ──────────────
INTEREST_LABELS = {
    "traditional_food": "Traditional Food",
    "local_cuisine": "Local Cuisine",
    "arts_crafts": "Arts & Crafts",
    "music_dance": "Music & Dance",
    "history_heritage": "History & Heritage",
    "traditional_clothing": "Traditional Clothing",
    "township_culture": "Township Culture",
    "indigenous_culture": "Indigenous Culture",
    "community_experiences": "Community Experiences",
    "festivals_events": "Festivals & Events",
    "nature_outdoor": "Nature & Outdoor Experiences",
    "museums_historical": "Museums & Historical Sites",
    "local_markets": "Local Markets",
    "traditional_activities": "Traditional Activities",
}

# Maps the existing CulturalCategory enum to the interest taxonomy.
CATEGORY_TAGS = {
    "Traditional Cooking": ["traditional_food", "local_cuisine", "traditional_activities"],
    "Storytelling": ["history_heritage", "indigenous_culture", "community_experiences", "festivals_events"],
    "Music & Dance": ["music_dance", "indigenous_culture", "festivals_events", "community_experiences"],
    "Crafts & Art": ["arts_crafts", "local_markets", "indigenous_culture"],
    "Heritage Tours": ["history_heritage", "museums_historical", "indigenous_culture"],
    "Township Life": ["township_culture", "community_experiences", "music_dance", "local_cuisine"],
    "Rural Heritage": ["indigenous_culture", "traditional_activities", "nature_outdoor", "community_experiences"],
    "Traditional Healing": ["indigenous_culture", "traditional_activities"],
    "Textile & Weaving": ["traditional_clothing", "arts_crafts", "local_markets"],
    "Photography Tours": ["nature_outdoor", "community_experiences"],
    "Nature & Wildlife": ["nature_outdoor"],
    "Accommodation & Lodging": ["community_experiences"],
}

PACE_ACTIVITIES = {"relaxed": 2, "balanced": 3, "packed": 4}
DEFAULT_DURATION = 2.0
OPEN_MIN = 8 * 60          # 08:00
CLOSE_MIN = 18 * 60        # 18:00
TRAVEL_MIN = 30            # travel gap between stops (minutes)
SAME_AREA_MIN = 20
LUNCH_MINUTES = 60


def _cat(exp):
    return exp.category.value if hasattr(exp.category, "value") else exp.category


def _fmt(mins):
    return f"{mins // 60:02d}:{mins % 60:02d}"


def category_tags(cat):
    return CATEGORY_TAGS.get(cat, [])


def rating_map(db: Session, exp_ids):
    if not exp_ids:
        return {}
    rows = (
        db.query(Rating.experience_id, func.avg(Rating.score), func.count(Rating.id))
        .filter(Rating.experience_id.in_(exp_ids), Rating.is_approved == True)
        .group_by(Rating.experience_id)
        .all()
    )
    return {r[0]: (round(float(r[1]), 1) if r[1] is not None else None, r[2] or 0) for r in rows}


# ── Scoring ───────────────────────────────────────────────────────

def score_experience(exp, prefs, rating, per_activity_budget):
    cat = _cat(exp)
    interests = set(prefs.get("interests") or [])
    tags = set(category_tags(cat))
    overlap = tags & interests
    reasons = []

    # 1. Cultural interest match — 30
    interest_ratio = min(1.0, len(overlap) / 2.0) if interests else 0.6
    s_interests = 30 * interest_ratio
    if overlap:
        labels = [INTEREST_LABELS[t] for t in sorted(overlap)]
        reasons.append("Matches your interest in " + ", ".join(labels))

    # 2. Category match — 20
    etype = (prefs.get("experience_type") or "").strip().lower()
    if etype and etype not in ("any", "all"):
        s_category = 20.0 if cat.lower() == etype else 0.0
        if s_category:
            reasons.append(f"It is a {cat} experience, exactly the type you chose")
    else:
        s_category = 20.0 * interest_ratio

    # 3. Budget compatibility — 15
    price = float(exp.price or 0)
    if per_activity_budget and per_activity_budget > 0:
        ratio = price / per_activity_budget
        if ratio <= 1:
            s_budget = 15.0
        elif ratio <= 1.5:
            s_budget = 15.0 * (1.5 - ratio) / 0.5
        else:
            s_budget = 0.0
    else:
        s_budget = 11.0
    bp = (prefs.get("budget_preference") or "mid").lower()
    if bp == "budget" and price <= 250:
        s_budget = min(15.0, s_budget + 2)
    elif bp == "luxury" and price >= 600:
        s_budget = min(15.0, s_budget + 2)

    # 4. Province / location match — 10
    province = (prefs.get("province") or "").strip().lower()
    if province:
        s_prov = 10.0 if (exp.province or "").lower() == province else 4.0
    else:
        s_prov = 8.0

    # 5. Rating — 10
    if rating is not None:
        s_rating = 10.0 * (rating / 5.0)
        if rating >= 4.5:
            reasons.append(f"Highly rated by travellers ({rating}\u2605)")
    else:
        s_rating = 6.0

    # 6. Duration / time compatibility — 10
    dur = float(exp.duration_hours or DEFAULT_DURATION)
    if 1 <= dur <= 4:
        s_dur = 10.0
    elif dur < 1:
        s_dur = 6.0
    else:
        s_dur = max(0.0, 10.0 - (dur - 4) * 3)

    # 7. Other tag matches — 5
    s_other = 5.0 if len(overlap) >= 2 else (2.5 if overlap else 0.0)

    total = s_interests + s_category + s_budget + s_prov + s_rating + s_dur + s_other
    if not reasons:
        reasons.append("A good all-round cultural fit for your trip")
    return round(total, 1), reasons, tags


def _fallback_reason(cat):
    return f"A popular {cat.lower()} experience in the region"


# ── Candidate retrieval ───────────────────────────────────────────

def candidate_experiences(db: Session, prefs):
    q = (
        db.query(Experience)
        .options(selectinload(Experience.owner))
        .filter(Experience.is_active == True, Experience.is_approved == True)
    )
    exps = q.all()
    province = (prefs.get("province") or "").strip()
    if province:
        pl = province.lower()
        matched = [e for e in exps if (e.province or "").lower() == pl]
        if matched:
            exps = matched
    return exps


def rank_candidates(db: Session, prefs, exclude_ids=None):
    exclude_ids = set(exclude_ids or [])
    exps = candidate_experiences(db, prefs)
    ratings = rating_map(db, [e.id for e in exps])
    days = max(1, int(prefs.get("num_days") or 1))
    apd = PACE_ACTIVITIES.get(prefs.get("pace"), 3)
    per_activity_budget = None
    if prefs.get("budget"):
        per_activity_budget = float(prefs["budget"]) / max(1, days * apd)

    min_rating = float(prefs.get("min_rating") or 0)
    ranked = []
    for e in exps:
        r = ratings.get(e.id, (None, 0))[0]
        if min_rating and (r or 0) < min_rating:
            continue
        if e.id in exclude_ids:
            continue
        score, reasons, tags = score_experience(e, prefs, r, per_activity_budget)
        ranked.append({
            "exp": e,
            "cat": _cat(e),
            "score": score,
            "reason": reasons[0],
            "reasons": reasons,
            "rating": r,
            "tags": tags,
        })
    ranked.sort(key=lambda x: -x["score"])
    return ranked, ratings, per_activity_budget


# ── Itinerary generation ──────────────────────────────────────────

def generate_plan(db: Session, prefs):
    days = max(1, int(prefs.get("num_days") or 1))
    apd = PACE_ACTIVITIES.get(prefs.get("pace"), 3)
    budget = float(prefs["budget"]) if prefs.get("budget") else None

    ranked, ratings, _ = rank_candidates(db, prefs)
    warnings = []
    if not ranked:
        return [], 0.0, 0, "We couldn't find suitable experiences for your preferences. Try widening your interests, province or budget."

    needed = days * apd
    if len(ranked) < needed:
        warnings.append(
            f"Only {len(ranked)} suitable experience(s) matched your filters, so some days are lighter than requested."
        )

    used_ids = set()
    category_use = defaultdict(int)
    max_per_category = max(2, days)
    days_out = []
    total_cost = 0.0
    activity_count = 0

    def pick_next():
        # Prefer unused, category not over-represented.
        for item in ranked:
            eid = item["exp"].id
            if eid in used_ids or category_use[item["cat"]] >= max_per_category:
                continue
            if budget and used_ids and total_cost + float(item["exp"].price or 0) > budget:
                continue
            return item
        # Relax the category cap, then the budget guard.
        for item in ranked:
            if item["exp"].id not in used_ids:
                return item
        return None

    for day_no in range(1, days + 1):
        day_items = []
        cursor = 9 * 60
        lunch_done = False
        placed = 0
        guard = 0
        while placed < apd and guard < 40:
            guard += 1
            if not lunch_done and cursor >= 12 * 60:
                day_items.append(("break", "Lunch break", cursor, cursor + LUNCH_MINUTES, 0.0, 0.0,
                                  "Time to rest and try a local spot"))
                cursor += LUNCH_MINUTES + 10
                lunch_done = True

            picked = pick_next()
            if not picked:
                break
            exp = picked["exp"]
            dur_min = int(max(0.75, min(float(exp.duration_hours or DEFAULT_DURATION), 6.0)) * 60)
            start = cursor
            end = start + dur_min
            if end > CLOSE_MIN:
                used_ids.add(exp.id)
                continue
            price = float(exp.price or 0)
            total_cost += price
            activity_count += 1
            used_ids.add(exp.id)
            category_use[picked["cat"]] += 1
            day_items.append(("experience", exp.title, start, end, price, picked["score"], picked["reason"], exp))
            placed += 1
            cursor = end + TRAVEL_MIN

        days_out.append({"day_number": day_no, "items": day_items})

    if not any(items for _, items in [(d["day_number"], d["items"]) for d in days_out]):
        return [], 0.0, 0, "We couldn't build a schedule from the available experiences."

    return days_out, round(total_cost, 2), activity_count, " ".join(warnings) if warnings else None


def save_plan(db: Session, user, prefs, days_out, total_cost, activity_count, title=None, summary=None):
    itin = Itinerary(
        user_id=user.id,
        title=title or _default_title(prefs, days_out),
        province=prefs.get("province"),
        num_days=int(prefs.get("num_days") or 1),
        budget=prefs.get("budget"),
        estimated_cost=total_cost,
        pace=prefs.get("pace") or "balanced",
        interests=",".join(prefs.get("interests") or []),
        experience_type=prefs.get("experience_type"),
        min_rating=float(prefs.get("min_rating") or 0),
        budget_preference=prefs.get("budget_preference") or "mid",
        summary=summary,
    )
    db.add(itin)
    db.flush()

    for day in days_out:
        for order, entry in enumerate(day["items"]):
            kind, label, start, end, cost, score, reason = entry[:7]
            exp = entry[7] if kind == "experience" else None
            db.add(ItineraryItem(
                itinerary_id=itin.id,
                experience_id=exp.id if exp else None,
                item_type=kind,
                title=label,
                day_number=day["day_number"],
                start_time=_fmt(start),
                end_time=_fmt(end),
                sort_order=order,
                estimated_cost=cost,
                recommendation_score=score,
                reason=reason,
            ))
    db.commit()
    db.refresh(itin)
    return itin


def _default_title(prefs, days_out):
    province = prefs.get("province") or "South Africa"
    days = int(prefs.get("num_days") or 1)
    return f"{days}-day cultural journey · {province}"


def to_response(itin: Itinerary, db: Session):
    exp_ids = [i.experience_id for i in itin.items if i.experience_id]
    ratings = rating_map(db, exp_ids)
    by_day = defaultdict(list)
    for item in sorted(itin.items, key=lambda i: (i.day_number, i.sort_order)):
        exp = item.experience
        by_day[item.day_number].append({
            "id": item.id,
            "experience_id": item.experience_id,
            "day_number": item.day_number,
            "start_time": item.start_time,
            "end_time": item.end_time,
            "sort_order": item.sort_order,
            "estimated_cost": item.estimated_cost or 0,
            "recommendation_score": item.recommendation_score or 0,
            "reason": item.reason,
            "title": exp.title if exp else item.title,
            "category": _cat(exp) if exp else ("Break" if item.item_type == "break" else None),
            "description": exp.description if exp else None,
            "location": exp.location if exp else None,
            "province": exp.province if exp else None,
            "price": float(exp.price or 0) if exp else 0,
            "duration_hours": exp.duration_hours if exp else None,
            "image_url": exp.image_url if exp else None,
            "avg_rating": ratings.get(item.experience_id, (None, 0))[0] if item.experience_id else None,
        })

    days = []
    for day_no in sorted(by_day.keys()):
        items = by_day[day_no]
        days.append({
            "day_number": day_no,
            "date": None,
            "items": items,
            "estimated_cost": round(sum(i["estimated_cost"] or 0 for i in items if i["experience_id"]), 2),
        })

    budget = itin.budget
    return {
        "id": itin.id,
        "title": itin.title,
        "province": itin.province,
        "num_days": itin.num_days,
        "budget": budget,
        "estimated_cost": itin.estimated_cost or 0,
        "remaining_budget": round(budget - (itin.estimated_cost or 0), 2) if budget is not None else None,
        "pace": itin.pace,
        "interests": [c for c in (itin.interests or "").split(",") if c],
        "experience_type": itin.experience_type,
        "min_rating": itin.min_rating or 0,
        "budget_preference": itin.budget_preference,
        "summary": itin.summary,
        "activity_count": sum(1 for i in itin.items if i.experience_id),
        "created_at": itin.created_at,
        "updated_at": itin.updated_at,
        "days": days,
        "warning": None,
    }


def alternatives_for(db: Session, itin: Itinerary, item: ItineraryItem, limit=6):
    prefs = _prefs_from_itinerary(itin)
    exclude_ids = [i.experience_id for i in itin.items if i.experience_id]
    exclude_ids.append(item.experience_id)
    ranked, ratings, _ = rank_candidates(db, prefs, exclude_ids=exclude_ids)
    if not ranked:
        ranked, ratings, _ = rank_candidates(db, prefs)
    out = []
    for r in ranked:
        e = r["exp"]
        out.append({
            "experience_id": e.id,
            "title": e.title,
            "category": _cat(e),
            "location": e.location,
            "province": e.province,
            "price": float(e.price or 0),
            "duration_hours": e.duration_hours,
            "image_url": e.image_url,
            "avg_rating": ratings.get(e.id, (None, 0))[0],
            "score": r["score"],
            "reason": r["reason"],
        })
        if len(out) >= limit:
            break
    return out


def _prefs_from_itinerary(itin: Itinerary):
    return {
        "province": itin.province,
        "num_days": itin.num_days,
        "budget": itin.budget,
        "pace": itin.pace,
        "interests": [c for c in (itin.interests or "").split(",") if c],
        "experience_type": itin.experience_type,
        "min_rating": itin.min_rating or 0,
        "budget_preference": itin.budget_preference or "mid",
    }


def regenerate_day(db: Session, itin: Itinerary, day_number: int):
    """Rebuild a single day using the saved preferences, keeping other days intact."""
    prefs = _prefs_from_itinerary(itin)
    prefs["num_days"] = 1
    apd = PACE_ACTIVITIES.get(prefs.get("pace"), 3)
    keep_ids = {i.experience_id for i in itin.items if i.experience_id and i.day_number != day_number}
    ranked, _, _ = rank_candidates(db, prefs, exclude_ids=list(keep_ids))
    if not ranked:
        return []

    ordered = []
    cursor = 9 * 60
    lunch_done = False
    used = set()
    cat_use = defaultdict(int)
    budget = float(itin.budget) if itin.budget else None
    spent = sum(i.estimated_cost or 0 for i in itin.items if i.experience_id and i.day_number != day_number)
    placed = 0
    for item in ranked:
        if placed >= apd:
            break
        e = item["exp"]
        if e.id in used or cat_use[item["cat"]] >= 2:
            continue
        if budget and spent + float(e.price or 0) > budget and placed > 0:
            continue
        dur_min = int(max(0.75, min(float(e.duration_hours or DEFAULT_DURATION), 6.0)) * 60)
        if not lunch_done and cursor >= 12 * 60:
            ordered.append(("break", "Lunch break", cursor, cursor + LUNCH_MINUTES, 0.0, 0.0, "Time to rest and try a local spot"))
            cursor += LUNCH_MINUTES + 10
            lunch_done = True
        if cursor + dur_min > CLOSE_MIN:
            continue
        ordered.append(("experience", e.title, cursor, cursor + dur_min, float(e.price or 0), item["score"], item["reason"], e))
        cursor += dur_min + TRAVEL_MIN
        used.add(e.id)
        cat_use[item["cat"]] += 1
        placed += 1
    return ordered
