from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import get_db
from app.models import (
    User,
    RewardItem,
    RewardRedemption,
    ReadingSentence,
    Lesson,
    UserStats,
    RewardItemCreate,
    RewardItemUpdate,
    ReadingSentenceCreate,
    RedemptionStatusUpdate,
)

router = APIRouter()


# ==================== Reward Item Management ====================


@router.get("/shop/items", response_model=dict)
async def admin_list_items(db: Session = Depends(get_db)):
    """List all reward items (including inactive)."""
    items = db.query(RewardItem).order_by(RewardItem.id).all()

    return {
        "items": [
            {
                "id": item.id,
                "name": item.name,
                "description": item.description,
                "image_url": item.image_url,
                "emoji": item.emoji,
                "points_cost": item.points_cost,
                "stock": item.stock,
                "is_active": item.is_active,
                "created_at": item.created_at.isoformat(),
            }
            for item in items
        ]
    }


@router.post("/shop/items", response_model=dict, status_code=status.HTTP_201_CREATED)
async def admin_create_item(item_data: RewardItemCreate, db: Session = Depends(get_db)):
    """Create a new reward item."""
    item = RewardItem(
        name=item_data.name,
        description=item_data.description,
        image_url=item_data.image_url,
        emoji=item_data.emoji,
        points_cost=item_data.points_cost,
        stock=item_data.stock,
        is_active=item_data.is_active,
    )
    db.add(item)

    try:
        db.commit()
        db.refresh(item)
        return {
            "message": f"Reward item '{item.name}' created",
            "item": {
                "id": item.id,
                "name": item.name,
                "points_cost": item.points_cost,
                "emoji": item.emoji,
            },
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.put("/shop/items/{item_id}", response_model=dict)
async def admin_update_item(
    item_id: int, item_data: RewardItemUpdate, db: Session = Depends(get_db)
):
    """Update a reward item."""
    item = db.query(RewardItem).filter(RewardItem.id == item_id).first()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Reward item not found"
        )

    update_data = item_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)

    try:
        db.commit()
        db.refresh(item)
        return {"message": f"Reward item '{item.name}' updated"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.delete("/shop/items/{item_id}", response_model=dict)
async def admin_delete_item(item_id: int, db: Session = Depends(get_db)):
    """Delete a reward item."""
    item = db.query(RewardItem).filter(RewardItem.id == item_id).first()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Reward item not found"
        )

    db.delete(item)

    try:
        db.commit()
        return {"message": f"Reward item '{item.name}' deleted"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


# ==================== Redemption Management ====================


@router.get("/redemptions", response_model=dict)
async def admin_list_redemptions(
    status_filter: str = None, db: Session = Depends(get_db)
):
    """List all redemptions, optionally filtered by status."""
    query = db.query(RewardRedemption).order_by(RewardRedemption.redeemed_at.desc())

    if status_filter:
        query = query.filter(RewardRedemption.status == status_filter)

    redemptions = query.all()

    return {
        "redemptions": [
            {
                "id": r.id,
                "user_id": r.user_id,
                "username": r.user.username if r.user else "Unknown",
                "reward_item_id": r.reward_item_id,
                "reward_item_name": r.reward_item.name if r.reward_item else "Unknown",
                "reward_item_emoji": r.reward_item.emoji if r.reward_item else None,
                "points_spent": r.points_spent,
                "status": r.status,
                "redeemed_at": r.redeemed_at.isoformat(),
            }
            for r in redemptions
        ]
    }


@router.put("/redemptions/{redemption_id}", response_model=dict)
async def admin_update_redemption(
    redemption_id: int,
    update: RedemptionStatusUpdate,
    db: Session = Depends(get_db),
):
    """Update the status of a redemption (approve, fulfill, reject)."""
    redemption = (
        db.query(RewardRedemption).filter(RewardRedemption.id == redemption_id).first()
    )

    if not redemption:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Redemption not found"
        )

    valid_statuses = {"pending", "approved", "fulfilled", "rejected"}
    if update.status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {valid_statuses}",
        )

    # If rejecting, refund points
    if update.status == "rejected" and redemption.status != "rejected":
        stats = (
            db.query(UserStats).filter(UserStats.user_id == redemption.user_id).first()
        )
        if stats:
            stats.total_points += redemption.points_spent

        # Restore stock
        item = (
            db.query(RewardItem)
            .filter(RewardItem.id == redemption.reward_item_id)
            .first()
        )
        if item and item.stock is not None:
            item.stock += 1

    redemption.status = update.status

    try:
        db.commit()
        return {
            "message": f"Redemption {redemption_id} status updated to '{update.status}'"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


# ==================== Reading Sentence Management ====================


@router.get("/sentences", response_model=dict)
async def admin_list_sentences(db: Session = Depends(get_db)):
    """List all reading sentences."""
    sentences = (
        db.query(ReadingSentence)
        .order_by(
            ReadingSentence.difficulty_level, ReadingSentence.order, ReadingSentence.id
        )
        .all()
    )

    return {
        "sentences": [
            {
                "id": s.id,
                "lesson_id": s.lesson_id,
                "lesson_title": s.lesson.title if s.lesson else None,
                "text": s.text,
                "difficulty_level": s.difficulty_level,
                "category": s.category,
                "points_value": s.points_value,
                "order": s.order,
            }
            for s in sentences
        ]
    }


@router.post("/sentences", response_model=dict, status_code=status.HTTP_201_CREATED)
async def admin_create_sentence(
    data: ReadingSentenceCreate, db: Session = Depends(get_db)
):
    """Create a new reading sentence."""
    lesson = db.query(Lesson).filter(Lesson.id == data.lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found"
        )

    sentence = ReadingSentence(
        lesson_id=data.lesson_id,
        text=data.text,
        difficulty_level=data.difficulty_level,
        category=data.category,
        points_value=data.points_value,
        order=data.order,
    )
    db.add(sentence)

    try:
        db.commit()
        db.refresh(sentence)
        return {
            "message": "Sentence created",
            "sentence": {
                "id": sentence.id,
                "text": sentence.text,
                "lesson_id": sentence.lesson_id,
            },
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.put("/sentences/{sentence_id}", response_model=dict)
async def admin_update_sentence(
    sentence_id: int, data: ReadingSentenceCreate, db: Session = Depends(get_db)
):
    """Update a reading sentence."""
    sentence = (
        db.query(ReadingSentence).filter(ReadingSentence.id == sentence_id).first()
    )

    if not sentence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sentence not found"
        )

    sentence.lesson_id = data.lesson_id
    sentence.text = data.text
    sentence.difficulty_level = data.difficulty_level
    sentence.category = data.category
    sentence.points_value = data.points_value
    sentence.order = data.order

    try:
        db.commit()
        return {"message": f"Sentence {sentence_id} updated"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.delete("/sentences/{sentence_id}", response_model=dict)
async def admin_delete_sentence(sentence_id: int, db: Session = Depends(get_db)):
    """Delete a reading sentence."""
    sentence = (
        db.query(ReadingSentence).filter(ReadingSentence.id == sentence_id).first()
    )

    if not sentence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sentence not found"
        )

    db.delete(sentence)

    try:
        db.commit()
        return {"message": f"Sentence {sentence_id} deleted"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


# ==================== User Management ====================


@router.get("/users", response_model=dict)
async def admin_list_users(db: Session = Depends(get_db)):
    """List all users with their stats."""
    users = db.query(User).order_by(User.id).all()

    return {
        "users": [
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "is_admin": u.is_admin,
                "total_points": u.stats.total_points if u.stats else 0,
                "level": u.stats.level if u.stats else 1,
                "created_at": u.created_at.isoformat(),
            }
            for u in users
        ]
    }
