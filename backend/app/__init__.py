from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize database
engine = create_engine(
    os.getenv("DATABASE_URL", "sqlite:///learning.db"),
    connect_args={"check_same_thread": False}
    if "sqlite" in os.getenv("DATABASE_URL", "")
    else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    from app.models import Base

    app = FastAPI(
        title="Rewarding English Learning API",
        description="Adaptive English learning platform with gamification",
        version="1.0.0",
    )

    # Create tables
    Base.metadata.create_all(bind=engine)

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    from app.routes import auth, lessons, progress, rewards, speech, shop, admin

    app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
    app.include_router(lessons.router, prefix="/api/lessons", tags=["Lessons"])
    app.include_router(progress.router, prefix="/api/progress", tags=["Progress"])
    app.include_router(rewards.router, prefix="/api/rewards", tags=["Rewards"])
    app.include_router(speech.router, prefix="/api/speech", tags=["Speech"])
    app.include_router(shop.router, prefix="/api/shop", tags=["Shop"])
    app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])

    @app.get("/")
    async def root():
        return {
            "message": "Rewarding English Learning API",
            "version": "1.0.0",
            "docs": "/docs",
        }

    return app
