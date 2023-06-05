from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from app.users.schemas import SUserAuth
from app.users.router import register_user, read_users_me
from app.users.auth import authenticate_user, create_access_token
from app.bookings.services import BookingService
from app.hotels.router import get_hotels_by_location


router = APIRouter(
    prefix="/pages",
    tags=["Фронтенд"],
)

templates = Jinja2Templates(directory="app/templates")


# РАБОТА С ГЛАВНОЙ СТРАНИЦЕЙ
@router.route("/", methods=["GET"])
async def home_page(request: Request):
    """
    Возврат главной страницы
    """
    # Переменная для проверки авторизации пользователя
    has_access_token = True if request.cookies.get("booking_access_token") else False
    return templates.TemplateResponse(name="index.html", context={"request": request, "user": has_access_token})


# РАБОТА С ОТЕЛЯМИ
@router.get("/hotels")
async def hotels_page(request: Request):
    """
    Возврат страницы с формой для поиска отелей
    """
    return templates.TemplateResponse("hotels.html", {"request": request})


@router.get("/hotels/filter")
async def hotels_filter_page(request: Request, hotels=Depends(get_hotels_by_location)):
    """
    Возврат страницы отелей с фильтрами
    """
    return templates.TemplateResponse(name="hotels.html", context={"request": request, "hotels": hotels})


# РАБОТА С ПОЛЬЗОВАТЕЛЯМИ
@router.route("/auth", methods=["GET"])
async def auth_page(request: Request):
    """
    Возврат страницы с формой для авторизации и регистрации
    """
    # Если пользователь авторизован, произойдет переадрессация в профиль пользователя
    if request.cookies.get("booking_access_token"):
        return RedirectResponse("/pages/me")
    else:
        return templates.TemplateResponse("login.html", {"request": request})


@router.route("/login", methods=["POST"])
async def login_post(request: Request):
    """
    Возврат страницы авторизации
    """
    # Получение введенных данных
    form_data = await request.form()
    email = form_data["email"]
    password = form_data["password"]
    # Попытка авторизации пользователя
    try:
        user = await authenticate_user(email, password)
        access_token = create_access_token({"sub": str(user.id)})
        response = RedirectResponse(
            "/", 
            status_code=303, 
            headers={"Set-Cookie": f"booking_access_token={access_token}; httponly=True"}
        )
        return response
    # Возврат сообщения с ошибкой, если данные неверные
    except:
        return templates.TemplateResponse(
            "login.html", 
            {"request": request, "message": "Неверный логин или пароль"}
        )


@router.route("/registration", methods=["POST"])
async def registration_post(request: Request):
    """
    Возврат страницы регистрации
    """
    # Получение введенных данных
    form_data = SUserAuth.parse_obj(await request.form())
    # Попытка авторизации пользователя
    try:
        await register_user(form_data)
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "message": "Вы успешно зарегистрированы"}
        )
    # Возврат сообщения с ошибкой, если не удалось зарегистрировать пользователя
    except:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "message": "Пользователь уже зарегистрирован"}
        )
  

@router.get("/me")
async def profile_page(request: Request, user=Depends(read_users_me)):
    """
    Возврат страницы личного кабинета
    """
    # Получение бронирований конкретного пользователя
    user_bookings = await BookingService.find_bookings(user_id=user.id)
    return templates.TemplateResponse(name="profile.html", context={"request": request, "user": user, "bookings": user_bookings})
