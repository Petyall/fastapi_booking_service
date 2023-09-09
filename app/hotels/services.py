from datetime import date
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from app.exceptions import HotelCannotBeFound

from app.hotels.schemas import SRoom
from app.hotels.models import Rooms, Hotels
from app.services.base import BaseService
from app.bookings.services import BookingService
from app.logger import logger

 
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
        try:
            # Создание пустого списка для будушего наполнения отелями
            result: list = []
            # Поиск отелей по заданному городу
            hotels = await cls.select_all_filter(func.lower(Hotels.location).like(f"%{location.lower()}%"))
            # Цикл для подсчета свободных номеров в отелях
            for hotel in hotels:
                # Общее количество комнат
                total_rooms: int = hotel.rooms_quantity
                # Количество комнат в конкретном отеле
                rooms: list[int] = [room.id for room in await RoomService.select_all_filter(Rooms.hotel_id == hotel.id)]
                # Переменная для подсчета забронированных номеров
                qty_booked_rooms: int = 0
                # Цикл подсчитывающий забронированные комнаты
                for room_id in rooms:
                    qty_booked_rooms += len(await BookingService.get_booked_rooms(room_id, date_from, date_to))
                # Проверка осталась ли хоть одна комната в наличии
                if total_rooms > qty_booked_rooms:
                    hotel.rooms_left = total_rooms - qty_booked_rooms
                    # Обновление количества свободных комнат
                    result.append(hotel)
            # Возврат списка отелей с обновленным количеством комнат на заданную дату
            return result
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database error when finding hotels"
            elif isinstance(e, Exception):
                msg = "Unknown error when finding hotels"
            extra = {"location": location,"date_from": date_from, "date_to": date_to}
            logger.error(msg, extra=extra, exc_info=True)
    

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
    