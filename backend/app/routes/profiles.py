from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import get_db
from app.models import ChildProfile, ChildProfileCreate

router = APIRouter()


@router.get("/profiles", response_model=dict)
async def get_profiles(user_id: int = Query(...), db: Session = Depends(get_db)):
    profiles = (
        db.query(ChildProfile)
        .filter(ChildProfile.user_id == user_id)
        .order_by(ChildProfile.id)
        .all()
    )

    return {
        "profiles": [
            {
                "id": profile.id,
                "user_id": profile.user_id,
                "name": profile.name,
                "age": profile.age,
                "avatar": profile.avatar,
                "created_at": profile.created_at.isoformat() if profile.created_at else None,
            }
            for profile in profiles
        ]
    }


@router.post("/profiles", response_model=dict)
async def create_profile(payload: ChildProfileCreate, db: Session = Depends(get_db)):
    profile = ChildProfile(
        user_id=payload.user_id,
        name=payload.name,
        age=payload.age,
        avatar=payload.avatar,
    )
    db.add(profile)

    try:
        db.commit()
        db.refresh(profile)
    except Exception as caught_error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(caught_error),
        )

    return {
        "profile": {
            "id": profile.id,
            "user_id": profile.user_id,
            "name": profile.name,
            "age": profile.age,
            "avatar": profile.avatar,
            "created_at": profile.created_at.isoformat() if profile.created_at else None,
        }
    }


@router.get("/profiles/{profile_id}", response_model=dict)
async def get_profile(profile_id: int, db: Session = Depends(get_db)):
    profile = db.query(ChildProfile).filter(ChildProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    return {
        "profile": {
            "id": profile.id,
            "user_id": profile.user_id,
            "name": profile.name,
            "age": profile.age,
            "avatar": profile.avatar,
            "created_at": profile.created_at.isoformat() if profile.created_at else None,
        }
    }

