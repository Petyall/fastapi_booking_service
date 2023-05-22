from datetime import date
from fastapi import APIRouter

from exceptions import HotelCannotBeFound
from hotels.services import RoomService, HotelService
from hotels.schemas import SHotelRoomsLeft, SHotel, SRoomsRoomLeft


router = APIRouter(
    prefix="/hotels",
    tags=["Отели"],
)


@router.get("/{location}")
async def get_hotels_by_location(
    location: str, date_from: date, date_to: date) -> list[SHotelRoomsLeft]:
    return await HotelService.find_hotels_by_location(location, date_from, date_to)


@router.get("/id/{hotel_id}")
async def get_hotel(hotel_id: int) -> SHotel:
    hotel = await HotelService.find_one_or_none(id=hotel_id)
    if hotel is None:
        raise HotelCannotBeFound
    return hotel


@router.get("/{hotel_id}/rooms")
async def get_all_rooms_by_hotel_id(
    hotel_id: str, data_from: date, data_to: date) -> list[SRoomsRoomLeft]:
    return await RoomService.get_available_rooms_by_hotel_id(int(hotel_id), data_from, data_to)
        