from sqlalchemy import delete, select, insert
from app.database import async_session_maker

class BaseService:
    model = None

    # Поиск чего-либо по id
    @classmethod
    # cls (класс) == self (функция)
    async def find_by_id(cls, model_id: int):
        # Создание сессии для работы с БД
        async with async_session_maker() as session:
            # Выборка данных из БД по фильтру
            query = select(cls.model).filter_by(id=model_id)
            result = await session.execute(query)
            return(result.scalar_one_or_none())


    @classmethod
    async def find_one_or_none(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return(result.scalar_one_or_none())


    @classmethod
    async def find_all(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return(result.scalars().all())
        

    @classmethod
    async def add(cls, **data):
        async with async_session_maker() as session:
            query = insert(cls.model).values(**data)
            await session.execute(query)
            await session.commit()

    @classmethod
    async def select_all_filter(cls, *args, **kwargs):
        async with async_session_maker() as session:
            query = select(cls.model).filter(*args, **kwargs)
            result = await session.execute(query)
            return result.scalars().all()