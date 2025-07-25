from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.constants import UNEXPECTED_ERROR, UPDATING_STATUS, STATUS_UPDATED, GENERATION_TASK
from app.core.logging import get_logger
from app.models import Job

logger = get_logger(__name__)
async def post_job_details(db, request_data):
    """
    Create a job in the database.

    Args:
        db: The database session to use for adding the job.
        request_data: The data for the job, typically provided as a Pydantic model.

    Returns:
        The created job object after being added to the database and refreshed.
    """
    try:
        job = Job(**request_data.dict())
        db.add(job)
        await db.commit()
        return job
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def get_job_status(db: AsyncSession, job_id):
    """
        Retrieve the status and result path of a job from the database.

        Args:
            db: The database session to use for querying the job.
            job_id: The ID of the job to retrieve.

        Returns:
            A tuple containing the job's status and result path (if available).
    """
    try:
        job = await db.get(Job, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return job.status, job.result_path if job.result_path else None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))