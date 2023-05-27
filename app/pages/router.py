from fastapi import APIRouter, Request, Depends, Response
from fastapi.templating import Jinja2Templates
from bookings.services import BookingService
from bookings.router import get_bookings
from users.router import read_users_me
from users.auth import create_access_token
from users.auth import authenticate_user
from hotels.router import get_hotels_by_location
from fastapi.responses import RedirectResponse

router = APIRouter(
    prefix="/pages",
    tags=["Фронтенд"],
)


templates = Jinja2Templates(directory="templates")


@router.get("/hotels")
async def get_hotels_page(request: Request, hotels=Depends(get_hotels_by_location)):
    return templates.TemplateResponse(name="hotels.html", context={"request": request, "hotels": hotels})

# Маршрут для отображения формы авторизации
@router.route("/", methods=["GET"])
async def login_get(request: Request):
    if request.cookies.get("booking_access_token"):
        return RedirectResponse("/pages/login/me")
    else:
        # Отображение формы авторизации при первом запуске страницы
        return templates.TemplateResponse("login.html", {"request": request})

# Обработка POST-запроса маршрута /login
@router.route("/login", methods=["POST"])
async def login_post(request: Request):
    # Получение данных из формы
    form = await request.form()
    email = form["email"]
    password = form["password"]
    user = await authenticate_user(email, password)
    access_token = create_access_token({"sub": str(user.id)})
    # Отправка данных авторизации в cookies и перенаправление на главную страницу
    response = RedirectResponse("/", status_code=303, headers={"Set-Cookie": f"booking_access_token={access_token}; httponly=True"})
    return response
  

@router.get("/login/me")
async def profile_page(request: Request, user=Depends(read_users_me)):
    bookings = await BookingService.find_bookings(user_id=user.id)
    return templates.TemplateResponse(name="profile.html", context={"request": request, "user": user, "bookings": bookings})



