import asyncio
from datetime import date
from fastapi import APIRouter, Depends

from app.exceptions import HotelCannotBeFound, NotEnoughAuthorityException
from app.hotels.services import RoomService, HotelService
from app.hotels.schemas import SHotelRoomsLeft, SHotel, SRoomsRoomLeft
from fastapi_cache.decorator import cache

from app.users.dependences import get_current_user
from app.users.models import Users

router = APIRouter(
    prefix="/hotels",
    tags=["Отели"],
)


@router.get("/{location}")
@cache(expire=1800)
async def get_hotels_by_location(location: str, date_from: date, date_to: date) -> list[SHotelRoomsLeft]:
    """
    Поиск отеля по заданному городу и дате заезда и выезда
    """
    return await HotelService.find_hotels_by_location(location, date_from, date_to)


@router.get("/id/{hotel_id}")
@cache(expire=1800)
async def get_hotel(hotel_id: int) -> SHotel:
    """
    Поиск отеля по id
    """
    hotel = await HotelService.find_one_or_none(id=hotel_id)
    if hotel is None:
        raise HotelCannotBeFound
    return hotel


@router.get("/{hotel_id}/rooms")
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
    if user.role_id == 2:
        hotel = await HotelService.add(name=name, location=location, services=services, rooms_quantity=rooms_quantity)
        return f'Отель "{name}" успешно добавлен'
    else:
        raise NotEnoughAuthorityException