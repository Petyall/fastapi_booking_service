from datetime import date
from sqlalchemy import delete, insert, select, func, and_, or_

from bookings.models import Bookings
from hotels.models import Rooms
from services.base import BaseService

from database import async_session_maker
from exceptions import BookingCannotBeFound, IncorrectDataFormat


class BookingService(BaseService):
    model = Bookings

    @classmethod
    async def add(cls, user_id: int, room_id: int, date_from: date, date_to: date):
        async with async_session_maker() as session:
            if date_from >= date_to:
                raise IncorrectDataFormat
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

            if rooms_left > 0:
                get_price = select(Rooms.price).filter_by(id=room_id)
                price = await session.execute(get_price)
                price: int = price.scalar()
                add_booking = (
                    insert(Bookings)
                    .values(
                        room_id=room_id,
                        user_id=user_id,
                        date_from=date_from,
                        date_to=date_to,
                        price=price,
                    )
                    .returning(Bookings.id, Bookings.user_id, Bookings.room_id)
                )

                new_booking = await session.execute(add_booking)
                await session.commit()
                return new_booking.mappings().one()
            else:
                return None
            

    @classmethod
    async def find_bookings(cls, user_id: int):
        async with async_session_maker() as session:
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
            
            bookings = await session.execute(bookings_query)
            return bookings.mappings().all()


    @classmethod
    async def delete_booking(cls, booking_id: int, user_id: int):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(id=booking_id, user_id=user_id)
            result = await session.execute(query)
            result = result.scalar_one_or_none()
            if result is None:
                raise BookingCannotBeFound
            query = delete(cls.model).filter_by(id=booking_id, user_id=user_id)
            await session.execute(query)
            await session.commit()
            

    @classmethod
    async def get_booked_rooms(cls, room_id: int, date_from: date, date_to: date) -> int:
        if date_from >= date_to:
            raise IncorrectDataFormat
        return await cls.select_all_filter(
            and_(
                Bookings.room_id == room_id,
                and_(Bookings.date_to >= date_from, Bookings.date_from <= date_to),
            )
        )

