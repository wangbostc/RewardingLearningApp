# 🚀 Quick Start Guide

This guide will get you up and running with the Rewarding Adaptive English Learning App in just a few minutes.

## Prerequisites

Before you begin, make sure you have installed:

- **Python 3.11 or higher** - [Download](https://www.python.org/downloads/)
- **Node.js 18+ and npm** - [Download](https://nodejs.org/)
- **Git** - [Download](https://git-scm.com/)
- **uv** (optional but recommended) - `brew install uv` or [Download](https://docs.astral.sh/uv/)

## Step 1: Start the Backend Server

### Option A: Using uv (Recommended)

```bash
cd backend
uv sync
uv run python main.py
```

### Option B: Using pip

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

✅ **Backend is running at** `http://localhost:5000`

## Step 2: Seed Sample Data (Optional but Recommended)

In a new terminal window:

```bash
cd backend

# Using uv
uv run python seed.py

# OR using Python directly (if venv is activated)
python seed.py
```

This creates:
- 5 sample lessons (Beginner to Intermediate)
- 4 exercises with different types
- 5 achievement badges
- 1 demo user for testing:
  - **Username**: `learner`
  - **Password**: `password123`

## Step 3: Start the Frontend Server

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

✅ **Frontend is running at** `http://localhost:3000`

## Step 4: Open in Browser

Visit **http://localhost:3000** and you should see the home page!

## Testing the App

### Sign In with Demo Account

1. Click "Login" on the home page
2. Use credentials:
   - Username: `learner`
   - Password: `password123`

### Explore Features

1. **Dashboard** - View your stats and quick actions
2. **Browse Lessons** - Explore available lessons filtered by difficulty and category
3. **Progress** - Track your learning journey
4. **Achievements** - View badges and leaderboard

### Create a New Account

1. Click "Sign Up" on the home page
2. Fill in the registration form
3. You'll be automatically logged in and redirected to the dashboard

## File Structure Quick Reference

```
RewardingLearning/
├── backend/
│   ├── app/models.py           # Database models
│   ├── app/routes/
│   │   ├── auth.py             # User registration & login
│   │   ├── lessons.py          # Lesson management
│   │   ├── progress.py         # Progress tracking
│   │   └── rewards.py          # Achievements & leaderboard
│   ├── seed.py                 # Sample data script
│   └── main.py                 # Flask entry point
│
├── frontend/
│   ├── src/app/
│   │   ├── page.tsx            # Home page
│   │   ├── dashboard/page.tsx  # User dashboard
│   │   ├── lessons/page.tsx    # Lesson browser
│   │   ├── progress/page.tsx   # Progress tracker
│   │   └── rewards/page.tsx    # Achievements & leaderboard
│   └── src/lib/api-client.ts   # API client
```

## API Endpoints Quick Reference

### Authentication
```
POST /api/auth/register      - Create new user
POST /api/auth/login         - Login user
GET  /api/auth/profile/{id}  - Get user profile
```

### Lessons
```
GET  /api/lessons                    - List all lessons
GET  /api/lessons/{id}               - Get single lesson
POST /api/lessons/{userId}/start/{lessonId}
```

### Progress
```
POST /api/progress/exercises/{userId}/{exerciseId}
GET  /api/progress/user/{userId}
POST /api/progress/lessons/{lessonId}/complete/{userId}
```

### Rewards
```
GET  /api/rewards/achievements/{userId}
POST /api/rewards/check-achievements/{userId}
GET  /api/rewards/leaderboard
```

## Troubleshooting

### Port Already in Use

**Backend port 5000 is in use:**
```bash
# Change port in backend/main.py:
app.run(debug=debug, host='0.0.0.0', port=5001)
```

**Frontend port 3000 is in use:**
```bash
npm run dev -- -p 3001
```

### Database Issues

**Reset the database:**
```bash
cd backend
rm learning.db
uv run python main.py
uv run python seed.py
```

### Connection Refused

Make sure both servers are running:
- Backend: `http://localhost:5000`
- Frontend: `http://localhost:3000`

Check environment variables:
- Backend: `.env` file exists with correct DATABASE_URL
- Frontend: `.env.local` has `NEXT_PUBLIC_API_URL=http://localhost:5000/api`

## Common Tasks

### Adding a New Lesson

1. Add lesson record in database (use a database GUI or Python script)
2. Attach exercises to the lesson
3. Reload the lessons page in frontend

### Creating a Custom Achievement

Edit `backend/seed.py` and add to `achievements_data`, then run seed script again.

### Viewing Database

Install SQLite viewer or use Python:
```bash
cd backend
python
>>> import sqlite3
>>> conn = sqlite3.connect('learning.db')
>>> cursor = conn.cursor()
>>> cursor.execute("SELECT * FROM users")
>>> cursor.fetchall()
```

## Next Steps

1. **Customize Lessons** - Add your own content in the database
2. **Deploy** - See README.md for deployment instructions
3. **Extend Features** - Add speaking exercises, social features, etc.
4. **Mobile App** - Create React Native version

## Need Help?

- Check the main [README.md](./README.md) for architecture details
- Review API documentation in the API endpoints section
- Check console for error messages (Browser DevTools or Terminal)

---

**Happy Learning! 🎓✨**

