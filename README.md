# 🎓 Rewarding Adaptive English Learning App

A full-stack application designed to help kids learn English through engaging, adaptive lessons with gamified rewards and progress tracking.

## 📋 Project Overview

**RewardingLearning** combines:
- **Backend**: Flask REST API with SQLAlchemy ORM for data persistence
- **Frontend**: Next.js (React) with TypeScript and Tailwind CSS for a modern UI
- **Database**: SQLite (can be upgraded to PostgreSQL)
- **Features**: User authentication, adaptive lessons, progress tracking, achievement system, and leaderboards

## 🏗️ Project Structure

```
RewardingLearning/
├── backend/                    # Flask backend application
│   ├── app/
│   │   ├── __init__.py        # Flask app factory
│   │   ├── models.py          # Database models
│   │   └── routes/
│   │       ├── auth.py        # Authentication endpoints
│   │       ├── lessons.py     # Lesson management
│   │       ├── progress.py    # User progress tracking
│   │       └── rewards.py     # Achievements & rewards
│   ├── main.py                # Entry point
│   ├── .env                   # Environment variables
│   └── pyproject.toml         # Python dependencies
│
├── frontend/                  # Next.js frontend application
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx       # Home page
│   │   │   ├── dashboard/     # User dashboard
│   │   │   ├── auth/          # Login & registration
│   │   │   └── lessons/       # Lesson browsing
│   │   └── lib/
│   │       └── api-client.ts  # API client
│   ├── package.json           # Node dependencies
│   └── next.config.ts         # Next.js configuration
│
└── README.md                  # This file

```

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+ & npm
- `uv` package manager for Python (optional but recommended)

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Install dependencies with uv:**
   ```bash
   uv sync
   ```

3. **Configure environment:**
   Edit `.env` file (already created with defaults)

4. **Run the server:**
   ```bash
   uv run python main.py
   ```

   The backend will run at `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure API URL:**
   Create `.env.local`:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:5000/api
   ```

4. **Run the development server:**
   ```bash
   npm run dev
   ```

   The frontend will run at `http://localhost:3000`

## 📚 API Documentation

### Authentication Endpoints

#### Register
```
POST /api/auth/register
Content-Type: application/json

{
  "username": "string",
  "email": "string",
  "password": "string",
  "age": "number (optional)",
  "native_language": "string (optional)"
}
```

#### Login
```
POST /api/auth/login
Content-Type: application/json

{
  "username": "string",
  "password": "string"
}
```

#### Get Profile
```
GET /api/auth/profile/{userId}
```

### Lesson Endpoints

#### Get All Lessons
```
GET /api/lessons?difficulty=beginner&category=vocab
```

#### Get Single Lesson
```
GET /api/lessons/{lessonId}
```

#### Start Lesson
```
POST /api/lessons/{userId}/start/{lessonId}
```

### Progress Endpoints

#### Submit Exercise
```
POST /api/progress/exercises/{userId}/{exerciseId}
Content-Type: application/json

{
  "answer": "any",
  "time_spent": 30
}
```

#### Get User Progress
```
GET /api/progress/user/{userId}
```

#### Complete Lesson
```
POST /api/progress/lessons/{lessonId}/complete/{userId}
```

### Rewards Endpoints

#### Get User Achievements
```
GET /api/rewards/achievements/{userId}
```

#### Check Achievements
```
POST /api/rewards/check-achievements/{userId}
```

#### Get Leaderboard
```
GET /api/rewards/leaderboard?limit=10
```

## 🗄️ Database Schema

### Core Tables

- **users**: User accounts and profiles
- **user_stats**: User progress metrics (points, level, streak, etc.)
- **lessons**: Learning content organized by difficulty and category
- **exercises**: Individual exercises within lessons
- **user_progress**: Track lesson completion status
- **exercise_responses**: User answers and performance data
- **achievements**: Badge definitions and conditions
- **user_achievements**: User's unlocked badges
- **rewards**: Point and reward transactions

## 🎮 Feature Highlights

### Adaptive Learning
- Difficulty automatically adjusts based on user performance
- Exercises tracked by accuracy rate
- Content recommendations based on weak areas

### Gamification
- **Points System**: Earn points for correct answers
- **Leveling**: Progress through levels every 10 lessons completed
- **Streaks**: Track consecutive learning days
- **Achievements**: Unlock badges for milestones (7-day streak, 100 points, etc.)
- **Leaderboard**: Compete with other learners

### Progress Tracking
- Real-time accuracy rate calculation
- Performance metrics by lesson and category
- Visual progress indicators
- Historical data for analytics

## 🔧 Configuration

### Backend `.env`
```
FLASK_ENV=development
FLASK_APP=main.py
DATABASE_URL=sqlite:///learning.db
SECRET_KEY=your-secret-key-change-in-production
```

### Frontend `.env.local`
```
NEXT_PUBLIC_API_URL=http://localhost:5000/api
```

## 📖 Development Workflow

### Adding a New Lesson

1. **Backend**: Create lesson record in database
   ```python
   lesson = Lesson(
       title="Greetings",
       description="Learn basic English greetings",
       difficulty="beginner",
       category="conversation"
   )
   db.session.add(lesson)
   ```

2. **Add Exercises**: Attach exercises to the lesson
3. **Frontend**: List appears automatically in lessons page

### Creating Custom Exercises

Exercises support multiple types:
- `multiple_choice`: Select from options
- `fill_blank`: Fill in missing words
- `listening`: Audio-based exercises
- `speaking`: Pronunciation practice (future)

## 🚀 Deployment

### Backend (Vercel, Railway, or Heroku)
1. Configure production database (PostgreSQL)
2. Set environment variables
3. Deploy Flask app with WSGI server (Gunicorn)

### Frontend (Vercel)
1. Connect GitHub repository
2. Set environment variables
3. Deploy Next.js with automatic CI/CD

## 📝 Future Enhancements

- [ ] Real-time adaptive difficulty based on performance
- [ ] Audio/speech recognition for listening exercises
- [ ] Social features (friend challenges, team learning)
- [ ] Mobile app (React Native)
- [ ] ML-powered content recommendation
- [ ] Parent dashboard for monitoring progress
- [ ] Custom lesson creation for teachers
- [ ] Analytics and reporting

## 🛠️ Tech Stack

### Backend
- **Framework**: Flask 3.0.0
- **Database ORM**: SQLAlchemy 2.0.25
- **Database**: SQLite (development), PostgreSQL (production)
- **CORS**: Flask-CORS 4.0.0

### Frontend
- **Framework**: Next.js 15+
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Package Manager**: npm

### Tools
- **Python Package Manager**: uv
- **Version Control**: Git

## 📄 License

This project is designed for educational purposes.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📧 Support

For questions or issues, please open an issue on GitHub or contact the development team.

---

**Happy Learning! 🚀**

