from fastapi import APIRouter
from bookings.schemas import SBooking
from sqlalchemy import select
from bookings.services import BookingService
from database import async_session_maker
from bookings.models import Bookings

router = APIRouter(
    prefix="/bookings",
    tags=["Бронирования"],
)

@router.get("")
async def get_bookings() -> list[SBooking]:
    return await BookingService.find_all()