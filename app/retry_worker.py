import time
from app.database import SessionLocal
from app.models import FailedRequest

def retry_failed():
    db = SessionLocal()

    failures = db.query(FailedRequest).filter(
        FailedRequest.status == "FAILED",
        FailedRequest.retry_count < 3
    ).all()

    for req in failures:
        print(f"Retrying request {req.id}")

        try:
            # Simulated retry success
            req.status = "SUCCESS"
            req.retry_count += 1
            db.commit()

        except:
            req.retry_count += 1
            db.commit()

while True:
    retry_failed()
    time.sleep(60)