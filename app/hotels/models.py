from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Hotels(Base):
    __tablename__ = "hotels"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    services = Column(JSON)
    rooms_quantity = Column(Integer, nullable=False)
    image_id  = Column(Integer)

    # Создание отношения для SQLAlchemy
    room = relationship("Rooms", back_populates="hotel")

    # Фукнция переопределяющая отображения названия модели
    def __str__(self):
        return f"Отель {self.name}"


class Rooms(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, nullable=False)
    hotel_id = Column(ForeignKey("hotels.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Integer, nullable=False)
    services = Column(JSON, nullable=True)
    quantity = Column(Integer, nullable=False)
    image_id = Column(Integer)

    # Создание отношения для SQLAlchemy
    hotel = relationship("Hotels", back_populates="room")
    booking = relationship("Bookings", back_populates="room")

    # Фукнция переопределяющая отображения названия модели
    def __str__(self):
        return f"Комната {self.id} отеля {self.hotel_id}"