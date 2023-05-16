from services.base import BaseService
from bookings.models import Bookings


class BookingService(BaseService):
    model = Bookings
