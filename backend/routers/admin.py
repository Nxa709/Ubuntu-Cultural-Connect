from datetime import datetime, timezone #Time Zone stored in UTC Format so it will become less confusing

#Import the dependency injection , it is like the fastAPi delivery service
#HTTP normally an error crashes in python
from fastapi import APIRouter, Depends, HTTPException, status #Imports 3 functions from FastAPI

#Assession is your conversaytion with the database
from sqlalchemy.orm import Session #This is the ORM(Object Relational Mapper)

from database import get_db #Import the function that creates the database session

#Import the user database table and the user role enumeration
#This all imports the models or the tables from the database
from models.user import User, UserRole
from models.experience import Experience, Rating, TripDay, ItineraryAdd
from models.notification import Notification

#Function allows sql aggregate functions such as sum, avg, count, max, min and sum
from sqlalchemy import func

#This are like contracts that define what the Client Sends and what the API returns 
from schemas.admin import CommentResponse, HotspotResponse, HotspotRejectRequest, AdminActionResponse, AdminStatsResponse, UserResponse, UserRoleUpdate, UserActionResponse

#This is authentication
#Every Token contains the JWT token: What is the JWT Token?
from routers.auth import get_current_user

#This creates the router , now every endpoint automatically starts with 
#/api/admin , tags for Swagger/OpenAPI documentation
router = APIRouter(prefix="/api/admin", tags=["admin"])

# This is like the bouncer at the admin
#Before creating any admin endpoint we create the authorization or security
def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


# -- Comments (Ratings with comments) --
#Response model , tells fastAPI exactly what the endpoint should return
@router.get("/comments", response_model=list[CommentResponse])
def list_comments(
    status_filter: str = "pending", #This is the query parameter with the default status filter which is "pending"
    db: Session = Depends(get_db), #Communicating with the database
    current_user: User = Depends(require_admin), #Checks if the user is the admin
):
    #This creates the query object
    #This selects all from the rating where the comment is not null
    #Only rating that actually contain comments are considered , The admin only reviews comments and not every rating
    q = db.query(Rating).filter(Rating.comment.isnot(None), Rating.comment != "")


    if status_filter == "pending":
        q = q.filter(Rating.is_approved == False, Rating.rejected_at == None) #The comment has never been reviewed
    elif status_filter == "approved":
        q = q.filter(Rating.is_approved == True, Rating.rejected_at == None) #The comment has beeen approved
    elif status_filter == "rejected":
        q = q.filter(Rating.rejected_at.isnot(None)) #Rejected
    elif status_filter == "all":
        pass
    else:
        raise HTTPException(status_code=400, detail="Invalid status_filter. Use: pending, approved, rejected, all")

    #Tells SQL Alchemy that execute the query and return every matching row
    #The newest comments appear first
    ratings = q.order_by(Rating.created_at.desc()).all()

    #This is called the list comprehension
    #Instead of return raw database models , the developer creates a CommentResponse object for each rating
    return [
        CommentResponse(
            id=r.id,
            user_id=r.user_id,
            user_name=r.user.full_name if r.user else None, #Prevent the run time error by handling the case if r.user is None
            experience_id=r.experience_id,
            experience_title=r.experience.title if r.experience else None,
            score=r.score,
            comment=r.comment,
            is_approved=r.is_approved,
            rejected_at=r.rejected_at,
            created_at=r.created_at,
        )
        for r in ratings
    ]

#Something to approve in the above function
#I would need to import Python's Enum class first (from enum import Enum)
#Replace the string values "pending","approved","rejected","all" with an Enum
#class CommentStatus(str,Enum):
    #pending = "pending"
    #approved =  "approved"
    #rejected = "rejected"
    #all = "all"

#This will count the pending comments
#This endpoint will return only one value
@router.get("/comments/pending/count")

#This again acts as a bouncer at the door 
#Since the number of comments is an administrative information
#Every Admin endpoint is protected in the same way
def pending_comments_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    count = db.query(Rating).filter(
        Rating.comment.isnot(None),
        Rating.comment != "",
        Rating.is_approved == False,
        Rating.rejected_at == None,
    ).count()
    return {"count": count} #returns a json object
    #example of designing an API with the future changes in mind

#Possible improvements of the above is to use the response schema


@router.put("/comments/{comment_id}/approve", response_model=AdminActionResponse)
def approve_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    rating = db.query(Rating).filter(Rating.id == comment_id).first()
    if not rating:
        raise HTTPException(status_code=404, detail="Comment not found")

    rating.is_approved = True
    rating.rejected_at = None
    db.commit()

    return AdminActionResponse(
        message="Comment approved successfully",
        id=rating.id,
        is_approved=True,
    )


@router.put("/comments/{comment_id}/reject", response_model=AdminActionResponse) #This is the fastAPI decorator
def reject_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    rating = db.query(Rating).filter(Rating.id == comment_id).first()
    if not rating:
        raise HTTPException(status_code=404, detail="Comment not found")

    rating.is_approved = False
    rating.rejected_at = datetime.now(timezone.utc)
    db.commit()

    return AdminActionResponse(
        message="Comment rejected and removed from display",
        id=rating.id,
        is_approved=False,
    )


# -- Hotspots (Experiences) --

@router.get("/hotspots", response_model=list[HotspotResponse])
def list_hotspots(
    status_filter: str = "pending",
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    if status_filter == "pending":
        q = db.query(Experience).filter(Experience.is_approved == False, Experience.rejected_at == None)
    elif status_filter == "approved":
        q = db.query(Experience).filter(Experience.is_approved == True)
    elif status_filter == "rejected":
        q = db.query(Experience).filter(Experience.rejected_at.isnot(None))
    elif status_filter == "all":
        q = db.query(Experience)
    else:
        raise HTTPException(status_code=400, detail="Invalid status_filter. Use: pending, approved, rejected, all")

    experiences = q.order_by(Experience.created_at.desc()).all()

    return [
        HotspotResponse(
            id=e.id,
            title=e.title,
            description=e.description,
            category=e.category.value if hasattr(e.category, "value") else e.category,
            location=e.location,
            province=e.province,
            owner_id=e.owner_id,
            owner_name=e.owner.full_name if e.owner else None,
            owner_email=e.owner.email if e.owner else None,
            owner_phone=e.owner.phone_number if e.owner else None,
            image_url=e.image_url,
            price=e.price,
            duration_hours=e.duration_hours,
            max_participants=e.max_participants,
            is_active=e.is_active,
            is_approved=e.is_approved,
            rejection_reason=e.rejection_reason,
            rejected_at=e.rejected_at,
            rating_count=len(e.ratings) if e.ratings else 0,
            avg_rating=round(float(db.query(func.avg(Rating.score)).filter(Rating.experience_id == e.id, Rating.is_approved == True).scalar() or 0), 1),
            itinerary_adds=db.query(func.count(TripDay.id)).filter(TripDay.experience_id == e.id).scalar() or 0,
            created_at=e.created_at,
        )
        for e in experiences
    ]


@router.get("/hotspots/pending/count")
def pending_hotspots_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    count = db.query(Experience).filter(Experience.is_approved == False, Experience.rejected_at == None).count()
    return {"count": count}


@router.put("/hotspots/{hotspot_id}/approve", response_model=AdminActionResponse)
def approve_hotspot(
    hotspot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    exp = db.query(Experience).filter(Experience.id == hotspot_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Hotspot not found")

    if not exp.title or not exp.description:
        raise HTTPException(status_code=400, detail="Hotspot must have a name and description")

    exp.is_approved = True
    exp.is_active = True
    exp.rejection_reason = None
    exp.rejected_at = None
    db.commit()

    return AdminActionResponse(
        message="Hotspot approved successfully",
        id=exp.id,
        is_approved=True,
    )


@router.put("/hotspots/{hotspot_id}/reject", response_model=AdminActionResponse)
def reject_hotspot(
    hotspot_id: int,
    data: HotspotRejectRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    exp = db.query(Experience).filter(Experience.id == hotspot_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Hotspot not found")

    reason = (data.reason or "").strip()
    if not reason:
        raise HTTPException(status_code=400, detail="A rejection reason is required")

    exp.is_approved = False
    exp.is_active = False
    exp.rejected_at = datetime.now(timezone.utc)
    exp.rejection_reason = reason
    db.commit()

    if exp.owner_id:
        notif = Notification(
            user_id=exp.owner_id,
            type="hotspot_rejected",
            message=f"The business '{exp.title}' has been rejected.\n\nReason: {reason}\n\nClick to view the hotspot, see why it was rejected, and submit an appeal.",
            experience_id=exp.id,
        )
        db.add(notif)
        db.commit()

    return AdminActionResponse(
        message="Hotspot rejected and the owner has been notified",
        id=exp.id,
        is_approved=False,
    )


# -- Admin Dashboard Stats --

@router.get("/stats", response_model=AdminStatsResponse)
def get_admin_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    from models.experience import Experience, Rating, Trip, TripDay
    from models.user import UserRole

    total_users = db.query(User).count()
    total_tourists = db.query(User).filter(User.role == UserRole.tourist).count()
    total_hosts = db.query(User).filter(User.role == UserRole.business_owner).count()
    total_admins = db.query(User).filter(User.role == UserRole.admin).count()
    total_experiences = db.query(Experience).count()
    approved_experiences = db.query(Experience).filter(Experience.is_approved == True).count()
    pending_experiences = db.query(Experience).filter(Experience.is_approved == False).count()
    total_ratings = db.query(Rating).count()
    pending_comments = db.query(Rating).filter(
        Rating.comment.isnot(None), Rating.comment != "",
        Rating.is_approved == False, Rating.rejected_at == None,
    ).count()
    total_trips = db.query(Trip).count()

    return AdminStatsResponse(
        total_users=total_users,
        total_tourists=total_tourists,
        total_hosts=total_hosts,
        total_admins=total_admins,
        total_experiences=total_experiences,
        approved_experiences=approved_experiences,
        pending_experiences=pending_experiences,
        total_ratings=total_ratings,
        pending_comments=pending_comments,
        total_trips=total_trips,
    )


# -- User Management --

@router.get("/users", response_model=list[UserResponse])
def list_users(
    role_filter: str = "all",
    search: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    q = db.query(User)

    if role_filter == "tourist":
        q = q.filter(User.role == UserRole.tourist)
    elif role_filter == "business_owner":
        q = q.filter(User.role == UserRole.business_owner)
    elif role_filter == "admin":
        q = q.filter(User.role == UserRole.admin)
    elif role_filter != "all":
        raise HTTPException(status_code=400, detail="Invalid role_filter. Use: all, tourist, business_owner, admin")

    if search:
        search_pattern = f"%{search}%"
        q = q.filter(
            (User.full_name.ilike(search_pattern)) |
            (User.email.ilike(search_pattern))
        )

    users = q.order_by(User.created_at.desc()).all()

    return [
        UserResponse(
            id=u.id,
            email=u.email,
            full_name=u.full_name,
            phone_number=u.phone_number,
            role=u.role.value if hasattr(u.role, "value") else u.role,
            is_active=u.is_active,
            created_at=u.created_at,
        )
        for u in users
    ]


@router.put("/users/{user_id}/role", response_model=UserActionResponse)
def change_user_role(
    user_id: int,
    data: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot change your own role")

    if data.role not in ["tourist", "business_owner", "admin"]:
        raise HTTPException(status_code=400, detail="Invalid role. Use: tourist, business_owner, admin")

    user.role = UserRole(data.role)
    db.commit()

    return UserActionResponse(
        message=f"User role changed to {data.role}",
        id=user.id,
    )


@router.put("/users/{user_id}/toggle-active", response_model=UserActionResponse)
def toggle_user_active(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot deactivate your own account")

    user.is_active = not user.is_active
    db.commit()

    status_text = "activated" if user.is_active else "deactivated"
    return UserActionResponse(
        message=f"User account {status_text}",
        id=user.id,
    )


@router.delete("/users/{user_id}", response_model=UserActionResponse)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")

    db.delete(user)
    db.commit()

    return UserActionResponse(
        message="User deleted successfully",
        id=user_id,
    )
