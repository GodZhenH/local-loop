# Local Loop frontend (React + Vite)

## 1. Requirements
Install Node.js LTS from https://nodejs.org/ and restart VS Code afterward.

## 2. Run the frontend
Open a terminal in the `frontend` folder (the folder containing `package.json`) and run:

```bash
npm install
npm run dev
```

Open the local URL Vite prints, usually `http://localhost:5173`.

## 3. Demo mode
If no backend URL is configured, the app uses sample listings, a sample challenge, and sample leaderboard data. New listings and claims are saved in browser local storage. This lets you run and test the UI before the Flask API is ready.

## 4. Connect Flask later
Copy `.env.example` to `.env` and set `VITE_API_URL=http://127.0.0.1:5000`, matching Puvanan's actual Flask address.

The service currently expects:
- `GET /items` returning a JSON array (or `{ "items": [] }`)
- `POST /items` accepting `{ "title": "...", "category": "...", "description": "..." }`
- `POST /items/<id>/claim`
- `GET /leaderboard` returning a JSON array (or `{ "leaderboard": [] }`)
- `GET /challenge` returning `{ "category": "...", "title": "...", "reward": 20, "description": "..." }`

Agree on exact endpoint names and response formats with the backend owner. The frontend temporarily falls back to demo data when API requests fail.

## 5. Existing project
If your existing `frontend/package.json` and `frontend/src` already contain work, make a Git commit/backup first. Copy these files into the matching paths, replacing the matching files as needed. The supplied `src/pages` files match the folder structure in the screenshot.
