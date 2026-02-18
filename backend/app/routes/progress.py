from flask import Blueprint, request, jsonify
from app import db
from app.models import ExerciseResponse, Exercise, UserProgress, UserStats
from datetime import datetime

bp = Blueprint('progress', __name__, url_prefix='/api/progress')

@bp.route('/exercises/<int:user_id>/<int:exercise_id>', methods=['POST'])
def submit_exercise(user_id, exercise_id):
    """Submit an exercise response."""
    exercise = Exercise.query.get(exercise_id)

    if not exercise:
        return jsonify({'error': 'Exercise not found'}), 404

    data = request.get_json()

    if not data or 'answer' not in data:
        return jsonify({'error': 'Missing answer'}), 400

    # Check if answer is correct
    correct_answer = exercise.content.get('correct_answer') if exercise.content else None
    is_correct = data['answer'] == correct_answer

    # Calculate points
    points_earned = exercise.points_value if is_correct else 0

    # Create response record
    response = ExerciseResponse(
        exercise_id=exercise_id,
        user_id=user_id,
        answer=data['answer'],
        is_correct=is_correct,
        time_spent=data.get('time_spent', 0),
        points_earned=points_earned
    )

    db.session.add(response)

    # Update user stats
    stats = UserStats.query.filter_by(user_id=user_id).first()
    if stats:
        stats.total_points += points_earned
        stats.last_activity = datetime.utcnow()

        # Update accuracy rate
        user_responses = ExerciseResponse.query.filter_by(user_id=user_id).all()
        correct_count = sum(1 for resp in user_responses if resp.is_correct)
        total_count = len(user_responses)
        if total_count > 0:
            stats.accuracy_rate = (correct_count / total_count) * 100

    try:
        db.session.commit()
        return jsonify({
            'message': 'Response submitted',
            'response': {
                'exercise_id': exercise_id,
                'is_correct': is_correct,
                'points_earned': points_earned,
                'correct_answer': correct_answer if is_correct else None
            },
            'stats': {
                'total_points': stats.total_points,
                'accuracy_rate': stats.accuracy_rate
            } if stats else None
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_progress(user_id):
    """Get user's overall progress."""
    user_progress = UserProgress.query.filter_by(user_id=user_id).all()
    stats = UserStats.query.filter_by(user_id=user_id).first()

    if not stats:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({
        'stats': {
            'total_points': stats.total_points,
            'level': stats.level,
            'streak_days': stats.streak_days,
            'total_lessons_completed': stats.total_lessons_completed,
            'current_difficulty': stats.current_difficulty,
            'accuracy_rate': stats.accuracy_rate,
            'last_activity': stats.last_activity.isoformat() if stats.last_activity else None
        },
        'progress': [
            {
                'lesson_id': p.lesson_id,
                'lesson_title': p.lesson.title if p.lesson else None,
                'status': p.status,
                'progress_percentage': p.progress_percentage,
                'started_at': p.started_at.isoformat(),
                'completed_at': p.completed_at.isoformat() if p.completed_at else None
            }
            for p in user_progress
        ]
    }), 200

@bp.route('/lessons/<int:lesson_id>/complete/<int:user_id>', methods=['POST'])
def complete_lesson(lesson_id, user_id):
    """Mark lesson as completed and handle level progression."""
    progress = UserProgress.query.filter_by(
        user_id=user_id,
        lesson_id=lesson_id
    ).first()

    if not progress:
        return jsonify({'error': 'Progress not found'}), 404

    progress.status = 'completed'
    progress.progress_percentage = 100.0
    progress.completed_at = datetime.utcnow()

    stats = UserStats.query.filter_by(user_id=user_id).first()
    if stats:
        stats.total_lessons_completed += 1
        # Level up every 10 lessons
        stats.level = (stats.total_lessons_completed // 10) + 1

    try:
        db.session.commit()
        return jsonify({
            'message': 'Lesson completed',
            'progress': {
                'lesson_id': progress.lesson_id,
                'status': progress.status,
                'progress_percentage': progress.progress_percentage
            },
            'stats': {
                'total_lessons_completed': stats.total_lessons_completed,
                'level': stats.level
            } if stats else None
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

