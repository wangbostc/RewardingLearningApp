# RewardingLearning Backend

FastAPI backend for the reading-rewards app.

## Run locally

```bash
cd backend
uv sync
uv run python main.py
```

Backend runs on:

- `http://localhost:8001`
- docs: `http://localhost:8001/docs`

## Seed the database

```bash
cd backend
uv run python seed.py
```

This creates:

- lessons
- reading sentences
- reward shop items
- sample users

## Sample users

- admin: `admin` / `admin123`
- kid: `emma` / `emma123`

## Test the speech feedback logic

```bash
cd backend
uv run pytest tests/test_speech_feedback.py
```

## Notes

`/api/speech/check` now returns token-level comparison feedback so the frontend can highlight:

- wrong words
- missing words
- extra words

