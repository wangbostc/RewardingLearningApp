# English Learning App — Engineering Specification

## 1. Overview
This document specifies the **engineering architecture and implementation details** for a kid‑focused English learning application.

The system expands an existing sentence matching module into a **data‑driven lesson engine** supporting multiple learning activity types.

The platform is designed to be:

- extensible (new activity types easily added)
- content‑driven (lessons defined via structured data)
- child‑friendly
- mobile‑first

Primary stack:

### Backend
- FastAPI
- Python
- uv for dependency and environment management

### Frontend
- Next.js
- React
- TailwindCSS
- Vite (only if currently used for dev tooling or component builds)

---

# 2. High Level Architecture

System components:

```
Frontend (Next.js)
        |
        |
    REST API
        |
Backend (FastAPI)
        |
   Application Services
        |
      Database
```

Optional services:

- media storage (S3 compatible)
- speech evaluation service
- CDN for media assets

---

# 3. Core System Concept

The system revolves around **Lessons**.

Lessons contain ordered **Activities**.

Each activity type corresponds to a UI component in the frontend.

Example:

```
Lesson
  ├─ Activity
  ├─ Activity
  ├─ Activity
  └─ Activity
```

Activities are rendered dynamically based on `type`.

---

# 4. Learning Paths

Learning paths define curriculum structure.

```
LearningPath
  ├─ Unit
  │   ├─ Lesson
  │   │   ├─ Activity
```

Example paths:

- listening
- vocabulary
- reading
- speaking
- grammar
- story

---

# 5. Database Schema

Recommended: **PostgreSQL** with **SQLAlchemy or SQLModel**.

## 5.1 User

```
User
-----
id
email
password_hash
created_at
```

## 5.2 ChildProfile

```
ChildProfile
------------
id
user_id
name
age
avatar
created_at
```

## 5.3 LearningPath

```
LearningPath
------------
id
name
description
order_index
```

## 5.4 Unit

```
Unit
----
id
path_id
name
order_index
```

## 5.5 Lesson

```
Lesson
------
id
unit_id
title
level
order_index
estimated_minutes
```

## 5.6 Activity

```
Activity
--------
id
lesson_id
type
prompt
instructions
activity_data (JSON)
order_index
points
```

`activity_data` stores activity‑specific configuration.

Example:

```
{
  "audioUrl": "/audio/apple.mp3",
  "options": [
    {"id": "apple", "image": "/img/apple.png"},
    {"id": "dog", "image": "/img/dog.png"}
  ],
  "answer": "apple"
}
```

## 5.7 Attempt

Tracks activity attempts.

```
Attempt
-------
id
profile_id
activity_id
answer
correct
score
created_at
```

## 5.8 LessonProgress

```
LessonProgress
--------------
profile_id
lesson_id
completed
score
attempts
last_attempt_at
```

---

# 6. Backend API Design

Base prefix:

```
/api
```

---

# 6.1 Authentication

### Login

```
POST /api/auth/login
```

Request

```
{
  "email": "parent@email.com",
  "password": "password"
}
```

Response

```
{
  "access_token": "jwt",
  "token_type": "bearer"
}
```

---

# 6.2 Profiles

### Get profiles

```
GET /api/profiles
```

### Create profile

```
POST /api/profiles
```

```
{
  "name": "Tom",
  "age": 5
}
```

---

# 6.3 Learning Paths

```
GET /api/paths
```

Returns list of learning paths.

---

# 6.4 Units

```
GET /api/paths/{path_id}/units
```

---

# 6.5 Lessons

### List lessons

```
GET /api/units/{unit_id}/lessons
```

### Get lesson

```
GET /api/lessons/{lesson_id}
```

Example response

```
{
  "id": "lesson_animals_1",
  "title": "Animals 1",
  "activities": [
    {
      "id": "act_1",
      "type": "audio_to_picture",
      "prompt": "Tap the cat",
      "activity_data": {
        "audioUrl": "/audio/cat.mp3",
        "options": [
          {"id": "cat", "image": "/img/cat.png"},
          {"id": "dog", "image": "/img/dog.png"}
        ],
        "answer": "cat"
      }
    }
  ]
}
```

---

# 6.6 Activity Attempt

```
POST /api/activities/{activity_id}/attempt
```

Request

```
{
  "profile_id": "123",
  "answer": "cat",
  "time_spent": 3.2
}
```

Response

```
{
  "correct": true,
  "score": 10
}
```

---

# 6.7 Lesson Completion

```
POST /api/lessons/{lesson_id}/complete
```

---

# 7. Backend Project Structure

```
backend/

app/

  main.py

  api/
    routes/
      auth.py
      profiles.py
      lessons.py
      activities.py
      progress.py

  models/
    user.py
    profile.py
    lesson.py
    activity.py

  schemas/
    auth.py
    profile.py
    lesson.py
    activity.py

  services/
    lesson_service.py
    progress_service.py

  db/
    base.py
    session.py

  seeds/
    seed_lessons.py
```

---

# 8. Frontend Architecture

Main application sections:

```
Parent Dashboard
Child Home
Lesson Player
Results Screen
Profile Settings
```

---

# 9. Frontend Component Structure

```
frontend/

src/

  components/

    lesson/
      LessonPlayer.tsx
      ActivityRenderer.tsx
      ProgressBar.tsx

    activities/
      AudioToPicture.tsx
      WordMatch.tsx
      SentenceOrder.tsx
      StoryQuestion.tsx
      SpeakAfterMe.tsx

    ui/

  hooks/
    useLesson.ts
    useAudio.ts
    useRecorder.ts

  lib/
    api.ts
    types.ts

  pages/
    dashboard
    lesson
```

---

# 10. Activity Type Definitions

Supported activity types:

```
audio_to_picture
word_to_picture
sentence_match
sentence_order
story_question
speak_after_me
fill_missing_letters
choose_correct_word
```

---

# 11. Frontend Activity Renderer

Activity renderer dynamically loads component based on type.

Example logic:

```
switch(activity.type) {

  case 'audio_to_picture':
    return <AudioToPicture />

  case 'sentence_order':
    return <SentenceOrder />

}
```

---

# 12. Lesson Player Flow

```
load lesson

for activity in lesson.activities

render activity

collect answer

submit attempt

move to next activity

finish lesson

show results
```

---

# 13. Progress System

Track:

- lesson completion
- accuracy
- mistakes
- attempts

Unlock rule:

```
score >= 70%
```

---

# 14. Speech Recording

Basic MVP flow:

```
record audio
upload file
store url
```

Endpoint

```
POST /api/media/upload
```

Speech scoring can be implemented later.

---

# 15. Media Storage

Recommended options:

- S3
- Cloudflare R2
- Supabase Storage

Store:

- audio
- images
- story narration

---

# 16. Content Seeding

Initial content pack:

### Unit 1: Animals

Words

```
cat
dog
bird
fish
```

Example sentence

```
I see a cat
```

---

### Unit 2: Food

```
apple
banana
milk
bread
```

---

### Unit 3: Greetings

```
hello
goodbye
how are you
thank you
```

---

# 17. MVP Implementation Plan

### Phase 1

Implement core engine

- lesson schema
- activity schema
- lesson API
- activity renderer

---

### Phase 2

Add activity types

- audio_to_picture
- word_to_picture
- sentence_order

---

### Phase 3

Progress system

- attempts
- lesson completion
- parent dashboard

---

### Phase 4

Content pack

- animals
- food
- greetings

---

# 18. Suggested Engineering Tasks

Backend tasks

```
Define DB schema
Implement lesson APIs
Implement attempt APIs
Add progress tracking
Seed starter lessons
```

Frontend tasks

```
Build lesson player
Implement activity renderer
Implement activity components
Implement progress UI
Implement dashboard
```

---

# 19. Future Enhancements

- pronunciation scoring
- AI tutor
- adaptive difficulty
- spaced repetition
- multi‑child profiles
- offline lessons

---

# 20. Key Design Principle

The system should be built as a **generic lesson engine**.

New learning experiences should be created by:

```
Adding content
+ configuring activity types
```

NOT by writing new application logic each time.

This ensures the platform scales easily as more lessons and learning paths are added.

