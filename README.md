# fastapi_stepik

celery -A app.tasks.celery_setup:celery worker --loglevel=INFO --pool=solo
celery -A app.tasks.celery_setup:celery flower