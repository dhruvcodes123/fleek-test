import asyncio
from celery.exceptions import MaxRetriesExceededError
from fastapi import HTTPException
from app.clients.media_client import mock_replicate_api, generate_image_from_api
from app.core.celery_app import celery_app
from app.core.constants import SUCCESS_STATUS, FAILED_STATUS
from app.core.db import AsyncSessionLocal
from app.core.logging import get_logger
from app.models.job_model import Job

logger = get_logger(__name__)


async def _generate_and_update(parameters: dict):
    job_id = parameters["job_id"]
    prompt = parameters["prompt"]
    width = parameters["width"]
    height = parameters["height"]
    retry_count = parameters["retry_count"]

    try:

        # use 'generate_image_from_api' function for replicate api call directly
        # need to pass replicate api token in .env file

        image_path = await mock_replicate_api({
            "prompt": prompt,
            "aspect_ratio": f"{width}:{height}",
            "job_id": job_id,
        })
        logger.info(f"[{job_id}] Image generated at {image_path}")

        # Update job status with explicit session and transaction
        async with AsyncSessionLocal() as session:
            async with session.begin():
                try:
                    job = await session.get(Job, job_id)
                    if not job:
                        logger.error(f"[{job_id}] Job not found")
                        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

                    job.status = SUCCESS_STATUS
                    job.retry_count = retry_count
                    job.result_path = image_path
                    await session.commit()
                    logger.info(f"[{job_id}] Status updated to {SUCCESS_STATUS}")
                except Exception as e:
                    await session.rollback()
                    logger.error(f"[{job_id}] Failed to update status: {str(e)}")
                    raise
    except Exception as e:
        logger.error(f"[{job_id}] Error in _generate_and_update: {str(e)}")
        raise


async def _fail_job(job_id: str, retry_count: int):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            try:
                job = await session.get(Job, job_id)
                if not job:
                    logger.error(f"[{job_id}] Job not found")
                    raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

                job.status = FAILED_STATUS
                job.retry_count = retry_count
                job.result_path = None
                await session.commit()
                logger.info(f"[{job_id}] Status updated to {FAILED_STATUS}")
            except Exception as e:
                await session.rollback()
                logger.error(f"[{job_id}] Failed to update status to FAILED: {str(e)}")
                raise


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={'max_retries': 5})
def generate_image_task(self, parameters: dict):
    job_id = parameters.get("job_id")
    prior_retries = self.request.retries
    logger.info(f"Received task for job: {job_id}")

    try:
        parameters["retry_count"] = prior_retries + 1
        # Get or create an event loop for the worker
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        # Run the async function in the existing event loop
        loop.run_until_complete(_generate_and_update(parameters))

    except MaxRetriesExceededError as final_exc:
        logger.error(f"Job {job_id} failed after maximum retries.")
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        loop.run_until_complete(_fail_job(job_id, self.request.retries))
        raise final_exc

    except Exception as exc:
        logger.warning(f"Temporary failure for job {job_id}: {exc}")
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)



