from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.db import get_db
from app.schemas.job_schema import GenerateImageResponse, GenerateImageRequest
from app.services.job_service import JobService

router = APIRouter(
    prefix="/api/v1"
)

@router.post("/generate/", response_model=GenerateImageResponse)
async def generate_image(
        request_data:GenerateImageRequest  ,
        db: AsyncSession = Depends(get_db)):
    """
        Endpoint to generate an image based on the provided request data.

        Args:
            request_data: The data required to generate the image.
            db: The database session dependency.

        Returns:
            The generated image response.
        """
    job_service = JobService(db=db)
    return await job_service.generate_image_service(request_data=request_data)

@router.get("/status/{job_id}")
async def check_status(job_id:str,
                       db: AsyncSession = Depends(get_db)):
    """ Endpoint to check the status of the application."""
    job_service = JobService(db=db)
    return await job_service.check_status(job_id=job_id)