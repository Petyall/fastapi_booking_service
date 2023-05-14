from sqlalchemy import select
from services.base import BaseService
from database import async_session_maker
from bookings.models import Bookings


class BookingService(BaseService):
    model = Bookings
