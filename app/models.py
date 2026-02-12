from sqlalchemy import Column, Integer, String, Text
from app.database import Base

class FailedRequest(Base):
    __tablename__ = "failed_requests"

    id = Column(Integer, primary_key=True, index=True)
    endpoint = Column(String)
    payload = Column(Text)
    error_message = Column(Text)
    status = Column(String, default="FAILED")
    retry_count = Column(Integer, default=0)
    idempotency_key = Column(String, unique=True)
