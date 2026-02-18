from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app import get_db
from app.models import Achievement, User, UserStats, Reward, AchievementResponse, LeaderboardEntry, RewardResponse
from datetime import datetime
from typing import List

router = APIRouter()

@router.get("/achievements/{user_id}", response_model=dict)
async def get_user_achievements(user_id: int, db: Session = Depends(get_db)):
    """Get user's achievements."""

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    achievements = user.achievements

    achievement_responses = []
    for achievement in achievements:
        # Find the unlock time from user_achievements
        from app.models import user_achievements as user_achievements_table
        unlock_time = db.execute(
            user_achievements_table.select().where(
                (user_achievements_table.c.user_id == user_id) &
                (user_achievements_table.c.achievement_id == achievement.id)
            )
        ).first()

        unlocked_at = unlock_time[2] if unlock_time and len(unlock_time) > 2 else datetime.utcnow()

        achievement_responses.append(AchievementResponse(
            id=achievement.id,
            name=achievement.name,
            description=achievement.description,
            badge_icon=achievement.badge_icon,
            unlocked_at=unlocked_at
        ))

    return {"achievements": achievement_responses}

@router.post("/check-achievements/{user_id}", response_model=dict)
async def check_achievements(user_id: int, db: Session = Depends(get_db)):
    """Check if user has earned any new achievements."""

    stats = db.query(UserStats).filter(UserStats.user_id == user_id).first()

    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    new_achievements = []

    # Check for streaks
    if stats.streak_days >= 7:
        achievement = db.query(Achievement).filter(
            (Achievement.condition_type == 'streak') & (Achievement.condition_value == 7)
        ).first()
        if achievement:
            existing = db.query(User).filter(User.id == user_id).first()
            if existing and achievement not in existing.achievements:
                existing.achievements.append(achievement)
                new_achievements.append(achievement.name)

    # Check for points milestones
    if stats.total_points >= 100:
        achievement = db.query(Achievement).filter(
            (Achievement.condition_type == 'points') & (Achievement.condition_value == 100)
        ).first()
        if achievement:
            existing = db.query(User).filter(User.id == user_id).first()
            if existing and achievement not in existing.achievements:
                existing.achievements.append(achievement)
                new_achievements.append(achievement.name)

    # Check for lessons completed
    if stats.total_lessons_completed >= 5:
        achievement = db.query(Achievement).filter(
            (Achievement.condition_type == 'lessons_completed') & (Achievement.condition_value == 5)
        ).first()
        if achievement:
            existing = db.query(User).filter(User.id == user_id).first()
            if existing and achievement not in existing.achievements:
                existing.achievements.append(achievement)
                new_achievements.append(achievement.name)

    try:
        db.commit()
        return {
            "new_achievements": new_achievements,
            "message": f"{len(new_achievements)} new achievement(s) unlocked!" if new_achievements else "No new achievements"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/leaderboard", response_model=dict)
async def get_leaderboard(limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    """Get top users by points."""

    stats = db.query(UserStats).order_by(UserStats.total_points.desc()).limit(limit).all()

    leaderboard_entries = [
        LeaderboardEntry(
            rank=i + 1,
            user_id=stat.user_id,
            username=stat.user.username if stat.user else "Unknown",
            points=stat.total_points,
            level=stat.level,
            accuracy_rate=stat.accuracy_rate
        )
        for i, stat in enumerate(stats)
    ]

    return {"leaderboard": leaderboard_entries}

@router.get("/user/{user_id}/rewards", response_model=dict)
async def get_user_rewards(user_id: int, limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    """Get user's recent rewards."""

    rewards = db.query(Reward).filter(
        Reward.user_id == user_id
    ).order_by(Reward.created_at.desc()).limit(limit).all()

    reward_responses = [
        RewardResponse(
            id=r.id,
            reward_type=r.reward_type,
            amount=r.amount,
            reason=r.reason,
            created_at=r.created_at
        )
        for r in rewards
    ]

    return {"rewards": reward_responses}

