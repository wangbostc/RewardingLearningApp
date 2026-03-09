from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import get_db
from app.models import LearningPath, LearningUnit, EngineLesson, LearningActivity

router = APIRouter()


@router.get("/paths", response_model=dict)
async def get_paths(db: Session = Depends(get_db)):
    paths = db.query(LearningPath).order_by(LearningPath.order_index, LearningPath.id).all()

    return {
        "paths": [
            {
                "id": path.id,
                "name": path.name,
                "description": path.description,
                "order_index": path.order_index,
            }
            for path in paths
        ]
    }


@router.get("/paths/{path_id}/units", response_model=dict)
async def get_units_for_path(path_id: int, db: Session = Depends(get_db)):
    path = db.query(LearningPath).filter(LearningPath.id == path_id).first()
    if not path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Learning path not found"
        )

    units = (
        db.query(LearningUnit)
        .filter(LearningUnit.path_id == path_id)
        .order_by(LearningUnit.order_index, LearningUnit.id)
        .all()
    )

    return {
        "units": [
            {
                "id": unit.id,
                "path_id": unit.path_id,
                "name": unit.name,
                "order_index": unit.order_index,
            }
            for unit in units
        ]
    }


@router.get("/units/{unit_id}/lessons", response_model=dict)
async def get_lessons_for_unit(unit_id: int, db: Session = Depends(get_db)):
    unit = db.query(LearningUnit).filter(LearningUnit.id == unit_id).first()
    if not unit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Learning unit not found"
        )

    lessons = (
        db.query(EngineLesson)
        .filter(EngineLesson.unit_id == unit_id)
        .order_by(EngineLesson.order_index, EngineLesson.id)
        .all()
    )

    return {
        "lessons": [
            {
                "id": lesson.id,
                "unit_id": lesson.unit_id,
                "title": lesson.title,
                "level": lesson.level,
                "order_index": lesson.order_index,
                "estimated_minutes": lesson.estimated_minutes,
                "activity_count": len(lesson.activities),
            }
            for lesson in lessons
        ]
    }


@router.get("/engine-lessons/{lesson_id}", response_model=dict)
async def get_engine_lesson(lesson_id: int, db: Session = Depends(get_db)):
    lesson = db.query(EngineLesson).filter(EngineLesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Engine lesson not found"
        )

    activities = (
        db.query(LearningActivity)
        .filter(LearningActivity.lesson_id == lesson.id)
        .order_by(LearningActivity.order_index, LearningActivity.id)
        .all()
    )

    return {
        "lesson": {
            "id": lesson.id,
            "unit_id": lesson.unit_id,
            "title": lesson.title,
            "level": lesson.level,
            "order_index": lesson.order_index,
            "estimated_minutes": lesson.estimated_minutes,
            "activities": [
                {
                    "id": activity.id,
                    "lesson_id": activity.lesson_id,
                    "type": activity.type,
                    "prompt": activity.prompt,
                    "instructions": activity.instructions,
                    "activity_data": activity.activity_data,
                    "order_index": activity.order_index,
                    "points": activity.points,
                }
                for activity in activities
            ],
        }
    }

