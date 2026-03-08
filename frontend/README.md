# RewardingLearning Frontend

Vite + React + Tailwind frontend for the reading-rewards app.

## Features

- HTTPS dev server for iPhone/iPad microphone access
- `/api` proxy to the FastAPI backend
- Reading page with speech capture
- Word-by-word highlight feedback for wrong, missing, and extra words
- Reward shop and admin screens

## Run locally

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on:

- `https://localhost:3000`

## Backend requirement

The frontend expects the backend on:

- `http://127.0.0.1:8001`

Because Vite proxies `/api` to the backend during development.

## MacBook / iPad / iPhone microphone setup

### On MacBook
Open:

- `https://localhost:3000`

Allow microphone access when prompted.

### On iPad / iPhone
1. Make sure the phone/tablet is on the **same Wi‑Fi network** as your Mac.
2. Start the frontend with `npm run dev`.
3. Open the **HTTPS** Vite URL from your Mac on the mobile device.
4. Accept the local certificate warning once if Safari asks.
5. Allow microphone access in Safari.

Important: iOS Safari usually blocks microphone access on plain HTTP pages, so the HTTPS dev server is required.

## Reading feedback

When speech does not match the sentence:

- **red** = wrong word
- **amber** = missing word
- **purple** = extra word

This makes it easier to see exactly what needs another try.

## Build

```bash
cd frontend
npm run build
```
