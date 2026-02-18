from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app import get_db
from app.models import (
    Lesson, Exercise, UserProgress, ExerciseResponse, UserStats,
    LessonResponse, ExerciseDetailResponse, UserProgressResponse
)
from datetime import datetime

router = APIRouter(prefix="/lessons", tags=["lessons"])

@router.get("/", response_model=dict)
async def get_lessons(
    difficulty: str = Query(None),
    category: str = Query(None),
    db: Session = Depends(get_db)
):
    """Get all lessons, optionally filtered by difficulty."""
    query = db.query(Lesson)

    if difficulty:
        query = query.filter(Lesson.difficulty == difficulty)
    if category:
        query = query.filter(Lesson.category == category)

    lessons = query.all()

    return {
        'lessons': [
            {
                'id': lesson.id,
                'title': lesson.title,
                'description': lesson.description,
                'difficulty': lesson.difficulty,
                'category': lesson.category,
                'estimated_duration': lesson.estimated_duration,
                'exercise_count': len(lesson.exercises)
            }
            for lesson in lessons
        ]
    }

@router.get("/{lesson_id}", response_model=dict)
async def get_lesson(lesson_id: int, db: Session = Depends(get_db)):
    """Get lesson details with exercises."""
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()

    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )

    exercises = sorted(lesson.exercises, key=lambda x: x.order or x.id)

    return {
        'lesson': {
            'id': lesson.id,
            'title': lesson.title,
            'description': lesson.description,
            'difficulty': lesson.difficulty,
            'category': lesson.category,
            'estimated_duration': lesson.estimated_duration
        },
        'exercises': [
            {
                'id': exercise.id,
                'type': exercise.type,
                'question': exercise.question,
                'content': exercise.content,
                'points_value': exercise.points_value,
                'order': exercise.order
            }
            for exercise in exercises
        ]
    }

@router.get("/{user_id}/progress/{lesson_id}", response_model=dict)
async def get_lesson_progress(
    user_id: int,
    lesson_id: int,
    db: Session = Depends(get_db)
):
    """Get user's progress on a specific lesson."""
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == user_id,
        UserProgress.lesson_id == lesson_id
    ).first()

    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Progress not found"
        )

    return {
        'progress': {
            'lesson_id': progress.lesson_id,
            'status': progress.status,
            'progress_percentage': progress.progress_percentage,
            'started_at': progress.started_at.isoformat(),
            'completed_at': progress.completed_at.isoformat() if progress.completed_at else None
        }
    }

@router.post("/{user_id}/start/{lesson_id}", response_model=dict)
async def start_lesson(
    user_id: int,
    lesson_id: int,
    db: Session = Depends(get_db)
):
    """Start a lesson for a user."""
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()

    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )

    # Check if progress already exists
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == user_id,
        UserProgress.lesson_id == lesson_id
    ).first()

    if not progress:
        progress = UserProgress(
            user_id=user_id,
            lesson_id=lesson_id,
            status='in_progress'
        )
        db.add(progress)
    else:
        progress.status = 'in_progress'
        progress.started_at = datetime.utcnow()

    try:
        db.commit()
        db.refresh(progress)
        return {
            'message': 'Lesson started',
            'progress': {
                'lesson_id': progress.lesson_id,
                'status': progress.status,
                'progress_percentage': progress.progress_percentage
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

