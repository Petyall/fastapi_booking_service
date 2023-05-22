from datetime import date
from sqlalchemy import func

from hotels.schemas import SRoom, SRoomsRoomLeft, SHotelRoomsLeft
from hotels.models import Rooms, Hotels

from services.base import BaseService

from bookings.services import BookingService

 
class HotelService(BaseService):
    model = Hotels

    @classmethod
    async def find_hotels_by_location(
        cls, location: str, date_from: date, date_to: date) -> list[SHotelRoomsLeft]:
        result: list = []
        hotels = await cls.select_all_filter(
            func.lower(Hotels.location).like(f"%{location.lower()}%"))

        for hotel in hotels:
            total_rooms: int = hotel.rooms_quantity
            rooms: list[int] = [room.id for room in 
                await RoomService.select_all_filter(Rooms.hotel_id == hotel.id)]
            
            qty_booked_rooms: int = 0
            for room_id in rooms:
                qty_booked_rooms += len(
                    await BookingService.get_booked_rooms(room_id, date_from, date_to))

            if total_rooms > qty_booked_rooms:
                hotel.rooms_left = total_rooms - qty_booked_rooms
                result.append(hotel)

        return result


class RoomService(BaseService):
    model = Rooms

    @classmethod
    async def get_available_rooms_by_hotel_id(
        cls, hotel_id: int, date_from: date, date_to: date) -> list[SRoomsRoomLeft]:
        result: list = []
        rooms: list[SRoom] = [room for room in 
            await cls.select_all_filter(Rooms.hotel_id == hotel_id)]
        for room in rooms:
            rooms_qty = room.quantity
            rooms_booked: int = len(
                await BookingService.get_booked_rooms(room.id, date_from, date_to))
            rooms_left: int = rooms_qty - rooms_booked
            if rooms_left:
                room.rooms_left = rooms_left
                result.append(room)
        return result