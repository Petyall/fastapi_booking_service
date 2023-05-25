from datetime import date
from fastapi import APIRouter, Depends

from users.dependences import get_current_user
from users.models import Users

from bookings.services import BookingService
from bookings.schemas import SBookingWithRooms

from exceptions import RoomCannotBeBooked, UserHasNotBookingsException


router = APIRouter(
    prefix="/bookings",
    tags=["Бронирования"],
)


@router.get("")
async def get_bookings(user: Users = Depends(get_current_user)) -> list[SBookingWithRooms]:
    """
    Возврат бронирований пользователя
    """
    bookings = await BookingService.find_bookings(user_id=user.id)
    if not bookings:
        raise UserHasNotBookingsException()
    else:
        return bookings


@router.post("")
async def add_booking(room_id: int, date_from: date, date_to: date, user: Users = Depends(get_current_user)):
    """
    Добавляет бронирование комнаты пользователем на указанный диапазон дат
    """
    booking = await BookingService.add(user_id=user.id, room_id=room_id, date_from=date_from, date_to=date_to)
    if not booking:
        raise RoomCannotBeBooked()


@router.delete("/{booking_id}")
async def delete_booking(booking_id: int, user: Users = Depends(get_current_user)):
    """
    Удаление бронирования пользователем
    """
    await BookingService.delete_booking(booking_id=booking_id, user_id=user.id)
