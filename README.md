# Failure Replay System

A small FastAPI project that simulates failed API requests, stores them in SQLite, and lets you replay or auto-retry them from a web console.

## Features
- `POST /process` to simulate success/failure and log failures
- Idempotency key handling to ignore duplicate requests
- `GET /failures` to inspect failed/successful replayed entries
- `POST /replay/{request_id}` to replay a specific failed request
- Background retry worker (`app/retry_worker.py`) that retries failed requests every 60 seconds
- Simple frontend at `/` for manual testing and monitoring

## Tech Stack
- FastAPI
- SQLAlchemy
- SQLite (`failures.db`)
- Vanilla HTML/CSS/JS frontend

## Project Structure
```text
app/
  main.py            # FastAPI app + core endpoints + static UI serving
  replay.py          # Replay endpoint
  retry_worker.py    # Background retry loop
  database.py        # SQLAlchemy engine/session
  models.py          # FailedRequest model
  static/            # UI assets (index.html, styles.css, app.js)
  requirements.txt   # Python dependencies
failures.db          # SQLite DB (created/updated at runtime)
```

## Prerequisites
- Python 3.9+ (3.10+ recommended)

## Setup
From the project root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r app/requirements.txt
```

## Run the API + UI
```bash
uvicorn app.main:app --reload
```

Open:
- Web console: `http://127.0.0.1:8000/`

## Run the Retry Worker
In a second terminal (same virtual environment):

```bash
python -m app.retry_worker
```

The worker checks for rows with:
- `status == "FAILED"`
- `retry_count < 3`

and marks them as `SUCCESS` in this demo implementation.

## API Reference

### `POST /process`
Submit payload for processing.

Request body fields:
- `idempotency_key` (optional string)
- `fail` (boolean): when `true`, simulates a failure and logs it

Responses:
- Success path: `{"message":"Processed Successfully"}`
- Duplicate idempotency key: `{"message":"Duplicate request ignored"}`
- Failure path: `{"message":"Failure logged"}`

### `GET /failures`
Returns stored requests (newest first):
- `id`
- `status`
- `retry_count`
- `idempotency_key`
- `error_message`

### `POST /replay/{request_id}`
Attempts replay of the saved request.

Responses:
- `{"message":"Replay successful"}`
- `{"message":"Replay failed"}`
- `{"message":"Request not found"}`

## Quick Test with cURL
```bash
# 1) Simulate failure
curl -X POST http://127.0.0.1:8000/process \
  -H "Content-Type: application/json" \
  -d '{"fail": true, "idempotency_key":"demo-1"}'

# 2) List failures
curl http://127.0.0.1:8000/failures

# 3) Replay ID 1
curl -X POST http://127.0.0.1:8000/replay/1
```

## Notes
- This project currently uses simulated replay/retry logic (no external API call yet).
- `payload` is stored as a string in the DB.
- If you restart with the same `failures.db`, previous records remain.
