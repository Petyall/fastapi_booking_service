from datetime import date
from pydantic import parse_obj_as
from fastapi import APIRouter, Depends

from app.exceptions import RoomCannotBeBooked, UserHasNotBookingsException, CannotDeleteBooking
from app.tasks.tasks import send_booking_confirmation_email
from app.users.dependences import get_current_user
from app.users.models import Users
from app.bookings.services import BookingService
from app.bookings.schemas import SBookingWithRooms, SBooking


router = APIRouter(
    prefix="/bookings",
    tags=["Бронирования"],
)


@router.get("")
async def get_bookings(user: Users = Depends(get_current_user)) -> list[SBookingWithRooms]:
    """
    Возврат бронирований пользователя
    """
    # Попытка получить бронирования по id пользователя
    bookings = await BookingService.find_bookings(user_id=user.id)
    # Вывод ошибки, если таких бронирований нет
    if not bookings:
        raise UserHasNotBookingsException()
    # Возврат всех бронирований
    else:
        return bookings


@router.post("")
async def add_booking(room_id: int, date_from: date, date_to: date, user: Users = Depends(get_current_user)):
    """
    Добавляет бронирование комнаты пользователем на указанный диапазон дат
    """
    # Попытка добавить бронирование для пользователя
    booking = await BookingService.add(user_id=user.id, room_id=room_id, date_from=date_from, date_to=date_to)
    # Вывод ошибки, если не получилось забронировать
    if not booking:
        raise RoomCannotBeBooked()
    # Получение списка из созданного бронирования
    booking_dict = parse_obj_as(SBooking, booking).dict()
    # Передача в celery задачи по подтверждению бронирования через почту
    send_booking_confirmation_email.delay(booking_dict, user.email)
    # Возврат созданного бронирования
    return booking_dict


@router.delete("/{booking_id}")
async def delete_booking(booking_id: int, user: Users = Depends(get_current_user)):
    """
    Удаление бронирования пользователем
    """
    # Удаление бронирования
    booking =  await BookingService.delete_booking(booking_id=booking_id, user_id=user.id)
    if not booking:
        raise CannotDeleteBooking()