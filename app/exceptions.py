from fastapi import HTTPException, status


# Создание класса для обработки исключений, наследующийся от HTTPException
class BookingException(HTTPException):
    # Значения по умолчанию
    status_code = 500
    detail = ""
    
    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


# Ошибки по работе с пользователями
class UserAlreadyExistsException(BookingException):
    status_code=status.HTTP_409_CONFLICT
    detail="Пользователь уже существует"

class UserIsNotPresentException(BookingException):
    status_code=status.HTTP_401_UNAUTHORIZED

class UserHasNotBookingsException(BookingException):
    status_code=status.HTTP_404_NOT_FOUND
    detail="У данного пользователя нет ни одного бронирования"

class NotEnoughAuthorityException(BookingException):
    status_code=status.HTTP_409_CONFLICT
    detail="У данного пользователя недостаточно прав"


# Ошибки по работе с авторизацией
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


# Ошибки по работе с бронированиями
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

class CannotDeleteBooking(BookingException):
    status_code=status.HTTP_409_CONFLICT
    detail="Не удалось удалить бронирование"


# Ошибки по работе с парсером
class TableNotFound(BookingException):
    status_code=status.HTTP_404_NOT_FOUND
    detail="Данная таблица не найдена"

class ParserError(BookingException):
    status_code=status.HTTP_409_CONFLICT
    detail="Ошибка при работе парсера"
