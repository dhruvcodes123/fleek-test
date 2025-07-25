from fastapi import FastAPI
from app.core.db import init_db
from app.api.v1.job_endpoints import router
from app.tasks.generate_task import generate_image_task
import replicate
app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "ok"}

app.include_router(router)

