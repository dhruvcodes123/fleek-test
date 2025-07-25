import asyncio
import os
from io import BytesIO
from pathlib import Path
import aiofiles
import httpx
from PIL import Image
import replicate
from app.core.config import settings
from app.core.constants import IMAGE_GENERATION_IN_PROGRESS, IMAGE_GENERATED_SUCCESSFULLY, IMAGE_GENERATION_FAILED
from app.core.logging import get_logger

logger = get_logger(__name__)

async def generate_image_from_api(prompt_input: dict):
    """
    Generates an image using the Replicate API based on the provided prompt input.

    Args:
        prompt_input (dict): The input parameters for the image generation API.

    """
    await asyncio.sleep(2)
    logger.info(IMAGE_GENERATION_IN_PROGRESS)
    job_id = prompt_input.get("job_id")

    replicate_client = replicate.Client(api_token=settings.REPLICATE_API_TOKEN)
    output = replicate_client.run(
        "black-forest-labs/flux-schnell",
        input=prompt_input
    )

    img_url = output[0] if isinstance(output[0], list) else output
    image_path = await download_and_save_image(img_url, f"img_{job_id}")
    logger.info(IMAGE_GENERATED_SUCCESSFULLY)
    return str(image_path)

async def mock_replicate_api(parameter_dict: dict) -> str:
    """
    Simulates an async API call to Replicate and returns a mock image URL.

    Args:
        parameter_dict (dict): The input parameters for the mock API call.

    Returns:
        str: The URL of the mock image.
    """
    await asyncio.sleep(2)  # simulate latency
    logger.info(IMAGE_GENERATION_IN_PROGRESS)
    job_id = parameter_dict.get("job_id")

    img_url = settings.DUMMY_IMAGE_URL
    image_path = await download_and_save_image(img_url, f"img_{job_id}")
    logger.info(IMAGE_GENERATED_SUCCESSFULLY)
    return str(image_path)



async def download_and_save_image(img_url: str, filename: str):
    """
        Save a Pillow image asynchronously to a file.

        Args:
            img: The Pillow Image object to be saved.
            filename: The name of the file where the image will be saved.
    """
    try:
        output_dir = "generated_images"
        os.makedirs(output_dir, exist_ok=True)

        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; CeleryMockBot/1.0)"
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(img_url, headers=headers)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content))

            if img.mode != "RGB":
                img = img.convert("RGB")
            buffer = BytesIO()
            img.save(buffer, format='JPEG')
            buffer.seek(0)

            # Full path to save the image
            full_path = Path(output_dir) / f"{filename}.jpg"

            async with aiofiles.open(full_path, "wb") as f:
                await f.write(buffer.getbuffer())
            return full_path

    except Exception as e:
        logger.error(IMAGE_GENERATION_FAILED.format(e))

