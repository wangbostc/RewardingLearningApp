from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import get_db
from app.models import (
    ActivityAttempt,
    ActivityAttemptSubmit,
    ActivityAttemptResult,
    ChildProfile,
    EngineLesson,
    EngineLessonCompleteRequest,
    EngineLessonCompleteResponse,
    EngineLessonProgress,
    LearningActivity,
    UserStats,
)

router = APIRouter()


def _resolve_user_id(
    db: Session, request_user_id: int | None, request_profile_id: int | None
) -> int:
    if request_user_id is not None:
        return request_user_id

    if request_profile_id is not None:
        profile = db.query(ChildProfile).filter(ChildProfile.id == request_profile_id).first()
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found.",
            )
        return profile.user_id

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Either user_id or profile_id is required.",
    )


@router.post("/activities/{activity_id}/attempt", response_model=ActivityAttemptResult)
async def submit_activity_attempt(
    activity_id: int,
    payload: ActivityAttemptSubmit,
    db: Session = Depends(get_db),
):
    activity = db.query(LearningActivity).filter(LearningActivity.id == activity_id).first()
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found",
        )

    user_id = _resolve_user_id(db, payload.user_id, payload.profile_id)

    expected_answer = None
    if isinstance(activity.activity_data, dict):
        expected_answer = activity.activity_data.get("answer")

    is_correct = expected_answer is not None and payload.answer == expected_answer
    score = activity.points if is_correct else 0

    attempt = ActivityAttempt(
        user_id=user_id,
        activity_id=activity.id,
        answer=payload.answer,
        correct=is_correct,
        score=score,
        time_spent=payload.time_spent,
    )
    db.add(attempt)

    if score > 0:
        stats = db.query(UserStats).filter(UserStats.user_id == user_id).first()
        if stats:
            stats.total_points += score

    try:
        db.commit()
    except Exception as caught_error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(caught_error),
        )

    return ActivityAttemptResult(correct=is_correct, score=score)


@router.post(
    "/engine-lessons/{lesson_id}/complete",
    response_model=EngineLessonCompleteResponse,
)
async def complete_engine_lesson(
    lesson_id: int,
    payload: EngineLessonCompleteRequest,
    db: Session = Depends(get_db),
):
    lesson = db.query(EngineLesson).filter(EngineLesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engine lesson not found",
        )

    user_id = _resolve_user_id(db, payload.user_id, payload.profile_id)

    activities = (
        db.query(LearningActivity)
        .filter(LearningActivity.lesson_id == lesson_id)
        .order_by(LearningActivity.order_index, LearningActivity.id)
        .all()
    )
    activity_ids = [activity.id for activity in activities]

    attempts_count = 0
    score_percent = 0.0
    if activity_ids:
        attempts = (
            db.query(ActivityAttempt)
            .filter(
                ActivityAttempt.user_id == user_id,
                ActivityAttempt.activity_id.in_(activity_ids),
            )
            .all()
        )
        attempts_count = len(attempts)

        best_scores = {}
        for attempt in attempts:
            current_best = best_scores.get(attempt.activity_id, 0)
            best_scores[attempt.activity_id] = max(current_best, attempt.score or 0)

        total_possible = sum(activity.points for activity in activities)
        total_scored = sum(best_scores.values())
        if total_possible > 0:
            score_percent = round((total_scored / total_possible) * 100, 2)

    completed = score_percent >= 70.0

    progress = (
        db.query(EngineLessonProgress)
        .filter(
            EngineLessonProgress.user_id == user_id,
            EngineLessonProgress.lesson_id == lesson_id,
        )
        .first()
    )
    if not progress:
        progress = EngineLessonProgress(user_id=user_id, lesson_id=lesson_id)
        db.add(progress)

    progress.completed = completed
    progress.score = score_percent
    progress.attempts = attempts_count
    progress.last_attempt_at = datetime.now(timezone.utc)

    try:
        db.commit()
    except Exception as caught_error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(caught_error),
        )

    return EngineLessonCompleteResponse(
        completed=completed,
        score=score_percent,
        unlock_threshold=70.0,
        attempts=attempts_count,
    )
