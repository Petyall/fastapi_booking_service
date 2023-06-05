from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings


# Создание движка для работы
engine = create_async_engine(settings.DATABASE_URL)
# Создание сессии работы с БД (работает по типу транзакции, т.е. если началось
# какое-то действие, то оно должно завершиться. если этого не произошло, то происходит откат)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
# Класс для наследоавния моделей и создания миграций
class Base(DeclarativeBase):
    pass
