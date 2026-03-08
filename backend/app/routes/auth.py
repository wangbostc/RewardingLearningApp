from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import get_db
from app.models import (
    User,
    UserStats,
    UserRegister,
    UserLogin,
    UserResponse,
    UserProfileResponse,
    UserStatsResponse,
)
from werkzeug.security import generate_password_hash, check_password_hash

router = APIRouter()


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user."""

    # Check if user already exists
    existing_user = (
        db.query(User)
        .filter((User.username == user_data.username) | (User.email == user_data.email))
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already exists",
        )

    # Create new user
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=generate_password_hash(user_data.password),
        age=user_data.age,
        native_language=user_data.native_language,
    )

    db.add(new_user)
    db.flush()

    # Create user stats
    stats = UserStats(user_id=new_user.id)
    db.add(stats)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=UserResponse)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user."""

    user = db.query(User).filter(User.username == credentials.username).first()

    if not user or not check_password_hash(
        str(user.password_hash), credentials.password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    return user


@router.get("/profile/{user_id}", response_model=UserProfileResponse)
async def get_profile(user_id: int, db: Session = Depends(get_db)):
    """Get user profile."""

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    stats = db.query(UserStats).filter(UserStats.user_id == user_id).first()

    return UserProfileResponse(
        user=UserResponse.model_validate(user),
        stats=UserStatsResponse.model_validate(stats) if stats else None,
    )
