import re

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from rapidfuzz import fuzz
from app import get_db
from app.models import (
    ReadingSentence,
    UserStats,
    Reward,
    SpeechCheckRequest,
    SpeechCheckResponse,
    ReadingSentenceResponse,
    UserExerciseResponse,
)

router = APIRouter()

# Minimum similarity threshold (0-100) to consider a reading "correct"
SIMILARITY_THRESHOLD = 75


def normalize_text(text: str) -> str:
    """Normalize text for comparison: lowercase, strip punctuation, collapse whitespace."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)  # Remove punctuation
    text = re.sub(r"\s+", " ", text)  # Collapse whitespace
    return text


@router.post("/check", response_model=SpeechCheckResponse)
async def check_speech(request: SpeechCheckRequest, db: Session = Depends(get_db)):
    """
    Compare a speech transcript against the expected sentence.
    Awards points if similarity >= threshold.
    """
    sentence = (
        db.query(ReadingSentence)
        .filter(ReadingSentence.id == request.sentence_id)
        .first()
    )

    if not sentence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sentence not found"
        )

    expected = normalize_text(sentence.text)
    heard = normalize_text(request.transcript)

    # Use token_sort_ratio for word-order-tolerant matching
    similarity = fuzz.token_sort_ratio(expected, heard)

    is_correct = similarity >= SIMILARITY_THRESHOLD
    points_earned = sentence.points_value if is_correct else 0

    # Update user stats if correct
    if is_correct:
        stats = db.query(UserStats).filter(UserStats.user_id == request.user_id).first()
        if stats:
            stats.total_points += points_earned

            # Create reward log entry
            reward = Reward(
                user_id=request.user_id,
                reward_type="points",
                amount=points_earned,
                reason=f'Read correctly: "{sentence.text[:50]}"',
            )
            db.add(reward)

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

    if is_correct:
        message = "Great job! You read it correctly! 🎉"
    elif similarity >= 50:
        message = "Almost there! Try reading it one more time. 💪"
    else:
        message = "Let's try again! Listen carefully to each word. 🔄"

    return SpeechCheckResponse(
        is_correct=is_correct,
        similarity=round(similarity, 1),
        points_earned=points_earned,
        expected=sentence.text,
        heard=request.transcript,
        message=message,
    )


@router.get("/sentences/{lesson_id}", response_model=dict)
async def get_lesson_sentences(lesson_id: int, db: Session = Depends(get_db)):
    """Get all reading sentences for a lesson."""
    sentences = (
        db.query(ReadingSentence)
        .filter(ReadingSentence.lesson_id == lesson_id)
        .order_by(ReadingSentence.order, ReadingSentence.id)
        .all()
    )

    return {
        "sentences": [
            {
                "id": s.id,
                "text": s.text,
                "difficulty_level": s.difficulty_level,
                "category": s.category,
                "points_value": s.points_value,
                "order": s.order,
            }
            for s in sentences
        ]
    }


@router.get("/next/{user_id}", response_model=dict)
async def get_next_sentence(user_id: int, db: Session = Depends(get_db)):
    """
    Get the next unread sentence for the user.
    Returns sentences they haven't successfully read yet.
    """
    # Get IDs of sentences the user has already read correctly
    # We store successful reads as exercise responses with is_correct=True
    completed_ids = (
        db.query(UserExerciseResponse.exercise_id)
        .filter(
            UserExerciseResponse.user_id == user_id,
            UserExerciseResponse.is_correct == True,
        )
        .all()
    )
    completed_set = {row[0] for row in completed_ids}

    # Get all sentences ordered by difficulty then order
    all_sentences = (
        db.query(ReadingSentence)
        .order_by(
            ReadingSentence.difficulty_level, ReadingSentence.order, ReadingSentence.id
        )
        .all()
    )

    # Find the first sentence not yet completed
    next_sentence = None
    total = len(all_sentences)
    completed_count = 0

    for s in all_sentences:
        if s.id in completed_set:
            completed_count += 1
        elif next_sentence is None:
            next_sentence = s

    if next_sentence is None:
        return {
            "sentence": None,
            "progress": {"completed": completed_count, "total": total},
            "message": "All sentences completed! 🎊",
        }

    return {
        "sentence": {
            "id": next_sentence.id,
            "text": next_sentence.text,
            "difficulty_level": next_sentence.difficulty_level,
            "category": next_sentence.category,
            "points_value": next_sentence.points_value,
            "lesson_id": next_sentence.lesson_id,
        },
        "progress": {"completed": completed_count, "total": total},
    }


@router.post("/record-success/{user_id}/{sentence_id}", response_model=dict)
async def record_reading_success(
    user_id: int, sentence_id: int, db: Session = Depends(get_db)
):
    """Record that a user successfully read a sentence (uses exercise_responses table)."""
    # Store as an exercise response to track completion
    response = UserExerciseResponse(
        exercise_id=sentence_id,  # Reusing this field for sentence_id tracking
        user_id=user_id,
        answer={"type": "reading", "sentence_id": sentence_id},
        is_correct=True,
        points_earned=0,  # Points already awarded in /check
    )
    db.add(response)

    try:
        db.commit()
        return {"message": "Reading success recorded"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
