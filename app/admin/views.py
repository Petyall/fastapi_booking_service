from sqladmin import ModelView
from app.users.models import Users, Role
from app.bookings.models import Bookings
from app.hotels.models import Hotels, Rooms


# Модель пользователей для админки
class UsersAdmin(ModelView, model=Users):
    column_list = [Users.id, Users.email]
    column_details_exclude_list = [Users.hashed_password]
    can_delete = False
    name = "Пользователь"
    name_plural = "Пользователи"
    icon = "fa-solid fa-user"


# Модель Ролей для админки
class RoleAdmin(ModelView, model=Role):
    column_list = [Role.id, Role.name]
    name = "Роль"
    name_plural = "Роли"


# Модель бронирований для админки
class BookingsAdmin(ModelView, model=Bookings):
    column_list = [column.name for column in Bookings.__table__.columns] # Цикл для получения названий колонок БД
    column_list += [Bookings.user, Bookings.room] # Расширение списка названия колонок пользователем
    name = "Бронь"
    name_plural = "Бронирования"


# Модель отелей для админки
class HotelsAdmin(ModelView, model=Hotels):
    column_list = [column.name for column in Hotels.__table__.columns]
    column_list += [Hotels.room]
    name = "Отель"
    name_plural = "Отели"


# Модель комнат для админки
class RoomsAdmin(ModelView, model=Rooms):
    column_list = [column.name for column in Rooms.__table__.columns]
    column_list += [Rooms.hotel, Rooms.booking]
    name = "Комната"
    name_plural = "Комнаты"



