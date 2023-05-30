from app.tasks.celery_setup import celery
from PIL import Image
from pathlib import Path

@celery.task
def process_pic(path: str):
    im_path = Path(path)
    im = Image.open(im_path)
    im_resized = im.resize((1000, 500))
    im_resized.save(f"static/images/rezized_1000_500_/{im_path.name}")