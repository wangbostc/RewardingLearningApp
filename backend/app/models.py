from app import db
from datetime import datetime
from enum import Enum

class DifficultyLevel(Enum):
    BEGINNER = "beginner"
    ELEMENTARY = "elementary"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class ExerciseType(Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    FILL_BLANK = "fill_blank"
    LISTENING = "listening"
    SPEAKING = "speaking"

# User Models
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer)
    native_language = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    progress = db.relationship('UserProgress', back_populates='user', cascade='all, delete-orphan')
    stats = db.relationship('UserStats', back_populates='user', uselist=False, cascade='all, delete-orphan')
    achievements = db.relationship('Achievement', secondary='user_achievements', back_populates='users')

    def __repr__(self):
        return f'<User {self.username}>'

class UserStats(db.Model):
    __tablename__ = 'user_stats'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    total_points = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    streak_days = db.Column(db.Integer, default=0)
    last_activity = db.Column(db.DateTime)
    total_lessons_completed = db.Column(db.Integer, default=0)
    current_difficulty = db.Column(db.String(20), default=DifficultyLevel.BEGINNER.value)
    accuracy_rate = db.Column(db.Float, default=0.0)  # Percentage 0-100

    user = db.relationship('User', back_populates='stats')

    def __repr__(self):
        return f'<UserStats user_id={self.user_id} level={self.level}>'

# Lesson Models
class Lesson(db.Model):
    __tablename__ = 'lessons'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    difficulty = db.Column(db.String(20), default=DifficultyLevel.BEGINNER.value)
    category = db.Column(db.String(100))  # e.g., "vocab", "grammar", "conversation"
    estimated_duration = db.Column(db.Integer)  # in minutes
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    exercises = db.relationship('Exercise', back_populates='lesson', cascade='all, delete-orphan')
    progress = db.relationship('UserProgress', back_populates='lesson', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Lesson {self.title}>'

class Exercise(db.Model):
    __tablename__ = 'exercises'

    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # multiple_choice, fill_blank, etc.
    question = db.Column(db.Text, nullable=False)
    content = db.Column(db.JSON)  # Stores options, correct_answer, etc.
    points_value = db.Column(db.Integer, default=10)
    order = db.Column(db.Integer)  # Order within lesson

    lesson = db.relationship('Lesson', back_populates='exercises')
    responses = db.relationship('ExerciseResponse', back_populates='exercise', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Exercise {self.id} - {self.type}>'

# Progress Models
class UserProgress(db.Model):
    __tablename__ = 'user_progress'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=False)
    status = db.Column(db.String(20), default='in_progress')  # not_started, in_progress, completed
    progress_percentage = db.Column(db.Float, default=0.0)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    user = db.relationship('User', back_populates='progress')
    lesson = db.relationship('Lesson', back_populates='progress')

    def __repr__(self):
        return f'<UserProgress user_id={self.user_id} lesson_id={self.lesson_id}>'

class ExerciseResponse(db.Model):
    __tablename__ = 'exercise_responses'

    id = db.Column(db.Integer, primary_key=True)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    answer = db.Column(db.JSON)  # User's response
    is_correct = db.Column(db.Boolean)
    time_spent = db.Column(db.Integer)  # in seconds
    points_earned = db.Column(db.Integer, default=0)
    answered_at = db.Column(db.DateTime, default=datetime.utcnow)

    exercise = db.relationship('Exercise', back_populates='responses')

    def __repr__(self):
        return f'<ExerciseResponse exercise_id={self.exercise_id} correct={self.is_correct}>'

# Reward Models
class Achievement(db.Model):
    __tablename__ = 'achievements'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    badge_icon = db.Column(db.String(200))  # URL or identifier
    condition_type = db.Column(db.String(50))  # 'streak', 'points', 'lessons_completed', etc.
    condition_value = db.Column(db.Integer)  # e.g., 7 days for streak

    users = db.relationship('User', secondary='user_achievements', back_populates='achievements')

    def __repr__(self):
        return f'<Achievement {self.name}>'

class UserAchievement(db.Model):
    __tablename__ = 'user_achievements'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievements.id'), nullable=False)
    unlocked_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<UserAchievement user_id={self.user_id} achievement_id={self.achievement_id}>'

class Reward(db.Model):
    __tablename__ = 'rewards'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reward_type = db.Column(db.String(50))  # 'points', 'badge', 'level_up', etc.
    amount = db.Column(db.Integer)  # Points amount
    reason = db.Column(db.String(200))  # Why the reward was given
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Reward {self.reward_type} user_id={self.user_id}>'

