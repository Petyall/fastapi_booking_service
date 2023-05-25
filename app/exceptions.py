from fastapi import HTTPException, status


class BookingException(HTTPException):  # <-- наследуемся от HTTPException, который наследован от Exception
    status_code = 500  # <-- задаем значения по умолчанию
    detail = ""
    
    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)



class UserAlreadyExistsException(BookingException):
    status_code=status.HTTP_409_CONFLICT
    detail="Пользователь уже существует"

class UserIsNotPresentException(BookingException):
    status_code=status.HTTP_401_UNAUTHORIZED

class UserHasNotBookingsException(BookingException):
    status_code=status.HTTP_404_NOT_FOUND
    detail="У данного пользователя нет ни одного бронирования"



class TokenExpiredException(BookingException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Истек срок действия токена"

class TokenAbsentException(BookingException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Токен отсутствует"

class IncorrectFormatTokenException(BookingException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Неверный формат токена"

class IncorrectEmailOrPasswordException(BookingException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Неверная почта или пароль"



class RoomCannotBeBooked(BookingException):
    status_code=status.HTTP_409_CONFLICT
    detail="Не осталось свободных номеров"

class HotelCannotBeFound(BookingException):
    status_code=status.HTTP_404_NOT_FOUND
    detail="Данного отеля нет"

class BookingCannotBeFound(BookingException):
    status_code=status.HTTP_404_NOT_FOUND
    detail="Отказано в доступе"

class IncorrectDataFormat(BookingException):
    status_code=status.HTTP_409_CONFLICT
    detail="Дата введена неправильно"
