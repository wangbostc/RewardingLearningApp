from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app import get_db
from app.models import UserExerciseResponse, Exercise, UserProgress, UserStats
from datetime import datetime, timezone

router = APIRouter()


class ExerciseSubmission(BaseModel):
    answer: str
    time_spent: int = 0


@router.post("/exercises/{user_id}/{exercise_id}", response_model=dict)
async def submit_exercise(
    user_id: int,
    exercise_id: int,
    submission: ExerciseSubmission,
    db: Session = Depends(get_db),
):
    """Submit an exercise response."""
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()

    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found"
        )

    # Check if answer is correct
    correct_answer = (
        exercise.content.get("correct_answer") if exercise.content else None
    )
    is_correct = submission.answer == correct_answer

    # Calculate points
    points_earned = exercise.points_value if is_correct else 0

    # Create response record
    response = UserExerciseResponse(
        exercise_id=exercise_id,
        user_id=user_id,
        answer=submission.answer,
        is_correct=is_correct,
        time_spent=submission.time_spent,
        points_earned=points_earned,
    )

    db.add(response)

    # Update user stats
    stats = db.query(UserStats).filter(UserStats.user_id == user_id).first()
    if stats:
        stats.total_points += points_earned
        stats.last_activity = datetime.now(timezone.utc)

        # Update accuracy rate
        user_responses = (
            db.query(UserExerciseResponse)
            .filter(UserExerciseResponse.user_id == user_id)
            .all()
        )
        correct_count = sum(1 for resp in user_responses if resp.is_correct)
        total_count = len(user_responses)
        if total_count > 0:
            stats.accuracy_rate = (correct_count / total_count) * 100

    try:
        db.commit()
        return {
            "message": "Response submitted",
            "response": {
                "exercise_id": exercise_id,
                "is_correct": is_correct,
                "points_earned": points_earned,
                "correct_answer": correct_answer if is_correct else None,
            },
            "stats": {
                "total_points": stats.total_points,
                "accuracy_rate": stats.accuracy_rate,
            }
            if stats
            else None,
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/user/{user_id}", response_model=dict)
async def get_user_progress(user_id: int, db: Session = Depends(get_db)):
    """Get user's overall progress."""
    user_progress = db.query(UserProgress).filter(UserProgress.user_id == user_id).all()
    stats = db.query(UserStats).filter(UserStats.user_id == user_id).first()

    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return {
        "stats": {
            "total_points": stats.total_points,
            "level": stats.level,
            "streak_days": stats.streak_days,
            "total_lessons_completed": stats.total_lessons_completed,
            "current_difficulty": stats.current_difficulty,
            "accuracy_rate": stats.accuracy_rate,
            "last_activity": stats.last_activity.isoformat()
            if stats.last_activity is not None
            else None,
        },
        "progress": [
            {
                "lesson_id": p.lesson_id,
                "lesson_title": p.lesson.title if p.lesson else None,
                "status": p.status,
                "progress_percentage": p.progress_percentage,
                "started_at": p.started_at.isoformat() if p.started_at else None,
                "completed_at": p.completed_at.isoformat()
                if p.completed_at is not None
                else None,
            }
            for p in user_progress
        ],
    }


@router.post("/lessons/{lesson_id}/complete/{user_id}", response_model=dict)
async def complete_lesson(lesson_id: int, user_id: int, db: Session = Depends(get_db)):
    """Mark lesson as completed and handle level progression."""
    progress = (
        db.query(UserProgress)
        .filter(UserProgress.user_id == user_id, UserProgress.lesson_id == lesson_id)
        .first()
    )

    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Progress not found"
        )

    progress.status = "completed"
    progress.progress_percentage = 100.0
    progress.completed_at = datetime.now(timezone.utc)

    stats = db.query(UserStats).filter(UserStats.user_id == user_id).first()
    if stats:
        stats.total_lessons_completed += 1
        # Level up every 10 lessons
        stats.level = (stats.total_lessons_completed // 10) + 1

    try:
        db.commit()
        db.refresh(progress)
        return {
            "message": "Lesson completed",
            "progress": {
                "lesson_id": progress.lesson_id,
                "status": progress.status,
                "progress_percentage": progress.progress_percentage,
            },
            "stats": {
                "total_lessons_completed": stats.total_lessons_completed,
                "level": stats.level,
            }
            if stats
            else None,
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
