import json
from shutil import copyfileobj
from fastapi import APIRouter, Depends, UploadFile
from datetime import datetime

from app.exceptions import NotEnoughAuthorityException, TableNotFound, ParserError
from app.hotels.services import HotelService, RoomService
from app.users.dependences import get_current_user
from app.users.models import Users


router = APIRouter(
    prefix="/importer",
    tags=["Загрузка данных"],
)


@router.post("")
async def get_data_from_json(table_name: str, file: UploadFile, user: Users = Depends(get_current_user)):
    if user.role_id != 2:
        raise NotEnoughAuthorityException

    file_path = f"app/static/json/{table_name} - {datetime.utcnow().strftime('%Y%m%d%H%M%S')}.json"
    with open(file_path, "wb+") as file_object:
        copyfileobj(file.file, file_object)
    try:
        with open(file_path, 'r', encoding='utf-8') as json_file:
            parsed_data = json.load(json_file)

            if table_name == "hotels":
                for obj in parsed_data.get(table_name, []):
                    details = {
                        'name': obj.get('name'),
                        'location': obj.get('location'),
                        'services': obj.get('services'),
                        'rooms_quantity': int(obj.get('rooms_quantity'))
                    }
                    await HotelService.add(**details)
                        
            elif table_name == "rooms":
                for obj in parsed_data.get(table_name, []):
                    details = {
                        'hotel_id': int(obj.get('hotel_id')),
                        'name': obj.get('name'),
                        'description': obj.get('description'),
                        'price': int(obj.get('price')),
                        'services': obj.get('services'),
                        'quantity': int(obj.get('quantity'))
                    }
                    await RoomService.add(**details)
            
            else:
                raise TableNotFound
    except:
        raise ParserError

    return 'В таблицу {table_name} были успешно добавлены данные'
