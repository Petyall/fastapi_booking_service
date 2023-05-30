from datetime import date
from sqlalchemy import func
from app.hotels.schemas import SRoom, SRoomsRoomLeft, SHotelRoomsLeft
from app.hotels.models import Rooms, Hotels
from app.services.base import BaseService

from app.bookings.services import BookingService

 
class HotelService(BaseService):
    model = Hotels

    @classmethod
    async def find_hotels_by_location(cls, location: str, date_from: date, date_to: date):
        """
        Поиск отеля по заданному городу и дате заезда и выезда

        Принимает:
        location: str
        date_from: date
        date_to: date

        Возвращает:
            SHotelRoomsLeft: list
        """
        # Создание пустого списка для будушего наполнения отелями
        result: list = []
        # Поиск отелей заданному городу
        hotels = await cls.select_all_filter(
            func.lower(Hotels.location).like(f"%{location.lower()}%"))
        # Цикл для подсчета свободных номеров в отелях
        for hotel in hotels:
            # Общее количество комнат
            total_rooms: int = hotel.rooms_quantity
            # Количество комнат в конкретном отеле
            rooms: list[int] = [room.id for room in 
                await RoomService.select_all_filter(Rooms.hotel_id == hotel.id)]
            # Переменная для подсчета забронированных номеров
            qty_booked_rooms: int = 0
            # Цикл подсчитывающий забронированные комнаты
            for room_id in rooms:
                qty_booked_rooms += len(
                    await BookingService.get_booked_rooms(room_id, date_from, date_to))
            # Проверка осталась ли хоть одна комната в наличии
            if total_rooms > qty_booked_rooms:
                hotel.rooms_left = total_rooms - qty_booked_rooms
                # Обновление количества свободных комнат
                result.append(hotel)
        # Возврат списка отелей с обновленным количеством комнат на заданную дату
        return result
    

class RoomService(BaseService):
    model = Rooms

    @classmethod
    async def get_available_rooms_by_hotel_id(cls, hotel_id: int, date_from: date, date_to: date):
        """
        Подсчет свободных комнат конкретного отеля на заданную дату

        Принимает:
        hotel_id: int
        date_from: date
        date_to: date

        Возвращает:
            SHotelRoomsLeft: list
        """
        # Создание пустого списка для будушего наполнения отелями
        result: list = []
        # Заполнение списка комнатами заданного отеля
        rooms: list[SRoom] = [room for room in 
            await cls.select_all_filter(Rooms.hotel_id == hotel_id)]
        # Цикл для подсчета свободных комнат
        for room in rooms:
            # Общее количество комнат
            rooms_qty = room.quantity
            # Подсчет забронированных комнат
            rooms_booked: int = len(
                await BookingService.get_booked_rooms(room.id, date_from, date_to))
            # Подсчет свободных комнат
            rooms_left: int = rooms_qty - rooms_booked
            # Если осталась хоть 1 комната, добавляем новое значение свободных комнат в список
            if rooms_left:
                room.rooms_left = rooms_left
                result.append(room)
        return result