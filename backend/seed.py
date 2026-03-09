#!/usr/bin/env python3
"""
Seed script to populate the database with:
- Australian Year 1 reading sentences (based on M100W sight words and decodable patterns)
- Sample reward shop items
- Demo users (kid + admin)
- Achievements

Run: cd backend && uv run python seed.py
"""

from app import engine, SessionLocal
from app.models import (
    Base,
    User,
    UserStats,
    Lesson,
    Achievement,
    ReadingSentence,
    RewardItem,
    LearningPath,
    LearningUnit,
    EngineLesson,
    LearningActivity,
)
from werkzeug.security import generate_password_hash


def seed_database():
    """Populate database with sample data."""
    # Create tables
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        print("🌱 Seeding database...")

        # ==================== LESSONS (Reading themes) ====================
        lessons_data = [
            {
                "title": "My First Words",
                "description": "Simple sight word sentences with 2-3 words",
                "difficulty": "beginner",
                "category": "sight_words",
                "estimated_duration": 5,
                "order": 1,
            },
            {
                "title": "I Can See",
                "description": "Sentences using 'I can see' pattern",
                "difficulty": "beginner",
                "category": "sight_words",
                "estimated_duration": 5,
                "order": 2,
            },
            {
                "title": "Animals Around Us",
                "description": "Read about common animals",
                "difficulty": "beginner",
                "category": "decodable",
                "estimated_duration": 5,
                "order": 3,
            },
            {
                "title": "At Home",
                "description": "Sentences about things at home",
                "difficulty": "beginner",
                "category": "sight_words",
                "estimated_duration": 5,
                "order": 4,
            },
            {
                "title": "My Family",
                "description": "Read about family members",
                "difficulty": "beginner",
                "category": "sight_words",
                "estimated_duration": 5,
                "order": 5,
            },
            {
                "title": "Fun at the Park",
                "description": "Sentences about playing at the park",
                "difficulty": "elementary",
                "category": "decodable",
                "estimated_duration": 8,
                "order": 6,
            },
            {
                "title": "Food I Like",
                "description": "Talk about favourite foods",
                "difficulty": "elementary",
                "category": "decodable",
                "estimated_duration": 8,
                "order": 7,
            },
            {
                "title": "At School",
                "description": "Sentences about school life",
                "difficulty": "elementary",
                "category": "sight_words",
                "estimated_duration": 8,
                "order": 8,
            },
            {
                "title": "Colours and Shapes",
                "description": "Describe colours and shapes around us",
                "difficulty": "elementary",
                "category": "decodable",
                "estimated_duration": 8,
                "order": 9,
            },
            {
                "title": "Weather and Seasons",
                "description": "Read about weather and seasons in Australia",
                "difficulty": "intermediate",
                "category": "short_story",
                "estimated_duration": 10,
                "order": 10,
            },
            {
                "title": "Little Stories",
                "description": "Short two-sentence stories to read aloud",
                "difficulty": "intermediate",
                "category": "short_story",
                "estimated_duration": 10,
                "order": 11,
            },
            {
                "title": "Australian Animals",
                "description": "Read about uniquely Australian animals",
                "difficulty": "intermediate",
                "category": "short_story",
                "estimated_duration": 10,
                "order": 12,
            },
        ]

        lessons = []
        for data in lessons_data:
            lesson = Lesson(**data)
            db.add(lesson)
            lessons.append(lesson)
        db.flush()

        # ==================== GENERIC LESSON ENGINE STARTER PACK ====================
        starter_path = LearningPath(
            name="Vocabulary Basics",
            description="Starter path for the new generic lesson engine.",
            order_index=1,
        )
        db.add(starter_path)
        db.flush()

        starter_unit = LearningUnit(
            path_id=starter_path.id,
            name="Animals",
            order_index=1,
        )
        db.add(starter_unit)
        db.flush()

        starter_lesson = EngineLesson(
            unit_id=starter_unit.id,
            title="Animals 1",
            level="beginner",
            order_index=1,
            estimated_minutes=5,
        )
        db.add(starter_lesson)
        db.flush()

        starter_activities = [
            LearningActivity(
                lesson_id=starter_lesson.id,
                type="audio_to_picture",
                prompt="Tap the cat",
                instructions="Listen carefully, then choose the matching picture.",
                activity_data={
                    "audioUrl": "/audio/cat.mp3",
                    "options": [
                        {"id": "cat", "image": "/img/cat.png"},
                        {"id": "dog", "image": "/img/dog.png"},
                    ],
                    "answer": "cat",
                },
                order_index=1,
                points=10,
            ),
            LearningActivity(
                lesson_id=starter_lesson.id,
                type="word_to_picture",
                prompt="Find the bird",
                instructions="Read the word and tap the right picture.",
                activity_data={
                    "word": "bird",
                    "options": [
                        {"id": "bird", "image": "/img/bird.png"},
                        {"id": "fish", "image": "/img/fish.png"},
                    ],
                    "answer": "bird",
                },
                order_index=2,
                points=10,
            ),
            LearningActivity(
                lesson_id=starter_lesson.id,
                type="sentence_order",
                prompt="Put the sentence in order",
                instructions="Drag the words to make a sentence.",
                activity_data={
                    "tokens": ["I", "see", "a", "cat"],
                    "answer": ["I", "see", "a", "cat"],
                },
                order_index=3,
                points=15,
            ),
        ]
        db.add_all(starter_activities)

        # ==================== READING SENTENCES ====================
        # Based on Australian M100W (Magic 100 Words) and Year 1 decodable patterns
        # Grouped by lesson, ordered by difficulty within each lesson

        sentences_by_lesson = {
            # Lesson 1: My First Words (Level 1 — 2-4 word sentences)
            0: [
                ("I am here.", "sight_words", 1, 5),
                ("Look at me.", "sight_words", 1, 5),
                ("I can go.", "sight_words", 1, 5),
                ("Come and look.", "sight_words", 1, 5),
                ("I am big.", "sight_words", 1, 5),
                ("It is red.", "sight_words", 1, 5),
                ("Go up here.", "sight_words", 1, 5),
                ("I like it.", "sight_words", 1, 5),
                ("We are here.", "sight_words", 1, 5),
                ("Is it in?", "sight_words", 1, 5),
            ],
            # Lesson 2: I Can See (Level 1)
            1: [
                ("I can see a cat.", "sight_words", 1, 10),
                ("I can see a dog.", "sight_words", 1, 10),
                ("I can see the sun.", "sight_words", 1, 10),
                ("I can see a bird.", "sight_words", 1, 10),
                ("I can see my mum.", "sight_words", 1, 10),
                ("I can see the tree.", "sight_words", 1, 10),
                ("I can see a fish.", "sight_words", 1, 10),
                ("I can see two eggs.", "sight_words", 1, 10),
                ("I can see the moon.", "sight_words", 1, 10),
                ("I can see my dad.", "sight_words", 1, 10),
            ],
            # Lesson 3: Animals Around Us (Level 1-2)
            2: [
                ("The cat sat on the mat.", "decodable", 1, 10),
                ("The dog can run fast.", "decodable", 1, 10),
                ("A big hen is in the pen.", "decodable", 2, 10),
                ("The fat pig can dig.", "decodable", 2, 10),
                ("A red fox ran and hid.", "decodable", 2, 10),
                ("The frog can hop on a log.", "decodable", 2, 10),
                ("My pet rat is on my lap.", "decodable", 2, 10),
                ("The duck can swim in the dam.", "decodable", 2, 10),
                ("A bat can fly at night.", "decodable", 2, 10),
                ("The ant is very small.", "decodable", 2, 10),
            ],
            # Lesson 4: At Home (Level 1-2)
            3: [
                ("This is my home.", "sight_words", 1, 10),
                ("I sit on my bed.", "sight_words", 1, 10),
                ("The cup is on the table.", "sight_words", 2, 10),
                ("I can see the door.", "sight_words", 1, 10),
                ("Mum is in the kitchen.", "sight_words", 2, 10),
                ("My room has a window.", "sight_words", 2, 10),
                ("The book is on the shelf.", "sight_words", 2, 10),
                ("We eat at the table.", "sight_words", 2, 10),
                ("I play in the garden.", "sight_words", 2, 10),
                ("Dad is at the door.", "sight_words", 2, 10),
            ],
            # Lesson 5: My Family (Level 2)
            4: [
                ("I love my mum and dad.", "sight_words", 2, 10),
                ("My sister is little.", "sight_words", 2, 10),
                ("My brother can run fast.", "sight_words", 2, 10),
                ("We like to play together.", "sight_words", 2, 10),
                ("Grandma reads me a book.", "sight_words", 2, 10),
                ("Grandpa has a big hat.", "sight_words", 2, 10),
                ("My family is the best.", "sight_words", 2, 10),
                ("We go to the park.", "sight_words", 2, 10),
                ("I help my mum cook.", "sight_words", 2, 10),
                ("Dad and I play ball.", "sight_words", 2, 10),
            ],
            # Lesson 6: Fun at the Park (Level 2-3)
            5: [
                ("I like to go on the slide.", "decodable", 2, 15),
                ("We play on the swings.", "decodable", 2, 15),
                ("I can run very fast.", "decodable", 2, 15),
                ("The ball went over the fence.", "decodable", 3, 15),
                ("We had a picnic on the grass.", "decodable", 3, 15),
                ("I like to climb the big tree.", "decodable", 3, 15),
                ("My friend and I play tag.", "decodable", 2, 15),
                ("The park has lots of flowers.", "decodable", 3, 15),
                ("We ride our bikes to the park.", "decodable", 3, 15),
                ("I kick the ball to my friend.", "decodable", 3, 15),
            ],
            # Lesson 7: Food I Like (Level 2-3)
            6: [
                ("I like to eat apples.", "decodable", 2, 15),
                ("Mum made me a sandwich.", "decodable", 2, 15),
                ("I drink milk every day.", "decodable", 2, 15),
                ("We have rice for dinner.", "decodable", 2, 15),
                ("I love cake and ice cream.", "decodable", 3, 15),
                ("The banana is yellow.", "decodable", 2, 15),
                ("Can I have some water please?", "decodable", 3, 15),
                ("We eat fruit at school.", "decodable", 2, 15),
                ("Dad makes eggs for breakfast.", "decodable", 3, 15),
                ("I had a jam sandwich for lunch.", "decodable", 3, 15),
            ],
            # Lesson 8: At School (Level 2-3)
            7: [
                ("I go to school every day.", "sight_words", 2, 15),
                ("My teacher is very kind.", "sight_words", 2, 15),
                ("We read books in class.", "sight_words", 2, 15),
                ("I like to draw and paint.", "sight_words", 3, 15),
                ("We play games at lunch time.", "sight_words", 3, 15),
                ("My best friend sits next to me.", "sight_words", 3, 15),
                ("I write my name on the page.", "sight_words", 3, 15),
                ("We sing songs in the morning.", "sight_words", 3, 15),
                ("The classroom has lots of books.", "sight_words", 3, 15),
                ("I put my bag on the hook.", "sight_words", 3, 15),
            ],
            # Lesson 9: Colours and Shapes (Level 2-3)
            8: [
                ("The sky is blue today.", "decodable", 2, 15),
                ("I have a red ball.", "decodable", 2, 15),
                ("The grass is very green.", "decodable", 2, 15),
                ("My hat is yellow and white.", "decodable", 3, 15),
                ("A circle is round like the sun.", "decodable", 3, 15),
                ("The box has four sides.", "decodable", 3, 15),
                ("I drew a big orange star.", "decodable", 3, 15),
                ("The purple flower is pretty.", "decodable", 3, 15),
                ("A triangle has three sides.", "decodable", 3, 15),
                ("I painted a rainbow with all the colours.", "decodable", 3, 15),
            ],
            # Lesson 10: Weather and Seasons (Level 3-4)
            9: [
                ("The sun is shining today.", "short_story", 3, 20),
                ("It is raining outside.", "short_story", 3, 20),
                ("The wind is blowing the leaves.", "short_story", 3, 20),
                ("In summer we go to the beach.", "short_story", 3, 20),
                ("Winter is cold and we wear jumpers.", "short_story", 4, 20),
                ("In autumn the leaves fall down.", "short_story", 3, 20),
                ("Spring has lots of pretty flowers.", "short_story", 4, 20),
                ("I like to splash in the puddles.", "short_story", 3, 20),
                ("We need an umbrella when it rains.", "short_story", 4, 20),
                ("The clouds are big and white.", "short_story", 3, 20),
            ],
            # Lesson 11: Little Stories (Level 3-4)
            10: [
                (
                    "The little bird sat in the tree. It sang a pretty song.",
                    "short_story",
                    3,
                    20,
                ),
                (
                    "I went to the shops with mum. We got bread and milk.",
                    "short_story",
                    4,
                    20,
                ),
                (
                    "My dog likes to dig holes. He gets very dirty.",
                    "short_story",
                    4,
                    20,
                ),
                (
                    "We went to the beach last week. I made a sand castle.",
                    "short_story",
                    4,
                    20,
                ),
                (
                    "I found a shell at the beach. It was pink and white.",
                    "short_story",
                    4,
                    20,
                ),
                (
                    "The baby is sleeping now. We must be very quiet.",
                    "short_story",
                    4,
                    20,
                ),
                (
                    "I got a new book today. It has lots of pictures.",
                    "short_story",
                    4,
                    20,
                ),
                (
                    "We planted seeds in the garden. They will grow into flowers.",
                    "short_story",
                    4,
                    20,
                ),
            ],
            # Lesson 12: Australian Animals (Level 3-5)
            11: [
                ("A kangaroo can hop very far.", "short_story", 3, 20),
                ("The koala sleeps in the gum tree.", "short_story", 3, 20),
                ("A platypus lives near the river.", "short_story", 4, 20),
                ("The wombat digs a big burrow.", "short_story", 4, 20),
                ("Kookaburras laugh in the morning.", "short_story", 4, 20),
                ("An emu is a very big bird that cannot fly.", "short_story", 5, 20),
                ("The echidna has sharp spines on its back.", "short_story", 5, 20),
                ("A baby kangaroo lives in its mum's pouch.", "short_story", 5, 20),
                ("We saw a lizard on the rock at the park.", "short_story", 4, 20),
                (
                    "The cockatoo has white feathers and a yellow crest.",
                    "short_story",
                    5,
                    20,
                ),
            ],
        }

        sentence_count = 0
        for lesson_idx, sentences in sentences_by_lesson.items():
            for order, (text, category, difficulty, points) in enumerate(sentences, 1):
                sentence = ReadingSentence(
                    lesson_id=lessons[lesson_idx].id,
                    text=text,
                    difficulty_level=difficulty,
                    category=category,
                    points_value=points,
                    order=order,
                )
                db.add(sentence)
                sentence_count += 1

        db.flush()

        # ==================== ACHIEVEMENTS ====================
        achievements_data = [
            {
                "name": "First Words",
                "description": "Read your first sentence correctly",
                "badge_icon": "⭐",
                "condition_type": "lessons_completed",
                "condition_value": 1,
            },
            {
                "name": "Bookworm",
                "description": "Complete 5 lessons",
                "badge_icon": "📚",
                "condition_type": "lessons_completed",
                "condition_value": 5,
            },
            {
                "name": "Super Reader",
                "description": "Complete 10 lessons",
                "badge_icon": "🦸",
                "condition_type": "lessons_completed",
                "condition_value": 10,
            },
            {
                "name": "Point Collector",
                "description": "Earn 100 points",
                "badge_icon": "💰",
                "condition_type": "points",
                "condition_value": 100,
            },
            {
                "name": "Star Student",
                "description": "Earn 500 points",
                "badge_icon": "🌟",
                "condition_type": "points",
                "condition_value": 500,
            },
            {
                "name": "Reading Champion",
                "description": "Earn 1000 points",
                "badge_icon": "🏆",
                "condition_type": "points",
                "condition_value": 1000,
            },
            {
                "name": "Week Warrior",
                "description": "Read every day for a week",
                "badge_icon": "🔥",
                "condition_type": "streak",
                "condition_value": 7,
            },
            {
                "name": "Sharp Shooter",
                "description": "Get 100% accuracy on a lesson",
                "badge_icon": "🎯",
                "condition_type": "accuracy",
                "condition_value": 100,
            },
        ]

        for data in achievements_data:
            db.add(Achievement(**data))
        db.flush()

        # ==================== REWARD SHOP ITEMS ====================
        shop_items = [
            {
                "name": "Extra Screen Time (15 min)",
                "description": "Earn 15 minutes of extra iPad or TV time",
                "emoji": "📱",
                "points_cost": 50,
                "stock": None,
                "is_active": True,
            },
            {
                "name": "Choose Tonight's Dinner",
                "description": "You get to pick what the family eats for dinner!",
                "emoji": "🍕",
                "points_cost": 100,
                "stock": None,
                "is_active": True,
            },
            {
                "name": "Sticker Pack",
                "description": "A pack of shiny stickers from the sticker box",
                "emoji": "⭐",
                "points_cost": 30,
                "stock": None,
                "is_active": True,
            },
            {
                "name": "Trip to the Playground",
                "description": "A special trip to your favourite playground",
                "emoji": "🎢",
                "points_cost": 150,
                "stock": None,
                "is_active": True,
            },
            {
                "name": "New Book",
                "description": "Choose a new book from the bookshop",
                "emoji": "📖",
                "points_cost": 200,
                "stock": None,
                "is_active": True,
            },
            {
                "name": "Movie Night Pick",
                "description": "Choose the movie for family movie night",
                "emoji": "🎬",
                "points_cost": 120,
                "stock": None,
                "is_active": True,
            },
            {
                "name": "Ice Cream Treat",
                "description": "A special ice cream from the shop",
                "emoji": "🍦",
                "points_cost": 80,
                "stock": None,
                "is_active": True,
            },
            {
                "name": "Stay Up Late (30 min)",
                "description": "Stay up 30 minutes past bedtime on a weekend",
                "emoji": "🌙",
                "points_cost": 100,
                "stock": None,
                "is_active": True,
            },
            {
                "name": "Arts & Craft Supplies",
                "description": "New colouring pencils or craft supplies",
                "emoji": "🎨",
                "points_cost": 180,
                "stock": None,
                "is_active": True,
            },
            {
                "name": "Toy Shop Visit",
                "description": "Pick a small toy from the toy shop",
                "emoji": "🧸",
                "points_cost": 500,
                "stock": None,
                "is_active": True,
            },
        ]

        for data in shop_items:
            db.add(RewardItem(**data))
        db.flush()

        # ==================== USERS ====================
        # Admin user (parent)
        admin_user = User(
            username="admin",
            email="admin@example.com",
            password_hash=generate_password_hash("admin123"),
            is_admin=True,
            age=30,
            native_language="english",
        )
        db.add(admin_user)
        db.flush()
        db.add(UserStats(user_id=admin_user.id))

        # Kid user
        kid_user = User(
            username="emma",
            email="emma@example.com",
            password_hash=generate_password_hash("emma123"),
            is_admin=False,
            age=6,
            native_language="english",
        )
        db.add(kid_user)
        db.flush()
        db.add(UserStats(user_id=kid_user.id))

        # Commit all changes
        db.commit()

        print("✅ Database seeded successfully!")
        print(f"\n📊 Created:")
        print(f"  - {len(lessons)} reading lessons")
        print(f"  - {sentence_count} reading sentences")
        print(f"  - {len(achievements_data)} achievements")
        print(f"  - {len(shop_items)} reward shop items")
        print(f"  - 2 users:")
        print(f"    • admin (password: admin123) — parent/admin account")
        print(f"    • emma  (password: emma123)  — kid account")
        print("\n🚀 Ready to go!")

    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        import traceback

        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
