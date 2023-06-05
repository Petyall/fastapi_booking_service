from typing import Optional
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse

from app.config import settings
from app.users.auth import authenticate_user, create_access_token
from app.users.dependences import get_current_user


# Класс для авторизации в админ панель
class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        # Получение введенных данных
        form = await request.form()
        email, password = form["username"], form["password"]
        # Авторизация пользователя
        user = await authenticate_user(email, password)
        # Проверка авторизация пользователя
        if user:
            # Создание токена
            access_token = create_access_token({"sub": str(user.id)})
            request.session.update({"token": access_token})
        return True

    async def logout(self, request: Request) -> bool:
        # Очистка токена из cookie
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> Optional[RedirectResponse]:
        # Попытка получить токен
        token = request.session.get("token")
        # Если нет токена, произойдет возврат на страницу авторизации
        if not token:
            return RedirectResponse(request.url_for("admin:login"), status_code=302)
        # Получение пользователя по токену
        user = await get_current_user(token)
        # Если пользователя не существует или у него нет админ прав, произойдет возврат на страницу авторизации
        if not user or user.role_id != 2:
            return RedirectResponse(request.url_for("admin:login"), status_code=302)


authentication_backend = AdminAuth(secret_key=settings.SECRET_KEY)
