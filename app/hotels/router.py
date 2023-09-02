from datetime import date
from fastapi import APIRouter, Depends
from fastapi_cache.decorator import cache

from app.exceptions import HotelCannotBeFound, NotEnoughAuthorityException
from app.hotels.services import RoomService, HotelService
from app.hotels.schemas import SHotelRoomsLeft, SHotel, SRoomsRoomLeft
from app.users.dependences import get_current_user
from app.users.models import Users


router = APIRouter(
    prefix="/hotels",
    tags=["Отели"],
)


@router.get("/{location}")
# Кеширование запроса на полчаса
@cache(expire=1800)
async def get_hotels_by_location(location: str, date_from: date, date_to: date):
    """
    Поиск отеля по заданному городу и дате заезда и выезда
    """
    hotels = await HotelService.find_hotels_by_location(location, date_from, date_to)
    if not hotels:
        raise HotelCannotBeFound
    return hotels


@router.get("/id/{hotel_id}")
# Кеширование запроса на полчаса
@cache(expire=1800)
async def get_hotel(hotel_id: int) -> SHotel:
    """
    Поиск отеля по id
    """
    # Попытка поиска отеля
    hotel = await HotelService.find_one_or_none(id=hotel_id)
    # Возврат ошибки, если отель не найден
    if hotel is None:
        raise HotelCannotBeFound
    # Возврат отеля
    return hotel


@router.get("/{hotel_id}/rooms")
# Кеширование запроса на полчаса
@cache(expire=1800)
async def get_all_rooms_by_hotel_id(hotel_id: str, data_from: date, data_to: date) -> list[SRoomsRoomLeft]:
    """
    Поиск всех свободных комнат по id отеля
    """
    return await RoomService.get_available_rooms_by_hotel_id(int(hotel_id), data_from, data_to)


@router.post("/add/hotel")
async def add_hotel(name: str, location: str, services: list, rooms_quantity: int, user: Users = Depends(get_current_user)):
    """
    Добавление отеля с проверкой роли пользователя
    """
    # Проверка роли пользователя
    if user.role_id == 2:
        # Добавление нового отеля в БД
        hotel = await HotelService.add(name=name, location=location, services=services, rooms_quantity=rooms_quantity)
        return f'Отель "{name}" успешно добавлен'
    # Возврат ошибки, если пользователь не является администратором
    else:
        raise NotEnoughAuthorityException
    