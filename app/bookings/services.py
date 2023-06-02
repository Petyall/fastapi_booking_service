from datetime import date
from sqlalchemy import delete, insert, select, func, and_, or_

from app.bookings.models import Bookings
from app.hotels.models import Rooms
from app.services.base import BaseService

from app.database import async_session_maker
from app.exceptions import BookingCannotBeFound, IncorrectDataFormat, RoomCannotBeBooked


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
                    # .returning(Bookings.id, Bookings.user_id, Bookings.room_id)
                )
                new_booking = await session.execute(add_booking)
                await session.commit()
                return new_booking.scalar()
                # return new_booking.mappings().one()
            else:
                return RoomCannotBeBooked
            

    @classmethod
    async def find_bookings(cls, user_id: int):
        """
        Поиск всех бронирований для конкретного пользователя

        Принимает:
            user_id: int

        Возвращает:
            bookings: list
        """
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
        async with async_session_maker() as session:
            # Проверка наличия бронирования
            query = select(cls.model).filter_by(id=booking_id, user_id=user_id)
            booking = await session.execute(query)
            booking = booking.scalar_one_or_none()
            if booking is None:
                raise BookingCannotBeFound
            query = delete(cls.model).filter_by(id=booking_id, user_id=user_id)
            await session.execute(query)
            await session.commit()
            

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
