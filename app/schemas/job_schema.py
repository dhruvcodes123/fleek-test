from typing import Optional

from pydantic import BaseModel
from uuid import UUID


class GenerateImageResponse(BaseModel):
    message: str = "Image generation in progress."
    job_id: UUID

class GenerateImageRequest(BaseModel):
    prompt: str
    height: int
    width: int

class StatusResponse(BaseModel):
    status: str
    result_path: Optional[str] = None
