import os

from celery import Celery
from dotenv import load_dotenv


load_dotenv()


REDIS_URL = os.getenv(
    "REDIS_URL",
    "redis://localhost:6379/0"
)


celery_app = Celery(
    "task_management",
    broker=REDIS_URL,
    backend=REDIS_URL
)


@celery_app.task
def process_background_task(message: str):

    print(
        f"Background task started: {message}"
    )

    return {
        "message": f"Processed: {message}"
    }