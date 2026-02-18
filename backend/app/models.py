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
    exercise_responses = relationship("ExerciseResponse", back_populates="user", cascade="all, delete-orphan")
    rewards = relationship("Reward", back_populates="user", cascade="all, delete-orphan")

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

    # Relationships
    user = relationship("User", back_populates="stats")

class Lesson(Base):
    __tablename__ = 'lessons'

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    difficulty = Column(String(20), default=DifficultyLevel.BEGINNER.value, index=True)
    category = Column(String(100), nullable=True, index=True)
    estimated_duration = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    exercises = relationship("Exercise", back_populates="lesson", cascade="all, delete-orphan")
    progress = relationship("UserProgress", back_populates="lesson", cascade="all, delete-orphan")

class Exercise(Base):
    __tablename__ = 'exercises'

    id = Column(Integer, primary_key=True)
    lesson_id = Column(Integer, ForeignKey('lessons.id'), nullable=False, index=True)
    type = Column(String(20), nullable=False)
    question = Column(Text, nullable=False)
    content = Column(JSON, nullable=True)
    points_value = Column(Integer, default=10)
    order = Column(Integer, nullable=True)

    # Relationships
    lesson = relationship("Lesson", back_populates="exercises")
    responses = relationship("ExerciseResponse", back_populates="exercise", cascade="all, delete-orphan")

class UserProgress(Base):
    __tablename__ = 'user_progress'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    lesson_id = Column(Integer, ForeignKey('lessons.id'), nullable=False, index=True)
    status = Column(String(20), default='in_progress')
    progress_percentage = Column(Float, default=0.0)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="progress")
    lesson = relationship("Lesson", back_populates="progress")

class ExerciseResponse(Base):
    __tablename__ = 'exercise_responses'

    id = Column(Integer, primary_key=True)
    exercise_id = Column(Integer, ForeignKey('exercises.id'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    answer = Column(JSON, nullable=True)
    is_correct = Column(Boolean, nullable=True)
    time_spent = Column(Integer, default=0)
    points_earned = Column(Integer, default=0)
    answered_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    exercise = relationship("Exercise", back_populates="responses")
    user = relationship("User", back_populates="exercise_responses")

class Achievement(Base):
    __tablename__ = 'achievements'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    badge_icon = Column(String(200), nullable=True)
    condition_type = Column(String(50), nullable=False)
    condition_value = Column(Integer, nullable=False)

    # Relationships
    users = relationship("User", secondary=user_achievements, back_populates="achievements")

class Reward(Base):
    __tablename__ = 'rewards'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    reward_type = Column(String(50), nullable=False)
    amount = Column(Integer, nullable=True)
    reason = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="rewards")

# ==================== Pydantic Schemas ====================

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=80)
    email: EmailStr
    password: str = Field(..., min_length=6)
    age: Optional[int] = None
    native_language: Optional[str] = None

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
    accuracy_rate: float
    total_lessons_completed: int
    current_difficulty: str
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
    exercise_count: int = 0

    class Config:
        from_attributes = True

class ExerciseResponse(BaseModel):
    id: int
    lesson_id: int
    type: str
    question: str
    content: Optional[dict] = None
    points_value: int
    order: Optional[int] = None

    class Config:
        from_attributes = True

class ExerciseSubmit(BaseModel):
    answer: str | dict
    time_spent: Optional[int] = None

class UserProgressResponse(BaseModel):
    lesson_id: int
    lesson_title: Optional[str] = None
    status: str
    progress_percentage: float
    started_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserProgressDetailResponse(BaseModel):
    stats: UserStatsResponse
    progress: List[UserProgressResponse] = []

class AchievementResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    badge_icon: Optional[str] = None
    unlocked_at: datetime

    class Config:
        from_attributes = True

class LeaderboardEntry(BaseModel):
    rank: int
    user_id: int
    username: str
    points: int
    level: int
    accuracy_rate: float

class RewardResponse(BaseModel):
    id: int
    reward_type: str
    amount: Optional[int] = None
    reason: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

