from fastapi import APIRouter
from app.database import SessionLocal
from app.models import FailedRequest

router = APIRouter()

@router.post("/replay/{request_id}")
def replay_request(request_id: int):
    db = SessionLocal()
    request = db.query(FailedRequest).filter(
        FailedRequest.id == request_id
    ).first()

    if not request:
        return {"message": "Request not found"}

    try:
        # Simulated replay
        request.status = "SUCCESS"
        request.retry_count += 1
        db.commit()

        return {"message": "Replay successful"}

    except:
        request.retry_count += 1
        db.commit()
        return {"message": "Replay failed"}