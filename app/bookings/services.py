from datetime import date
from sqlalchemy import delete, insert, select, func, and_, or_
from sqlalchemy.exc import SQLAlchemyError

from app.bookings.models import Bookings
from app.hotels.models import Rooms
from app.services.base import BaseService
from app.database import async_session_maker
from app.exceptions import BookingCannotBeFound, IncorrectDataFormat, RoomCannotBeBooked
from app.logger import logger


class BookingService(BaseService):
    model = Bookings

    @classmethod
    async def add(cls, user_id: int, room_id: int, date_from: date, date_to: date):
        """
        Добавляет бронирование комнаты пользователем на указанный диапазон дат

        Принимает:
            user_id: int 
            room_id: int 
            date_from: date 
            date_to: date

        Возвращает:
            []
        """
        try:
            async with async_session_maker() as session:
                # Проверка валидности дат
                if date_from >= date_to:
                    raise IncorrectDataFormat
                # Получение забронированных комнат на указанную дату
                booked_rooms = (
                    select(Bookings)
                    .where(
                        and_(
                            Bookings.room_id == room_id,
                            or_(
                                and_(
                                    Bookings.date_from >= date_from,
                                    Bookings.date_from <= date_to,
                                ),
                                and_(
                                    Bookings.date_from <= date_from,
                                    Bookings.date_to > date_from,
                                ),
                            ),
                        )
                    )
                    .cte("booked_rooms")
                )
                # Подсчет комнат, оставшихся в наличии
                get_rooms_left = (
                    select(
                        (Rooms.quantity - func.count(booked_rooms.c.room_id)).label(
                            "rooms_left"
                        )
                    )
                    .select_from(Rooms)
                    .join(booked_rooms, booked_rooms.c.room_id == Rooms.id, isouter=True)
                    .where(Rooms.id == room_id)
                    .group_by(Rooms.quantity, booked_rooms.c.room_id)
                )
                rooms_left = await session.execute(get_rooms_left)
                rooms_left: int = rooms_left.scalar()
                # Проверка наличия хотя бы 1 комнаты
                if rooms_left > 0:
                    # Получение стоимости бронирования комнаты
                    get_price = select(Rooms.price).filter_by(id=room_id)
                    price = await session.execute(get_price)
                    price: int = price.scalar()
                    # Создание бронирования
                    add_booking = (
                        insert(Bookings)
                        .values(
                            room_id=room_id,
                            user_id=user_id,
                            date_from=date_from,
                            date_to=date_to,
                            price=price,
                        )
                        .returning(Bookings)
                    )
                    new_booking = await session.execute(add_booking)
                    await session.commit()
                    return new_booking.scalar()
                else:
                    return RoomCannotBeBooked
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Ошибка базы данных при добавлении бронирования"
            elif isinstance(e, Exception):
                msg = "Неизвестная ошибка при добавлении бронирования"
            extra = {"user_id": user_id, "room_id": room_id, "date_from": date_from, "date_to": date_to}
            logger.error(msg, extra=extra, exc_info=True)
            
            

    @classmethod
    async def find_bookings(cls, user_id: int):
        """
        Поиск всех бронирований для конкретного пользователя

        Принимает:
            user_id: int

        Возвращает:
            bookings: list
        """
        try:
            async with async_session_maker() as session:
                # Получение комнат и бронирований
                bookings_query = (
                    select(
                        Bookings.room_id,
                        Bookings.user_id,
                        Bookings.date_from,
                        Bookings.date_to,
                        Bookings.price,
                        Bookings.total_cost,
                        Bookings.total_days,
                        Rooms.image_id,
                        Rooms.name,
                        Rooms.services,
                        Rooms.description
                    )
                    .select_from(Bookings)
                    .join(Rooms, Bookings.room_id == Rooms.id)
                    .where(Bookings.user_id == user_id)
                )
                # Возврат полученных значений
                bookings = await session.execute(bookings_query)
                return bookings.mappings().all()
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Ошибка базы данных при поиске бронирований пользователя"
            elif isinstance(e, Exception):
                msg = "Неизвестная ошибка при поиске бронирований пользователя"
            extra = {"user_id": user_id}
            logger.error(msg, extra=extra, exc_info=True)


    @classmethod
    async def delete_booking(cls, booking_id: int, user_id: int):
        """
        Удаление бронирования для конкретного пользователя

        Принимает:
            booking_id: int
            user_id: int

        Возвращает:
            []
        """
        try:
            async with async_session_maker() as session:
                # Проверка наличия бронирования
                query = select(cls.model).filter_by(id=booking_id, user_id=user_id)
                booking = await session.execute(query)
                booking = booking.scalar_one_or_none()
                # Возврат ошибки, если бронирование не найдено
                if booking is None:
                    raise BookingCannotBeFound
                # Удаление бронирования
                query = delete(cls.model).filter_by(id=booking_id, user_id=user_id)
                await session.execute(query)
                await session.commit()
                return f"Бронирование #{booking_id} удалено"
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Ошибка базы данных при поиске бронирований пользователя"
            elif isinstance(e, Exception):
                msg = "Неизвестная ошибка при поиске бронирований пользователя"
            extra = {"user_id": user_id, "booking_id": booking_id}
            logger.error(msg, extra=extra, exc_info=True)


    @classmethod
    async def get_booked_rooms(cls, room_id: int, date_from: date, date_to: date) -> int:
        """
        Получение забронированных комнат на указанную дату

        Принимает:
            room_id: int 
            date_from: date 
            date_to: date

        Возвращает:
            Bookings: list
        """
        try:
            # Проверка валидности дат
            if date_from >= date_to:
                raise IncorrectDataFormat
            # Получение и возврат забронированных комнат
            return await cls.select_all_filter(
                and_(
                    Bookings.room_id == room_id,
                    and_(Bookings.date_to >= date_from, Bookings.date_from <= date_to),
                )
            )
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Ошибка базы данных при поиске забронированных комнат"
            elif isinstance(e, Exception):
                msg = "Неизвестная ошибка при поиске забронированных комнат"
            extra = {"room_id": room_id, "date_from": date_from, "date_to": date_to}
            logger.error(msg, extra=extra, exc_info=True)
