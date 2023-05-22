from pydantic import BaseModel
from pydantic.schema import Optional


class SHotel(BaseModel):
    id: int
    name: str
    location: str
    services: list
    image_id: int
    rooms_quantity: int
    # Позволяет преобразовывать json в query и обратно
    class Config:
        orm_mode = True
 

class SHotelRoomsLeft(SHotel):
    rooms_left: int


class SRoom(BaseModel):
    id: int
    hotel_id: int
    name: str
    description: Optional[str]
    price: int
    services: list
    quantity: int
    image_id: int
    # Позволяет преобразовывать json в query и обратно
    class Config:
        orm_mode = True


class SRoomsRoomLeft(SRoom):
    rooms_left: int


class SRoomWithPrice(BaseModel):
    id: int
    hotel_id: int
    name: str
    description: Optional[str]
    price: int
    services: list
    quantity: int
    image_id: int
    total_cost: int
    rooms_left: int

    # Позволяет преобразовывать json в query и обратно
    class Config:
        orm_mode = True