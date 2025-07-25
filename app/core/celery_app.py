from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "media_generator",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.task_routes = {
    "app.tasks.*": {"queue": "default"},
}

# Add this to ensure task discovery - use the exact module path
celery_app.conf.imports = (
    'app.tasks.generate_task',  # This matches your actual task module path
)

