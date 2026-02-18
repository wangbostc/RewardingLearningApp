from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app import get_db
from app.models import Achievement, UserAchievement, UserStats, Reward
from datetime import datetime

router = APIRouter(prefix="/rewards", tags=["rewards"])

@router.get("/achievements/{user_id}", response_model=dict)
async def get_user_achievements(user_id: int, db: Session = Depends(get_db)):
    """Get user's achievements."""
    achievements = db.query(UserAchievement).filter(UserAchievement.user_id == user_id).all()

    return {
        'achievements': [
            {
                'id': ua.achievement_id,
                'name': ua.achievement.name if ua.achievement else 'Unknown',
                'description': ua.achievement.description if ua.achievement else '',
                'badge_icon': ua.achievement.badge_icon if ua.achievement else '',
                'unlocked_at': ua.unlocked_at.isoformat()
            }
            for ua in achievements
        ]
    }

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
            Achievement.condition_type == 'streak',
            Achievement.condition_value == 7
        ).first()
        if achievement:
            existing = db.query(UserAchievement).filter(
                UserAchievement.user_id == user_id,
                UserAchievement.achievement_id == achievement.id
            ).first()
            if not existing:
                ua = UserAchievement(user_id=user_id, achievement_id=achievement.id)
                db.add(ua)
                new_achievements.append(achievement.name)

    # Check for points milestones
    if stats.total_points >= 100:
        achievement = db.query(Achievement).filter(
            Achievement.condition_type == 'points',
            Achievement.condition_value == 100
        ).first()
        if achievement:
            existing = db.query(UserAchievement).filter(
                UserAchievement.user_id == user_id,
                UserAchievement.achievement_id == achievement.id
            ).first()
            if not existing:
                ua = UserAchievement(user_id=user_id, achievement_id=achievement.id)
                db.add(ua)
                new_achievements.append(achievement.name)

    # Check for lessons completed
    if stats.total_lessons_completed >= 5:
        achievement = db.query(Achievement).filter(
            Achievement.condition_type == 'lessons_completed',
            Achievement.condition_value == 5
        ).first()
        if achievement:
            existing = db.query(UserAchievement).filter(
                UserAchievement.user_id == user_id,
                UserAchievement.achievement_id == achievement.id
            ).first()
            if not existing:
                ua = UserAchievement(user_id=user_id, achievement_id=achievement.id)
                db.add(ua)
                new_achievements.append(achievement.name)

    try:
        db.commit()
        return {
            'new_achievements': new_achievements,
            'message': f'{len(new_achievements)} new achievement(s) unlocked!' if new_achievements else 'No new achievements'
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/leaderboard", response_model=dict)
async def get_leaderboard(limit: int = Query(10), db: Session = Depends(get_db)):
    """Get top users by points."""
    stats = db.query(UserStats).order_by(UserStats.total_points.desc()).limit(limit).all()

    return {
        'leaderboard': [
            {
                'rank': i + 1,
                'user_id': stat.user_id,
                'username': stat.user.username if stat.user else 'Unknown',
                'points': stat.total_points,
                'level': stat.level,
                'accuracy_rate': stat.accuracy_rate
            }
            for i, stat in enumerate(stats)
        ]
    }

@router.get("/user/{user_id}/rewards", response_model=dict)
async def get_user_rewards(
    user_id: int,
    limit: int = Query(20),
    db: Session = Depends(get_db)
):
    """Get user's recent rewards."""
    rewards = db.query(Reward).filter(
        Reward.user_id == user_id
    ).order_by(Reward.created_at.desc()).limit(limit).all()

    return {
        'rewards': [
            {
                'id': reward.id,
                'reward_type': reward.reward_type,
                'amount': reward.amount,
                'reason': reward.reason,
                'created_at': reward.created_at.isoformat()
            }
            for reward in rewards
        ]
    }

