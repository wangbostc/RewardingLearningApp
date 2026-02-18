from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Table, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from enum import Enum
from typing import Optional, List

# SQLAlchemy Base
Base = declarative_base()

# Enums
class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    ELEMENTARY = "elementary"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class ExerciseType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    FILL_BLANK = "fill_blank"
    LISTENING = "listening"
    SPEAKING = "speaking"

# Association table for user achievements
user_achievements = Table(
    'user_achievements',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('achievement_id', Integer, ForeignKey('achievements.id'), primary_key=True),
    Column('unlocked_at', DateTime, default=datetime.utcnow)
)

# ==================== SQLAlchemy Models ====================

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    age = Column(Integer, nullable=True)
    native_language = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    stats = relationship("UserStats", back_populates="user", uselist=False, cascade="all, delete-orphan")
    progress = relationship("UserProgress", back_populates="user", cascade="all, delete-orphan")
    achievements = relationship("Achievement", secondary=user_achievements, back_populates="users")
    responses = relationship("ExerciseResponse", back_populates="user", cascade="all, delete-orphan")
    rewards = relationship("Reward", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f'<User {self.username}>'

class UserStats(Base):
    __tablename__ = 'user_stats'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True, index=True)
    total_points = Column(Integer, default=0)
    level = Column(Integer, default=1)
    streak_days = Column(Integer, default=0)
    last_activity = Column(DateTime, nullable=True)
    total_lessons_completed = Column(Integer, default=0)
    current_difficulty = Column(String(20), default=DifficultyLevel.BEGINNER.value)
    accuracy_rate = Column(Float, default=0.0)
    user = relationship("User", back_populates="stats")

    def __repr__(self):
        return f'<UserStats user_id={self.user_id}>'

class Lesson(Base):
    __tablename__ = 'lessons'

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    difficulty = Column(String(20), nullable=False)
    category = Column(String(100), nullable=True)
    estimated_duration = Column(Integer, nullable=True)  # in minutes
    order = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    exercises = relationship("Exercise", back_populates="lesson", cascade="all, delete-orphan")
    progress = relationship("UserProgress", back_populates="lesson", cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Lesson {self.title}>'

class Exercise(Base):
    __tablename__ = 'exercises'

    id = Column(Integer, primary_key=True)
    lesson_id = Column(Integer, ForeignKey('lessons.id'), nullable=False, index=True)
    type = Column(String(50), nullable=False)
    question = Column(Text, nullable=False)
    content = Column(JSON, nullable=True)  # Store options, hints, etc.
    points_value = Column(Integer, default=10)
    order = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    lesson = relationship("Lesson", back_populates="exercises")
    responses = relationship("ExerciseResponse", back_populates="exercise", cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Exercise {self.id} lesson_id={self.lesson_id}>'

class UserProgress(Base):
    __tablename__ = 'user_progress'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    lesson_id = Column(Integer, ForeignKey('lessons.id'), nullable=False, index=True)
    status = Column(String(50), default='not_started')  # not_started, in_progress, completed
    progress_percentage = Column(Float, default=0.0)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="progress")
    lesson = relationship("Lesson", back_populates="progress")

    def __repr__(self):
        return f'<UserProgress user_id={self.user_id} lesson_id={self.lesson_id}>'

class ExerciseResponse(Base):
    __tablename__ = 'exercise_responses'

    id = Column(Integer, primary_key=True)
    exercise_id = Column(Integer, ForeignKey('exercises.id'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    answer = Column(JSON, nullable=True)  # User's response
    is_correct = Column(Boolean, nullable=True)
    time_spent = Column(Integer, nullable=True)  # in seconds
    points_earned = Column(Integer, default=0)
    answered_at = Column(DateTime, default=datetime.utcnow)

    exercise = relationship("Exercise", back_populates="responses")
    user = relationship("User", back_populates="responses")

    def __repr__(self):
        return f'<ExerciseResponse exercise_id={self.exercise_id} correct={self.is_correct}>'

class Achievement(Base):
    __tablename__ = 'achievements'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    badge_icon = Column(String(200), nullable=True)
    condition_type = Column(String(50), nullable=True)  # 'streak', 'points', 'lessons_completed'
    condition_value = Column(Integer, nullable=True)

    users = relationship("User", secondary=user_achievements, back_populates="achievements")

    def __repr__(self):
        return f'<Achievement {self.name}>'

class Reward(Base):
    __tablename__ = 'rewards'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    reward_type = Column(String(50), nullable=False)  # 'points', 'badge', 'level_up'
    amount = Column(Integer, nullable=True)
    reason = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="rewards")

    def __repr__(self):
        return f'<Reward {self.reward_type} user_id={self.user_id}>'

# ==================== Pydantic Models (for request/response validation) ====================

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=80)
    email: EmailStr
    password: str = Field(..., min_length=6)
    age: Optional[int] = None
    native_language: Optional[str] = "unknown"

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    age: Optional[int] = None
    native_language: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class UserStatsResponse(BaseModel):
    id: int
    user_id: int
    total_points: int
    level: int
    streak_days: int
    total_lessons_completed: int
    current_difficulty: str
    accuracy_rate: float
    last_activity: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserProfileResponse(BaseModel):
    user: UserResponse
    stats: Optional[UserStatsResponse] = None

class LessonResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    difficulty: str
    category: Optional[str] = None
    estimated_duration: Optional[int] = None

    class Config:
        from_attributes = True

class ExerciseDetailResponse(BaseModel):
    id: int
    type: str
    question: str
    content: Optional[dict] = None
    points_value: int
    order: Optional[int] = None

    class Config:
        from_attributes = True

class UserProgressResponse(BaseModel):
    id: int
    user_id: int
    lesson_id: int
    status: str
    progress_percentage: float
    started_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AchievementResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    badge_icon: Optional[str] = None

    class Config:
        from_attributes = True

