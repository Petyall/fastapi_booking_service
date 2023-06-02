from celery import Celery
from app.config import settings

celery = Celery(
    "tasks",
    # broker="redis://localhost:6379",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
    include=["app.tasks.tasks"]
)
