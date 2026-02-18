#!/usr/bin/env python3
"""
Seed script to populate the database with sample lessons and achievements.
Run this after setting up the backend to get started with demo data.
"""

from app import create_app, db
from app.models import (
    User, UserStats, Lesson, Exercise, Achievement,
    DifficultyLevel, ExerciseType
)
from werkzeug.security import generate_password_hash

def seed_database():
    """Populate database with sample data."""
    app = create_app()

    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()

        print("🌱 Seeding database...")

        # Create sample lessons
        lessons_data = [
            {
                'title': 'Basic Greetings',
                'description': 'Learn how to greet people in English',
                'difficulty': 'beginner',
                'category': 'conversation',
                'estimated_duration': 5
            },
            {
                'title': 'Common Verbs',
                'description': 'Practice the most common English verbs',
                'difficulty': 'beginner',
                'category': 'vocab',
                'estimated_duration': 10
            },
            {
                'title': 'Past Tense',
                'description': 'Master the past tense in English',
                'difficulty': 'elementary',
                'category': 'grammar',
                'estimated_duration': 15
            },
            {
                'title': 'Restaurant Conversation',
                'description': 'Learn how to order food at a restaurant',
                'difficulty': 'intermediate',
                'category': 'conversation',
                'estimated_duration': 12
            },
            {
                'title': 'Business English Essentials',
                'description': 'Key phrases for business communication',
                'difficulty': 'intermediate',
                'category': 'vocab',
                'estimated_duration': 20
            }
        ]

        lessons = []
        for lesson_data in lessons_data:
            lesson = Lesson(**lesson_data)
            db.session.add(lesson)
            lessons.append(lesson)

        db.session.flush()

        # Add exercises to lessons
        exercises_data = [
            {
                'lesson_id': lessons[0].id,
                'type': 'multiple_choice',
                'question': 'How do you greet someone in the morning?',
                'content': {
                    'options': ['Good morning', 'Good night', 'Good bye', 'Hello evening'],
                    'correct_answer': 'Good morning'
                },
                'points_value': 10,
                'order': 1
            },
            {
                'lesson_id': lessons[0].id,
                'type': 'fill_blank',
                'question': 'How are ___?',
                'content': {
                    'correct_answer': 'you'
                },
                'points_value': 10,
                'order': 2
            },
            {
                'lesson_id': lessons[1].id,
                'type': 'multiple_choice',
                'question': 'Which is a common verb?',
                'content': {
                    'options': ['run', 'blue', 'happy', 'table'],
                    'correct_answer': 'run'
                },
                'points_value': 10,
                'order': 1
            },
            {
                'lesson_id': lessons[2].id,
                'type': 'fill_blank',
                'question': 'Yesterday I ___ to the store.',
                'content': {
                    'correct_answer': 'went'
                },
                'points_value': 15,
                'order': 1
            }
        ]

        for exercise_data in exercises_data:
            exercise = Exercise(**exercise_data)
            db.session.add(exercise)

        db.session.flush()

        # Create sample achievements
        achievements_data = [
            {
                'name': 'First Steps',
                'description': 'Complete your first lesson',
                'badge_icon': '🎯',
                'condition_type': 'lessons_completed',
                'condition_value': 1
            },
            {
                'name': 'Week Warrior',
                'description': 'Maintain a 7-day learning streak',
                'badge_icon': '🔥',
                'condition_type': 'streak',
                'condition_value': 7
            },
            {
                'name': 'Century Club',
                'description': 'Earn 100 points',
                'badge_icon': '💯',
                'condition_type': 'points',
                'condition_value': 100
            },
            {
                'name': 'Lesson Master',
                'description': 'Complete 5 lessons',
                'badge_icon': '📚',
                'condition_type': 'lessons_completed',
                'condition_value': 5
            },
            {
                'name': 'Perfect Score',
                'description': 'Achieve 100% accuracy on a lesson',
                'badge_icon': '⭐',
                'condition_type': 'accuracy',
                'condition_value': 100
            }
        ]

        for achievement_data in achievements_data:
            achievement = Achievement(**achievement_data)
            db.session.add(achievement)

        db.session.flush()

        # Create a demo user
        demo_user = User(
            username='learner',
            email='learner@example.com',
            password_hash=generate_password_hash('password123'),
            age=12,
            native_language='spanish'
        )
        db.session.add(demo_user)
        db.session.flush()

        # Create user stats
        stats = UserStats(user_id=demo_user.id)
        db.session.add(stats)

        # Commit all changes
        db.session.commit()

        print("✅ Database seeded successfully!")
        print(f"\n📊 Created:")
        print(f"  - {len(lessons)} lessons")
        print(f"  - {len(exercises_data)} exercises")
        print(f"  - {len(achievements_data)} achievements")
        print(f"  - 1 demo user (username: learner, password: password123)")
        print("\n🚀 You can now log in with the demo user!")

if __name__ == '__main__':
    seed_database()

