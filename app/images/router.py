from fastapi import Depends, UploadFile, APIRouter
import shutil
from app.tasks.tasks import process_pic
from app.users.dependences import get_current_admin_user
from app.users.models import Users
from app.exceptions import NotEnoughAuthorityException

router = APIRouter(
    prefix="/images",
    tags=["Загрузка картинок"]
)

 
@router.post("/hotels")
async def add_hotel_image(name: int, file: UploadFile, user: Users = Depends(get_current_admin_user)):
    if user.role_id == 2:
        im_path = f"app/static/images/hotels/{name}.webp"
        with open(im_path, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)
        process_pic.delay(im_path)
        return {"filename": file.filename}
    else:
        raise NotEnoughAuthorityException
    

@router.post("/rooms")
async def add_room_image(name: int, file: UploadFile, user: Users = Depends(get_current_admin_user)):
    if user.role_id == 2:
        with open(f"app/static/images/rooms/{name}.webp", "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)
        return {"filename": file.filename}
    else:
        raise NotEnoughAuthorityException