from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import get_db
from app.models import (
    RewardItem,
    RewardRedemption,
    UserStats,
    RedeemRequest,
    RewardItemResponse,
    RewardRedemptionResponse,
)

router = APIRouter()


@router.get("/items", response_model=dict)
async def get_shop_items(db: Session = Depends(get_db)):
    """Get all active reward items in the shop."""
    items = (
        db.query(RewardItem)
        .filter(RewardItem.is_active == True)
        .order_by(RewardItem.points_cost)
        .all()
    )

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
            }
            for item in items
        ]
    }


@router.post("/redeem/{item_id}", response_model=dict)
async def redeem_item(
    item_id: int, request: RedeemRequest, db: Session = Depends(get_db)
):
    """Redeem a reward item using points."""
    item = db.query(RewardItem).filter(RewardItem.id == item_id).first()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Reward item not found"
        )

    if not item.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This reward is no longer available",
        )

    if item.stock is not None and item.stock <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This reward is out of stock",
        )

    # Check user has enough points
    stats = db.query(UserStats).filter(UserStats.user_id == request.user_id).first()

    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if stats.total_points < item.points_cost:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Not enough points. You have {stats.total_points} but need {item.points_cost}",
        )

    # Deduct points
    stats.total_points -= item.points_cost

    # Reduce stock if applicable
    if item.stock is not None:
        item.stock -= 1

    # Create redemption record
    redemption = RewardRedemption(
        user_id=request.user_id,
        reward_item_id=item_id,
        points_spent=item.points_cost,
        status="pending",
    )
    db.add(redemption)

    try:
        db.commit()
        db.refresh(redemption)
        return {
            "message": f"Successfully redeemed '{item.name}'! Waiting for approval. 🎁",
            "redemption": {
                "id": redemption.id,
                "reward_item_name": item.name,
                "points_spent": redemption.points_spent,
                "status": redemption.status,
                "remaining_points": stats.total_points,
            },
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/redemptions/{user_id}", response_model=dict)
async def get_user_redemptions(user_id: int, db: Session = Depends(get_db)):
    """Get all redemptions for a user."""
    redemptions = (
        db.query(RewardRedemption)
        .filter(RewardRedemption.user_id == user_id)
        .order_by(RewardRedemption.redeemed_at.desc())
        .all()
    )

    return {
        "redemptions": [
            {
                "id": r.id,
                "user_id": r.user_id,
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
