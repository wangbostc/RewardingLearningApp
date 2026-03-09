# English Learning App --- New Learning Modules Proposal

This document proposes **additional learning modules (activity types)**
that can be added to the current lesson engine of the English learning
app.

The goal is to: - improve engagement for kids - strengthen vocabulary,
listening, speaking, and reading skills - reuse the existing
activity-driven architecture

The modules below are designed to fit naturally into the existing
`Activity` model using:

    type
    activity_data

------------------------------------------------------------------------

# 1. Listening Command (audio_to_action)

## Goal

Train **listening comprehension** and vocabulary recognition.

## Gameplay

The child hears an instruction and taps the correct object.

Example prompt:

> "Touch the red apple"

## Example activity_data

``` json
{
  "audioUrl": "/audio/touch_red_apple.mp3",
  "objects": [
    {"id": "apple_red", "image": "/img/apple_red.png"},
    {"id": "apple_green", "image": "/img/apple_green.png"},
    {"id": "banana", "image": "/img/banana.png"}
  ],
  "answer": "apple_red"
}
```

------------------------------------------------------------------------

# 2. Phonics Word Builder (phonics_build_word)

## Goal

Teach spelling and phonics.

## Gameplay

The child sees a picture and drags letters to build the correct word.

Example:

Picture: **cat**

Letters available:

    C A T B D

Correct answer:

    CAT

## Example activity_data

``` json
{
  "image": "/img/cat.png",
  "letters": ["C","A","T","B","D"],
  "answer": "CAT"
}
```

------------------------------------------------------------------------

# 3. Speak Sentence (speak_sentence)

## Goal

Encourage speaking practice and pronunciation.

## Gameplay

The app shows a sentence and plays reference audio.

The child records themselves speaking.

Example sentence:

    I see a cat

## Example activity_data

``` json
{
  "sentence": "I see a cat",
  "audio_reference": "/audio/i_see_a_cat.mp3"
}
```

Future improvements:

-   pronunciation scoring
-   word-by-word highlighting
-   speech similarity scoring

------------------------------------------------------------------------

# 4. Story Listening (story_listen)

## Goal

Teach comprehension through short illustrated stories.

Kids naturally learn language better through stories than isolated
words.

Example story:

    This is a cat.
    The cat is sleeping.
    The dog is barking.

Each story can be followed by questions.

## Example activity_data

``` json
{
  "pages": [
    {
      "image": "/img/story_cat_sleeping.png",
      "text": "This is a cat."
    },
    {
      "image": "/img/story_cat_sleeping2.png",
      "text": "The cat is sleeping."
    }
  ],
  "audio": "/audio/story_cat.mp3"
}
```

------------------------------------------------------------------------

# 5. Story Question (story_question)

## Goal

Test comprehension after a story.

Example question:

    Who is sleeping?

Options:

    cat
    dog
    bird

## Example activity_data

``` json
{
  "question": "Who is sleeping?",
  "options": ["cat","dog","bird"],
  "answer": "cat"
}
```

------------------------------------------------------------------------

# 6. Memory Match Game (memory_match)

## Goal

Reinforce vocabulary recall.

## Gameplay

Cards are flipped to match:

    word ↔ picture

Example matches:

    cat ↔ 🐱
    dog ↔ 🐶

## Example activity_data

``` json
{
  "pairs": [
    {"word": "cat", "image": "/img/cat.png"},
    {"word": "dog", "image": "/img/dog.png"}
  ]
}
```

------------------------------------------------------------------------

# 7. Listen and Type (listen_and_type)

## Goal

Train listening and spelling simultaneously.

## Gameplay

The child hears audio and types or selects the sentence.

Example audio:

    I see a dog

## Example activity_data

``` json
{
  "audio": "/audio/i_see_a_dog.mp3",
  "answer": "I see a dog"
}
```

------------------------------------------------------------------------

# 8. Sentence Builder (sentence_builder)

## Goal

Teach sentence structure.

## Gameplay

The child arranges words into the correct order.

Example words:

    see / I / cat / a

Correct answer:

    I see a cat

## Example activity_data

``` json
{
  "words": ["see","I","cat","a"],
  "answer": ["I","see","a","cat"]
}
```

------------------------------------------------------------------------

# 9. Role Play Dialogue (role_play)

## Goal

Practice conversational English.

## Gameplay

Simple dialogue interaction with the app.

Example:

    App: Hello!
    Child: Hello!

    App: How are you?
    Child: I am fine.

## Example activity_data

``` json
{
  "dialogue": [
    {"speaker": "app", "text": "Hello!"},
    {"speaker": "child", "expected": "Hello!"},
    {"speaker": "app", "text": "How are you?"},
    {"speaker": "child", "expected": "I am fine."}
  ]
}
```

------------------------------------------------------------------------

# 10. Picture Description (describe_picture)

## Goal

Encourage free speaking.

## Gameplay

Show a scene and ask the child to describe it.

Example prompt:

> "What is happening in this picture?"

Example picture:

    A boy eating an apple.

## Example activity_data

``` json
{
  "image": "/img/boy_eating_apple.png",
  "prompt": "What is happening in the picture?"
}
```

------------------------------------------------------------------------

# 11. Daily Practice Mode

Create a daily routine for kids.

Example structure:

    Daily Practice
      1 listening activity
      1 speaking activity
      1 vocabulary activity

Total time: **5 minutes**.

This helps build consistent learning habits.

------------------------------------------------------------------------

# 12. Reward System

Kids respond well to rewards.

Examples:

-   stars
-   stickers
-   coins
-   unlockable animals
-   avatars

Example reward rule:

    Finish lesson → earn 3 stars
    Collect 10 stars → unlock new sticker

------------------------------------------------------------------------

# 13. Adaptive Review

Use attempt history to review difficult words.

Example rule:

    if accuracy < 60%
        schedule review lesson

This improves long-term retention.

------------------------------------------------------------------------

# 14. Recommended Next Modules

If prioritizing development, implement these first:

1.  phonics_build_word
2.  story_listen
3.  audio_to_action
4.  memory_match
5.  role_play

These provide the best balance of:

-   engagement
-   educational value
-   development complexity.

------------------------------------------------------------------------

# 15. Long-Term Advanced Feature

## AI Story Generator

Allow parents to generate custom stories.

Example input:

    Topic: animals
    Level: beginner
    Length: short

The system generates:

-   a story
-   images
-   comprehension questions
-   speaking practice

This enables unlimited learning content.
