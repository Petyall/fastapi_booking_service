from fastapi import UploadFile, APIRouter
import shutil

router = APIRouter(
    prefix="/images",
    tags=["Загрузка картинок"]
)


@router.post("/hotels")
async def add_hotel_image(name: int, file: UploadFile):
    with open(f"static/images/hotels/{name}.webp", "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
    return {"filename": file.filename}

@router.post("/rooms")
async def add_room_image(name: int, file: UploadFile):
    with open(f"static/images/rooms/{name}.webp", "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
    return {"filename": file.filename}