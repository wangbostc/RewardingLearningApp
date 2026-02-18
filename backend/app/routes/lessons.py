from flask import Blueprint, request, jsonify
from app import db
from app.models import Lesson, Exercise, UserProgress, ExerciseResponse, UserStats
from datetime import datetime

bp = Blueprint('lessons', __name__, url_prefix='/api/lessons')

@bp.route('', methods=['GET'])
def get_lessons():
    """Get all lessons, optionally filtered by difficulty."""
    difficulty = request.args.get('difficulty')
    category = request.args.get('category')

    query = Lesson.query

    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    if category:
        query = query.filter_by(category=category)

    lessons = query.all()

    return jsonify({
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
    }), 200

@bp.route('/<int:lesson_id>', methods=['GET'])
def get_lesson(lesson_id):
    """Get lesson details with exercises."""
    lesson = Lesson.query.get(lesson_id)

    if not lesson:
        return jsonify({'error': 'Lesson not found'}), 404

    exercises = sorted(lesson.exercises, key=lambda x: x.order or x.id)

    return jsonify({
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
    }), 200

@bp.route('/<int:user_id>/progress/<int:lesson_id>', methods=['GET'])
def get_lesson_progress(user_id, lesson_id):
    """Get user's progress on a specific lesson."""
    progress = UserProgress.query.filter_by(
        user_id=user_id,
        lesson_id=lesson_id
    ).first()

    if not progress:
        return jsonify({'error': 'Progress not found'}), 404

    return jsonify({
        'progress': {
            'lesson_id': progress.lesson_id,
            'status': progress.status,
            'progress_percentage': progress.progress_percentage,
            'started_at': progress.started_at.isoformat(),
            'completed_at': progress.completed_at.isoformat() if progress.completed_at else None
        }
    }), 200

@bp.route('/<int:user_id>/start/<int:lesson_id>', methods=['POST'])
def start_lesson(user_id, lesson_id):
    """Start a lesson for a user."""
    lesson = Lesson.query.get(lesson_id)

    if not lesson:
        return jsonify({'error': 'Lesson not found'}), 404

    # Check if progress already exists
    progress = UserProgress.query.filter_by(
        user_id=user_id,
        lesson_id=lesson_id
    ).first()

    if not progress:
        progress = UserProgress(
            user_id=user_id,
            lesson_id=lesson_id,
            status='in_progress'
        )
        db.session.add(progress)
    else:
        progress.status = 'in_progress'
        progress.started_at = datetime.utcnow()

    try:
        db.session.commit()
        return jsonify({
            'message': 'Lesson started',
            'progress': {
                'lesson_id': progress.lesson_id,
                'status': progress.status,
                'progress_percentage': progress.progress_percentage
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

