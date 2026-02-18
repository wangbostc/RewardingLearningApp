from flask import Blueprint, request, jsonify
from app import db
from app.models import User, UserStats
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    data = request.get_json()

    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing required fields'}), 400

    # Check if user already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 409

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 409

    # Create new user
    user = User(
        username=data['username'],
        email=data['email'],
        password_hash=generate_password_hash(data['password']),
        age=data.get('age'),
        native_language=data.get('native_language', 'unknown')
    )

    db.session.add(user)
    db.session.flush()  # Flush to get the user ID

    # Create user stats
    stats = UserStats(user_id=user.id)
    db.session.add(stats)

    try:
        db.session.commit()
        return jsonify({
            'message': 'User created successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'age': user.age
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/login', methods=['POST'])
def login():
    """Login user."""
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Missing username or password'}), 400

    user = User.query.filter_by(username=data['username']).first()

    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'error': 'Invalid username or password'}), 401

    return jsonify({
        'message': 'Login successful',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'age': user.age
        }
    }), 200

@bp.route('/profile/<int:user_id>', methods=['GET'])
def get_profile(user_id):
    """Get user profile."""
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    stats = UserStats.query.filter_by(user_id=user_id).first()

    return jsonify({
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'age': user.age,
            'native_language': user.native_language,
            'created_at': user.created_at.isoformat()
        },
        'stats': {
            'total_points': stats.total_points,
            'level': stats.level,
            'streak_days': stats.streak_days,
            'total_lessons_completed': stats.total_lessons_completed,
            'current_difficulty': stats.current_difficulty,
            'accuracy_rate': stats.accuracy_rate
        } if stats else None
    }), 200

