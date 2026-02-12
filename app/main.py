import uuid
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.database import engine, SessionLocal
from app.models import Base, FailedRequest
from app.replay import router as replay_router

Base.metadata.create_all(bind=engine)

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Failure Replay Console")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
app.include_router(replay_router)


@app.get("/")
def serve_ui():
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.get("/failures")
def list_failures():
    db = SessionLocal()
    try:
        failures = db.query(FailedRequest).order_by(FailedRequest.id.desc()).all()
        return [
            {
                "id": item.id,
                "status": item.status,
                "retry_count": item.retry_count,
                "idempotency_key": item.idempotency_key,
                "error_message": item.error_message,
            }
            for item in failures
        ]
    finally:
        db.close()


@app.post("/process")
def process_request(data: dict):
    db = SessionLocal()
    try:
        idempotency_key = data.get("idempotency_key", str(uuid.uuid4()))

        existing = db.query(FailedRequest).filter(
            FailedRequest.idempotency_key == idempotency_key
        ).first()

        if existing:
            return {"message": "Duplicate request ignored"}

        if data.get("fail") is True:
            raise Exception("Simulated API Failure")

        return {"message": "Processed Successfully"}
    except Exception as e:
        failure = FailedRequest(
            endpoint="/process",
            payload=str(data),
            error_message=str(e),
            status="FAILED",
            idempotency_key=idempotency_key,
        )
        db.add(failure)
        db.commit()
        return {"message": "Failure logged"}
    finally:
        db.close()
