# Deployment Guide

## Local Run

1. Place the dataset files in:
   - `data/raw/train.csv`
   - `data/raw/test.csv`

2. Train the model:

```bash
python backend/train.py
```

3. Start the API:

```bash
uvicorn backend.app.main:app --reload --port 8000
```

4. Start the frontend:

```bash
npm install
npm run dev
```

## Notes

- The backend caches the model bundle in memory at startup.
- The prediction endpoint writes `outputs/latest_submission.csv` and serves it from `/download-submission`.
- For demos, keep the dataset local so the UI can upload and score files instantly.

