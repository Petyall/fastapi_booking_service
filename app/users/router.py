from fastapi import APIRouter, Depends, Response
from exceptions import UserAlreadyExistsException
from users.dependences import get_current_user, get_current_admin_user
from users.models import Users
from users.auth import get_password_hash, authenticate_user, create_access_token
from users.services import UserService
from users.schemas import SUserAuth


router = APIRouter(
    prefix="/auth",
    tags=["Аутентификация и пользователи"],
)


@router.post("/register")
async def register_user(user_data: SUserAuth):
    """
    Регистрация пользователя
    """
    existing_user = await UserService.find_one_or_none(email=user_data.email)
    if existing_user:
        raise UserAlreadyExistsException
    hashed_password = get_password_hash(user_data.password)
    await UserService.add(email=user_data.email, hashed_password=hashed_password)


@router.post("/login")
async def login_user(response: Response, user_data: SUserAuth):
    """
    Авторизация пользователя
    """
    user = await authenticate_user(user_data.email, user_data.password)
    access_token = create_access_token({"sub": str(user.id)})
    response.set_cookie(
        key="booking_access_token",
        value=access_token,
        httponly=True
    )
    return access_token


@router.post("/logout")
async def logout_user(response: Response):
    """
    Выход пользователя
    """
    response.delete_cookie("booking_access_token")


@router.get("/me")
async def read_users_me(current_user: Users = Depends(get_current_user)):
    """
    Получение информации о пользователе
    """
    return(current_user)


@router.get("/all")
async def read_users_all():
    """
    Получение информации обо всех пользователях
    """
    return await UserService.find_all()


@router.get("/id/{user_id}")
async def read_users_id(user_id: int):
    """
    Получение информации о пользователе по id
    """
    return await UserService.find_one_or_none(id=user_id)