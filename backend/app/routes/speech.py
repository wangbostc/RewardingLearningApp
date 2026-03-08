import re
from difflib import SequenceMatcher

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
    UserExerciseResponse,
)

router = APIRouter()

WORD_TOKEN_RE = re.compile(r"[A-Za-z0-9']+")
DISPLAY_TOKEN_RE = re.compile(r"[A-Za-z0-9']+|[^\w\s]")


def normalize_text(text: str) -> str:
    """Normalize text for comparison: lowercase, strip punctuation, collapse whitespace."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)  # Remove punctuation
    text = re.sub(r"\s+", " ", text)  # Collapse whitespace
    return text


def is_word_token(token: str) -> bool:
    return bool(WORD_TOKEN_RE.fullmatch(token))


def tokenize_for_display(text: str) -> list[str]:
    return DISPLAY_TOKEN_RE.findall(text)


def extract_word_tokens(text: str) -> list[str]:
    return [token for token in tokenize_for_display(text) if is_word_token(token)]


def normalize_word_tokens(text: str) -> list[str]:
    return [normalize_text(token) for token in extract_word_tokens(text)]


def is_exact_reading_match(expected_text: str, heard_text: str) -> bool:
    return normalize_word_tokens(expected_text) == normalize_word_tokens(heard_text)


def calculate_reading_similarity(expected_text: str, heard_text: str) -> float:
    expected = normalize_text(expected_text)
    heard = normalize_text(heard_text)

    if not expected and not heard:
        return 100.0
    if not expected or not heard:
        return 0.0

    return float(fuzz.ratio(expected, heard))


def build_display_feedback(display_tokens: list[str], word_statuses: list[str]) -> list[dict]:
    feedback = []
    word_index = 0

    for token in display_tokens:
        if is_word_token(token):
            feedback.append({"text": token, "status": word_statuses[word_index]})
            word_index += 1
        else:
            feedback.append({"text": token, "status": "neutral"})

    return feedback


def compare_word_feedback(expected_text: str, heard_text: str) -> tuple[list[dict], list[dict]]:
    """Return display token feedback for expected and heard text."""
    expected_display = tokenize_for_display(expected_text)
    heard_display = tokenize_for_display(heard_text)
    expected_words = [token for token in expected_display if is_word_token(token)]
    heard_words = [token for token in heard_display if is_word_token(token)]

    expected_statuses = ["wrong"] * len(expected_words)
    heard_statuses = ["wrong"] * len(heard_words)

    matcher = SequenceMatcher(
        a=[normalize_text(word) for word in expected_words],
        b=[normalize_text(word) for word in heard_words],
        autojunk=False,
    )

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            for index in range(i1, i2):
                expected_statuses[index] = "correct"
            for index in range(j1, j2):
                heard_statuses[index] = "correct"
        elif tag == "delete":
            for index in range(i1, i2):
                expected_statuses[index] = "missing"
        elif tag == "insert":
            for index in range(j1, j2):
                heard_statuses[index] = "extra"
        elif tag == "replace":
            for index in range(i1, i2):
                expected_statuses[index] = "wrong"
            for index in range(j1, j2):
                heard_statuses[index] = "wrong"

    return (
        build_display_feedback(expected_display, expected_statuses),
        build_display_feedback(heard_display, heard_statuses),
    )


def get_completed_sentence_ids(user_id: int, db: Session) -> set[int]:
    responses = (
        db.query(UserExerciseResponse)
        .filter(
            UserExerciseResponse.user_id == user_id,
            UserExerciseResponse.is_correct == True,
        )
        .all()
    )

    completed_ids: set[int] = set()
    for response in responses:
        if isinstance(response.answer, dict) and response.answer.get("type") == "reading":
            sentence_id = response.answer.get("sentence_id")
            if isinstance(sentence_id, int):
                completed_ids.add(sentence_id)
        elif response.exercise_id is not None:
            completed_ids.add(response.exercise_id)

    return completed_ids


@router.post("/check", response_model=SpeechCheckResponse)
async def check_speech(request: SpeechCheckRequest, db: Session = Depends(get_db)):
    """
    Compare a speech transcript against the expected sentence.
    Awards points only when the normalized words match exactly.
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

    expected_tokens, heard_tokens = compare_word_feedback(sentence.text, request.transcript)
    similarity = calculate_reading_similarity(sentence.text, request.transcript)
    is_correct = is_exact_reading_match(sentence.text, request.transcript)
    existing_success = (
        db.query(UserExerciseResponse)
        .filter(
            UserExerciseResponse.user_id == request.user_id,
            UserExerciseResponse.exercise_id == request.sentence_id,
            UserExerciseResponse.is_correct == True,
        )
        .first()
    )
    points_earned = sentence.points_value if is_correct and not existing_success else 0

    # Update user stats only once per sentence
    if points_earned > 0:
        stats = db.query(UserStats).filter(UserStats.user_id == request.user_id).first()
        if stats:
            stats.total_points += points_earned

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

    if is_correct and existing_success:
        message = "You got it right again! Let's move to the next sentence. ✨"
    elif is_correct:
        message = "Great job! You read every word correctly! 🎉"
    elif similarity >= 50:
        message = "Almost there! Fix the highlighted word and try again. 💪"
    else:
        message = "Let's try again! The highlighted word shows what to fix. 🔄"

    return SpeechCheckResponse(
        is_correct=is_correct,
        similarity=round(similarity, 1),
        points_earned=points_earned,
        expected=sentence.text,
        heard=request.transcript,
        message=message,
        expected_tokens=expected_tokens,
        heard_tokens=heard_tokens,
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
    completed_set = get_completed_sentence_ids(user_id, db)

    all_sentences = (
        db.query(ReadingSentence)
        .order_by(
            ReadingSentence.difficulty_level, ReadingSentence.order, ReadingSentence.id
        )
        .all()
    )

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
    existing = (
        db.query(UserExerciseResponse)
        .filter(
            UserExerciseResponse.user_id == user_id,
            UserExerciseResponse.exercise_id == sentence_id,
            UserExerciseResponse.is_correct == True,
        )
        .first()
    )
    if existing:
        return {"message": "Reading success already recorded"}

    response = UserExerciseResponse(
        exercise_id=sentence_id,
        user_id=user_id,
        answer={"type": "reading", "sentence_id": sentence_id},
        is_correct=True,
        points_earned=0,
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
