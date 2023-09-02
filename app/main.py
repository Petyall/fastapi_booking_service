import time

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from sqladmin import Admin

from app.admin.views import UsersAdmin, BookingsAdmin, RoomsAdmin, HotelsAdmin, RoleAdmin
from app.bookings.router import router as router_bookings
from app.users.router import router as router_users
from app.hotels.router import router as router_hotels
from app.pages.router import router as router_pages
from app.images.router import router as router_images
from app.database import engine
from app.config import settings
from app.admin.admin import authentication_backend
from app.logger import logger


app = FastAPI()
admin = Admin(app, engine, authentication_backend=authentication_backend)

# Путь к статическим файлам
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Роутеры
app.include_router(router_users)
app.include_router(router_bookings)
app.include_router(router_hotels)
app.include_router(router_pages)
app.include_router(router_images)

# Разрешенные источники
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "Set-Cookie", "Access-Control-Allow-Origin", "Access-Control-Allow-Headers"],
)

# Функция для запуска redis
@app.on_event("startup")
def startup():
    redis = aioredis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}", encoding="utf-8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

# Добавление моделей в админку
admin.add_view(UsersAdmin)
admin.add_view(RoleAdmin)
admin.add_view(BookingsAdmin)
admin.add_view(HotelsAdmin)
admin.add_view(RoomsAdmin)

# Middleware для логгирования
@app.middleware("http")
async def add_process_time_header(request, call_next):
    # Дата начала процесса
    start_time = time.time()
    # Запрос
    response = await call_next(request)
    # Время выполнения процесса
    process_time = time.time() - start_time
    # Вывод информации в консоль (логгирование)
    logger.info(f"Process time: {round(process_time, 4)}")
    return response
