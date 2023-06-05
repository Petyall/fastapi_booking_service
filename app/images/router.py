from shutil import copyfileobj
from fastapi import Depends, UploadFile, APIRouter

from app.tasks.tasks import process_pic
from app.users.dependences import get_current_user
from app.users.models import Users
from app.exceptions import NotEnoughAuthorityException


router = APIRouter(
    prefix="/images",
    tags=["Загрузка картинок"]
)

 
@router.post("/hotels")
async def add_hotel_image(name: int, file: UploadFile, user: Users = Depends(get_current_user)):
    # Проверка роли пользователя
    if user.role_id == 2:
        # Переменная с путем к картинке
        im_path = f"app/static/images/hotels/{name}.webp"
        # Загрузка картинки на сервер
        with open(im_path, "wb+") as file_object:
            copyfileobj(file.file, file_object)
        # Передача в celery задачи по форматированию картинки
        process_pic.delay(im_path)
        # Возврат названия картинки
        return {"filename": file.filename}
    # Возврат ошибки, если пользователь не администратор
    else:
        raise NotEnoughAuthorityException
    

@router.post("/rooms")
async def add_room_image(name: int, file: UploadFile, user: Users = Depends(get_current_user)):
    # Проверка роли пользователя
    if user.role_id == 2:
        # Загрузка картинки на сервер
        with open(f"app/static/images/rooms/{name}.webp", "wb+") as file_object:
            copyfileobj(file.file, file_object)
        # Возврат названия картинки
        return {"filename": file.filename}
    # Возврат ошибки, если пользователь не администратор
    else:
        raise NotEnoughAuthorityException
    