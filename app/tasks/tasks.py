import smtplib
from pydantic import EmailStr
from PIL import Image
from pathlib import Path

from app.config import settings
from app.tasks.celery_setup import celery
from app.tasks.email_templates import create_booking_confirmation_template


@celery.task
def process_pic(path: str):
    # Переменная с путем до картинки
    im_path = Path(path)
    # Переменная для работы с картинкой
    im = Image.open(im_path)
    # Переменная с измененным форматом картинки
    im_resized = im.resize((1000, 500))
    # Сохранение картинки с изменениями и другим названием
    im_resized.save(f"app/static/images/hotels/resized_1000_500_{im_path.name}")


@celery.task
def send_booking_confirmation_email(booking: dict, email_to: EmailStr):
    # Переменная с адресом отправителя
    email_to_mock = settings.SMTP_USER # ЗАМЕНИТЬ НА ПОЛЬЗОВАТЕЛЬСКИЙ EMAIL
    # Переменная вызывающая текст для отправки письма
    msg_content = create_booking_confirmation_template(booking, email_to_mock)

    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        # Авторизация в почтовом сервере
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        # Отправка письма
        server.send_message(msg_content)
