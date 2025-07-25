from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
import uuid

class Job(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    prompt: str
    status: str = Field(default="queued")
    result_path: Optional[str] = None
    retry_count: int = 0
    width: Optional[int]
    height: Optional[int]
    created_at: datetime = Field(default_factory=datetime.utcnow)
