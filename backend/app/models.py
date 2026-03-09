from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    JSON,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime, timezone
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


# Association model for user achievements
class UserAchievement(Base):
    __tablename__ = "user_achievements"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    achievement_id = Column(Integer, ForeignKey("achievements.id"), primary_key=True)
    unlocked_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="user_achievements_rel")
    achievement = relationship("Achievement", back_populates="user_achievements_rel")


# ==================== SQLAlchemy Models ====================


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False)
    age = Column(Integer, nullable=True)
    native_language = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    stats = relationship(
        "UserStats", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    progress = relationship(
        "UserProgress", back_populates="user", cascade="all, delete-orphan"
    )
    achievements = relationship(
        "Achievement", secondary="user_achievements", back_populates="users"
    )
    responses = relationship(
        "UserExerciseResponse", back_populates="user", cascade="all, delete-orphan"
    )
    rewards = relationship(
        "Reward", back_populates="user", cascade="all, delete-orphan"
    )
    user_achievements_rel = relationship("UserAchievement", back_populates="user")
    redemptions = relationship(
        "RewardRedemption", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User {self.username}>"


class UserStats(Base):
    __tablename__ = "user_stats"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True
    )
    total_points = Column(Integer, default=0)
    level = Column(Integer, default=1)
    streak_days = Column(Integer, default=0)
    last_activity = Column(DateTime, nullable=True)
    total_lessons_completed = Column(Integer, default=0)
    current_difficulty = Column(String(20), default=DifficultyLevel.BEGINNER.value)
    accuracy_rate = Column(Float, default=0.0)
    user = relationship("User", back_populates="stats")

    def __repr__(self):
        return f"<UserStats user_id={self.user_id}>"


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    difficulty = Column(String(20), nullable=False)
    category = Column(String(100), nullable=True)
    estimated_duration = Column(Integer, nullable=True)  # in minutes
    order = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    exercises = relationship(
        "Exercise", back_populates="lesson", cascade="all, delete-orphan"
    )
    reading_sentences = relationship(
        "ReadingSentence", back_populates="lesson", cascade="all, delete-orphan"
    )
    progress = relationship(
        "UserProgress", back_populates="lesson", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Lesson {self.title}>"


class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False, index=True)
    type = Column(String(50), nullable=False)
    question = Column(Text, nullable=False)
    content = Column(JSON, nullable=True)  # Store options, hints, etc.
    points_value = Column(Integer, default=10)
    order = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    lesson = relationship("Lesson", back_populates="exercises")
    responses = relationship(
        "UserExerciseResponse", back_populates="exercise", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Exercise {self.id} lesson_id={self.lesson_id}>"


class UserProgress(Base):
    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False, index=True)
    status = Column(
        String(50), default="not_started"
    )  # not_started, in_progress, completed
    progress_percentage = Column(Float, default=0.0)
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="progress")
    lesson = relationship("Lesson", back_populates="progress")


class UserExerciseResponse(Base):
    __tablename__ = "exercise_responses"

    id = Column(Integer, primary_key=True)
    exercise_id = Column(
        Integer, ForeignKey("exercises.id"), nullable=False, index=True
    )
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    answer = Column(JSON, nullable=True)  # User's response
    is_correct = Column(Boolean, nullable=True)
    time_spent = Column(Integer, nullable=True)  # in seconds
    points_earned = Column(Integer, default=0)
    answered_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    exercise = relationship("Exercise", back_populates="responses")
    user = relationship("User", back_populates="responses")


class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    badge_icon = Column(String(200), nullable=True)
    condition_type = Column(
        String(50), nullable=True
    )  # 'streak', 'points', 'lessons_completed'
    condition_value = Column(Integer, nullable=True)

    users = relationship(
        "User", secondary="user_achievements", back_populates="achievements"
    )
    user_achievements_rel = relationship(
        "UserAchievement", back_populates="achievement"
    )

    def __repr__(self):
        return f"<Achievement {self.name}>"


class Reward(Base):
    __tablename__ = "rewards"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    reward_type = Column(String(50), nullable=False)  # 'points', 'badge', 'level_up'
    amount = Column(Integer, nullable=True)
    reason = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="rewards")


class ReadingSentence(Base):
    __tablename__ = "reading_sentences"

    id = Column(Integer, primary_key=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False, index=True)
    text = Column(Text, nullable=False)  # The sentence to read aloud
    difficulty_level = Column(Integer, default=1)  # 1-5
    category = Column(String(100), nullable=True)  # sight_words, decodable, short_story
    points_value = Column(Integer, default=10)
    order = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    lesson = relationship("Lesson", back_populates="reading_sentences")

    def __repr__(self):
        return f"<ReadingSentence {self.id}: {self.text[:30]}>"


class RewardItem(Base):
    __tablename__ = "reward_items"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)
    emoji = Column(String(10), nullable=True)  # Emoji icon for display
    points_cost = Column(Integer, nullable=False)
    stock = Column(Integer, nullable=True)  # null = unlimited
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    redemptions = relationship(
        "RewardRedemption", back_populates="reward_item", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<RewardItem {self.name}>"


class RewardRedemption(Base):
    __tablename__ = "reward_redemptions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    reward_item_id = Column(
        Integer, ForeignKey("reward_items.id"), nullable=False, index=True
    )
    points_spent = Column(Integer, nullable=False)
    status = Column(
        String(20), default="pending"
    )  # pending, approved, fulfilled, rejected
    redeemed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="redemptions")
    reward_item = relationship("RewardItem", back_populates="redemptions")


class LearningPath(Base):
    __tablename__ = "learning_paths"

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    units = relationship(
        "LearningUnit", back_populates="path", cascade="all, delete-orphan"
    )


class LearningUnit(Base):
    __tablename__ = "learning_units"

    id = Column(Integer, primary_key=True)
    path_id = Column(Integer, ForeignKey("learning_paths.id"), nullable=False, index=True)
    name = Column(String(160), nullable=False)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    path = relationship("LearningPath", back_populates="units")
    lessons = relationship(
        "EngineLesson", back_populates="unit", cascade="all, delete-orphan"
    )


class EngineLesson(Base):
    __tablename__ = "engine_lessons"

    id = Column(Integer, primary_key=True)
    unit_id = Column(Integer, ForeignKey("learning_units.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    level = Column(String(30), nullable=True)
    order_index = Column(Integer, default=0)
    estimated_minutes = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    unit = relationship("LearningUnit", back_populates="lessons")
    activities = relationship(
        "LearningActivity", back_populates="lesson", cascade="all, delete-orphan"
    )


class LearningActivity(Base):
    __tablename__ = "learning_activities"

    id = Column(Integer, primary_key=True)
    lesson_id = Column(Integer, ForeignKey("engine_lessons.id"), nullable=False, index=True)
    type = Column(String(60), nullable=False)
    prompt = Column(Text, nullable=False)
    instructions = Column(Text, nullable=True)
    activity_data = Column(JSON, nullable=True)
    order_index = Column(Integer, default=0)
    points = Column(Integer, default=10)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    lesson = relationship("EngineLesson", back_populates="activities")
    attempts = relationship(
        "ActivityAttempt", back_populates="activity", cascade="all, delete-orphan"
    )


class ActivityAttempt(Base):
    __tablename__ = "activity_attempts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    activity_id = Column(
        Integer, ForeignKey("learning_activities.id"), nullable=False, index=True
    )
    answer = Column(JSON, nullable=True)
    correct = Column(Boolean, nullable=True)
    score = Column(Integer, default=0)
    time_spent = Column(Float, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    activity = relationship("LearningActivity", back_populates="attempts")


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
    is_admin: bool = False
    age: Optional[int] = None
    native_language: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


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

    model_config = {"from_attributes": True}


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

    model_config = {"from_attributes": True}


class ExerciseResponse(BaseModel):
    id: int
    lesson_id: int
    type: str
    question: str
    content: Optional[dict] = None
    points_value: int
    order: Optional[int] = None

    model_config = {"from_attributes": True}


class ExerciseSubmit(BaseModel):
    answer: str | dict
    time_spent: Optional[int] = None


class ExerciseDetailResponse(BaseModel):
    id: int
    type: str
    question: str
    content: Optional[dict] = None
    points_value: int
    order: Optional[int] = None

    model_config = {"from_attributes": True}


class UserProgressResponse(BaseModel):
    id: Optional[int] = None  # Added id
    user_id: Optional[int] = None  # Added user_id
    lesson_id: int
    lesson_title: Optional[str] = None
    status: str
    progress_percentage: float
    started_at: datetime
    completed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class UserProgressDetailResponse(BaseModel):
    stats: UserStatsResponse
    progress: List[UserProgressResponse] = []


class AchievementResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    badge_icon: Optional[str] = None
    unlocked_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


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

    model_config = {"from_attributes": True}


# ==================== Reading Sentence Schemas ====================


class ReadingSentenceResponse(BaseModel):
    id: int
    lesson_id: int
    text: str
    difficulty_level: int
    category: Optional[str] = None
    points_value: int
    order: Optional[int] = None

    model_config = {"from_attributes": True}


class ReadingSentenceCreate(BaseModel):
    lesson_id: int
    text: str
    difficulty_level: int = 1
    category: Optional[str] = None
    points_value: int = 10
    order: Optional[int] = None


class SpeechCheckRequest(BaseModel):
    user_id: int
    sentence_id: int
    transcript: str


class SpeechTokenFeedback(BaseModel):
    text: str
    status: str  # correct, wrong, missing, extra, neutral


class SpeechCheckResponse(BaseModel):
    is_correct: bool
    similarity: float
    points_earned: int
    expected: str
    heard: str
    message: str
    expected_tokens: List[SpeechTokenFeedback] = Field(default_factory=list)
    heard_tokens: List[SpeechTokenFeedback] = Field(default_factory=list)


# ==================== Reward Shop Schemas ====================


class RewardItemResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    emoji: Optional[str] = None
    points_cost: int
    stock: Optional[int] = None
    is_active: bool

    model_config = {"from_attributes": True}


class RewardItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    emoji: Optional[str] = None
    points_cost: int
    stock: Optional[int] = None
    is_active: bool = True


class RewardItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    emoji: Optional[str] = None
    points_cost: Optional[int] = None
    stock: Optional[int] = None
    is_active: Optional[bool] = None


class RedeemRequest(BaseModel):
    user_id: int


class RewardRedemptionResponse(BaseModel):
    id: int
    user_id: int
    reward_item_id: int
    reward_item_name: Optional[str] = None
    reward_item_emoji: Optional[str] = None
    points_spent: int
    status: str
    redeemed_at: datetime

    model_config = {"from_attributes": True}


class RedemptionStatusUpdate(BaseModel):
    status: str  # approved, fulfilled, rejected


class LearningPathResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    order_index: int

    model_config = {"from_attributes": True}


class LearningUnitResponse(BaseModel):
    id: int
    path_id: int
    name: str
    order_index: int

    model_config = {"from_attributes": True}


class EngineLessonSummaryResponse(BaseModel):
    id: int
    unit_id: int
    title: str
    level: Optional[str] = None
    order_index: int
    estimated_minutes: Optional[int] = None
    activity_count: int = 0

    model_config = {"from_attributes": True}


class LearningActivityResponse(BaseModel):
    id: int
    lesson_id: int
    type: str
    prompt: str
    instructions: Optional[str] = None
    activity_data: Optional[dict] = None
    order_index: int
    points: int

    model_config = {"from_attributes": True}


class EngineLessonDetailResponse(BaseModel):
    id: int
    unit_id: int
    title: str
    level: Optional[str] = None
    order_index: int
    estimated_minutes: Optional[int] = None
    activities: List[LearningActivityResponse] = Field(default_factory=list)

