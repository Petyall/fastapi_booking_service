from datetime import date
from pydantic import BaseModel
from pydantic.schema import Optional

class SBooking(BaseModel):
    id: int 
    room_id: int 
    user_id: int 
    date_from: date
    date_to: date
    price: int 
    total_cost: int 
    total_days: int 

    # Позволяет преобразовывать json в query и обратно
    class Config:
        orm_mode = True


class SBookingWithRooms(BaseModel):
    room_id: int 
    user_id: int 
    date_from: date
    date_to: date
    price: int 
    total_cost: int 
    total_days: int 
    image_id: int
    name: str
    description: Optional[str]
    services: list
    
    # Позволяет преобразовывать json в query и обратно
    class Config:
        orm_mode = True
        