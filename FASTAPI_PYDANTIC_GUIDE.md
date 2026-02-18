# FastAPI + Pydantic Usage Guide

## Quick Reference

### Running the Server

```bash
cd backend
uv sync        # Install/sync dependencies
uv run python main.py
```

Your API will be at: `http://localhost:5000`

---

## Understanding the New Architecture

### 1. FastAPI App Factory (app/__init__.py)

```python
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///learning.db')
SessionLocal = sessionmaker(bind=engine)

def get_db():
    """Dependency for database sessions"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_app() -> FastAPI:
    """Create FastAPI app with routes"""
    app = FastAPI()
    
    # Add routes
    app.include_router(auth.router, prefix="/api/auth")
    app.include_router(lessons.router, prefix="/api/lessons")
    
    return app
```

### 2. Pydantic Models (app/models.py)

```python
# Request validation
class UserRegister(BaseModel):
    username: str = Field(..., min_length=3)
    email: EmailStr
    password: str = Field(..., min_length=6)

# Response model
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    
    class Config:
        from_attributes = True  # ORM compatibility
```

### 3. FastAPI Routes (app/routes/auth.py)

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserRegister,           # Pydantic validation
    db: Session = Depends(get_db)      # Database injection
):
    """Register a new user"""
    
    # Create user
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=generate_password_hash(user_data.password)
    )
    
    db.add(new_user)
    db.commit()
    
    return new_user  # Auto-serialized to UserResponse
```

---

## Pydantic Features You're Using

### 1. Request Validation

```python
class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=80)
    email: EmailStr                           # Validates email format
    password: str = Field(..., min_length=6)
    age: Optional[int] = None                 # Optional field
    native_language: Optional[str] = None     # With default
```

Invalid request → Automatic 422 error:
```json
{
  "detail": [
    {
      "loc": ["body", "username"],
      "msg": "ensure this value has at least 3 characters",
      "type": "value_error.string.too_short"
    }
  ]
}
```

### 2. Response Models

```python
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True  # Converts SQLAlchemy to dict

# Endpoint returns SQLAlchemy model
@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).get(user_id)
    return user  # Auto-converted to UserResponse JSON
```

### 3. Type Hints

```python
@router.get("/lessons", response_model=dict)
async def get_lessons(
    difficulty: str = Query(None),      # Query parameter
    limit: int = Query(10, ge=1, le=100),  # With constraints
    db: Session = Depends(get_db)       # Dependency
):
    """Type hints provide auto-documentation"""
    pass
```

---

## API Documentation

### Automatic Swagger UI

Visit: `http://localhost:5000/docs`

Features:
- ✅ See all endpoints
- ✅ View request/response schemas
- ✅ Try endpoints directly in browser
- ✅ Test with different parameters

### Automatic ReDoc

Visit: `http://localhost:5000/redoc`

Features:
- ✅ Beautiful documentation
- ✅ Searchable endpoints
- ✅ Response schema details

---

## Error Handling

### HTTP Exceptions

```python
@router.get("/users/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).get(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user
```

### Validation Errors

Pydantic automatically returns 422 with error details:

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "invalid email format",
      "type": "value_error.email"
    }
  ]
}
```

---

## Database Session Dependency

```python
from app import get_db

@router.get("/user/{user_id}")
async def get_user(
    user_id: int,
    db: Session = Depends(get_db)  # Automatic session injection
):
    """
    FastAPI automatically:
    1. Creates a database session
    2. Passes it to the function
    3. Closes it after response
    """
    user = db.query(User).filter(User.id == user_id).first()
    return user
```

---

## Common Patterns

### Query Parameters

```python
@router.get("/lessons")
async def get_lessons(
    difficulty: str = Query(None),
    category: str = Query(None),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Lesson)
    
    if difficulty:
        query = query.filter(Lesson.difficulty == difficulty)
    if category:
        query = query.filter(Lesson.category == category)
    
    lessons = query.limit(limit).all()
    return {"lessons": lessons}
```

### Request Body

```python
@router.post("/exercises/{user_id}/{exercise_id}")
async def submit_exercise(
    user_id: int,
    exercise_id: int,
    submission: ExerciseSubmit,  # Pydantic model from body
    db: Session = Depends(get_db)
):
    # submission.answer is validated
    # submission.time_spent is validated
    pass
```

### Path Parameters

```python
@router.get("/users/{user_id}/profile")
async def get_profile(
    user_id: int,  # Path parameter (required)
    db: Session = Depends(get_db)
):
    pass
```

---

## Testing Endpoints

### Using Swagger UI

1. Go to http://localhost:5000/docs
2. Click endpoint section (e.g., "Authentication")
3. Click the endpoint (e.g., "POST /api/auth/register")
4. Click "Try it out"
5. Fill in parameters
6. Click "Execute"
7. See response

### Using cURL

```bash
# Register user
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "email": "john@example.com",
    "password": "pass123"
  }'

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "password": "pass123"
  }'

# Get lessons with filter
curl "http://localhost:5000/api/lessons?difficulty=beginner"
```

### Using Python

```python
import requests

# Register
response = requests.post(
    "http://localhost:5000/api/auth/register",
    json={
        "username": "john",
        "email": "john@example.com",
        "password": "pass123"
    }
)
print(response.json())

# Get lessons
response = requests.get(
    "http://localhost:5000/api/lessons",
    params={"difficulty": "beginner"}
)
print(response.json())
```

---

## Extending the API

### Adding a New Endpoint

```python
# 1. Create Pydantic model
class LessonCreate(BaseModel):
    title: str = Field(..., min_length=3)
    description: str
    difficulty: DifficultyLevel

# 2. Create route
@router.post("/lessons", response_model=LessonResponse)
async def create_lesson(
    lesson_data: LessonCreate,
    db: Session = Depends(get_db)
):
    lesson = Lesson(**lesson_data.dict())
    db.add(lesson)
    db.commit()
    db.refresh(lesson)
    return lesson

# 3. It automatically appears in Swagger UI!
```

### Adding Validation

```python
class ExerciseSubmit(BaseModel):
    answer: str | dict
    time_spent: int = Field(..., ge=0, le=3600)  # 0-60 min
    
    @validator('answer')
    def answer_not_empty(cls, v):
        if not v:
            raise ValueError('Answer cannot be empty')
        return v
```

---

## Tips & Best Practices

1. **Always use Pydantic models**
   - Validates requests
   - Documents API
   - Type-safe

2. **Use response_model**
   - Controls response format
   - Auto-serializes ORM objects
   - Generates OpenAPI schema

3. **Use Depends for dependencies**
   - Database sessions
   - Authentication
   - Shared logic

4. **Use type hints**
   - Auto-documentation
   - IDE support
   - Better maintainability

5. **Use descriptive error messages**
   - Helps frontend developers
   - Better debugging

---

## Reference Links

- FastAPI Docs: https://fastapi.tiangolo.com/
- Pydantic Docs: https://docs.pydantic.dev/
- Swagger UI: http://localhost:5000/docs
- ReDoc: http://localhost:5000/redoc

---

**Happy coding with FastAPI + Pydantic!** 🚀

