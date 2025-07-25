from app.repositories.job_repository import post_job_details, get_job_status
from app.schemas.job_schema import GenerateImageResponse, GenerateImageRequest, StatusResponse
from app.tasks.generate_task import generate_image_task
class JobService:
    def __init__(self,db):
        self.db = db

    async def generate_image_service(self, request_data: GenerateImageRequest):
        """
        Asynchronously generates an image based on the provided request data and stores the job details.

        Args:
            request_data (dict): A dictionary containing the prompt, height, and width for image generation.

        Returns:
            GenerateImageResponse: An object containing the job ID of the generated image task.
        """
        job = await post_job_details(self.db,request_data)
        # Call Celery task to generate the image asynchronously
        generate_image_task.delay({
            "prompt": request_data.prompt,
            "height": request_data.height,
            "width": request_data.width,
            "job_id": job.id
        })

        return GenerateImageResponse(job_id=job.id)

    async def check_status(self, job_id):
        status, result_path = await get_job_status(self.db, job_id)
        return StatusResponse(status=status, result_path=result_path)







