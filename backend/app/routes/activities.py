from datetime import datetime, timezone
import re
from typing import Any

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

PARTICIPATION_TYPES = {
    "speak_sentence",
    "story_listen",
    "describe_picture",
    "daily_practice",
    "reward_system",
    "adaptive_review",
}


def _normalize_text(value: str) -> str:
    lowered = value.lower().strip()
    lowered = re.sub(r"[^\w\s]", "", lowered)
    return re.sub(r"\s+", " ", lowered)


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


def _extract_child_dialogue_lines(payload_answer: Any) -> list[str]:
    if isinstance(payload_answer, list):
        return [str(item).strip() for item in payload_answer if str(item).strip()]
    if isinstance(payload_answer, dict):
        lines = payload_answer.get("lines")
        if isinstance(lines, list):
            return [str(item).strip() for item in lines if str(item).strip()]
    if isinstance(payload_answer, str) and payload_answer.strip():
        return [payload_answer.strip()]
    return []


def _is_non_empty_answer(payload_answer: Any) -> bool:
    if payload_answer is None:
        return False
    if isinstance(payload_answer, str):
        return bool(payload_answer.strip())
    if isinstance(payload_answer, (list, dict)):
        return len(payload_answer) > 0
    return True


def _score_activity_attempt(activity: LearningActivity, payload_answer: Any) -> tuple[bool, int]:
    activity_type = activity.type
    data = activity.activity_data if isinstance(activity.activity_data, dict) else {}
    max_points = activity.points

    answer = data.get("answer")

    # Backward compatibility for existing seeded content.
    if activity_type in {"audio_to_picture", "audio_to_action", "word_to_picture", "story_question"}:
        is_correct = answer is not None and payload_answer == answer
        return is_correct, max_points if is_correct else 0

    if activity_type == "phonics_build_word":
        if isinstance(answer, str) and isinstance(payload_answer, str):
            is_correct = _normalize_text(payload_answer) == _normalize_text(answer)
            return is_correct, max_points if is_correct else 0
        return False, 0

    if activity_type in {"sentence_order", "sentence_builder"}:
        if isinstance(answer, list) and isinstance(payload_answer, list):
            expected = [str(token).strip().lower() for token in answer]
            heard = [str(token).strip().lower() for token in payload_answer]
            is_correct = heard == expected
            return is_correct, max_points if is_correct else 0
        return False, 0

    if activity_type == "memory_match":
        if isinstance(answer, dict) and isinstance(payload_answer, dict):
            matched_pairs = payload_answer.get("matched_pairs")
            expected_pairs = answer.get("pairs")
            if isinstance(matched_pairs, list) and isinstance(expected_pairs, list):
                is_correct = sorted(matched_pairs) == sorted(expected_pairs)
                return is_correct, max_points if is_correct else 0
        return False, 0

    if activity_type == "listen_and_type":
        if isinstance(answer, str) and isinstance(payload_answer, str):
            is_correct = _normalize_text(payload_answer) == _normalize_text(answer)
            return is_correct, max_points if is_correct else 0
        return False, 0

    if activity_type == "role_play":
        dialogue = data.get("dialogue")
        if not isinstance(dialogue, list):
            return False, 0

        expected_lines = [
            _normalize_text(step.get("expected", ""))
            for step in dialogue
            if isinstance(step, dict) and step.get("speaker") == "child" and step.get("expected")
        ]
        actual_lines = [_normalize_text(line) for line in _extract_child_dialogue_lines(payload_answer)]

        if not expected_lines:
            completed = _is_non_empty_answer(payload_answer)
            return completed, max_points if completed else 0

        # Give proportional credit for partial dialogue completion.
        matched = 0
        for idx, expected_line in enumerate(expected_lines):
            if idx < len(actual_lines) and actual_lines[idx] == expected_line:
                matched += 1

        if matched == len(expected_lines):
            return True, max_points
        if matched > 0:
            partial_score = max(1, round((matched / len(expected_lines)) * max_points))
            return False, partial_score
        return False, 0

    if activity_type in PARTICIPATION_TYPES:
        completed = _is_non_empty_answer(payload_answer)
        if completed:
            return True, max_points
        return False, 0

    # Default strict equality for unknown future modules.
    is_correct = answer is not None and payload_answer == answer
    return is_correct, max_points if is_correct else 0


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
    is_correct, score = _score_activity_attempt(activity, payload.answer)

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
