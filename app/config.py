from pydantic import BaseSettings, root_validator
from typing import Literal


class Settings(BaseSettings):
    MODE:Literal["PROD", "DEV", "TEST"]
    LOG_LEVEL:str
    
    DB_HOST:str
    DB_PORT:int
    DB_USER:str
    DB_PASS:str
    DB_NAME:str

    @root_validator
    def get_database_url(cls, v):
        v["DATABASE_URL"] = f"postgresql+asyncpg://{v['DB_USER']}:{v['DB_PASS']}@{v['DB_HOST']}:{v['DB_PORT']}/{v['DB_NAME']}"
        return v

    SMTP_HOST:str
    SMTP_PORT:int
    SMTP_USER:str
    SMTP_PASS:str

    REDIS_HOST:str
    REDIS_PORT:int

    SECRET_KEY:str
    ALGORITHM:str

    class Config:
        env_file = '.env'

settings = Settings()
