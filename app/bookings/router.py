from fastapi import APIRouter, Depends
from users.dependences import get_current_user
from bookings.services import BookingService
from users.models import Users


# Что-то типо создания приложения, в котором будут все эндпоинты
router = APIRouter(
    prefix="/bookings",
    tags=["Бронирования"],
)


@router.get("")
async def get_bookings(user: Users = Depends(get_current_user)): #-> list[SBooking]:
    return await BookingService.find_all(user_id=user.id)
