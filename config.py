import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    app_title: str = 'Social Network API'
    database_url: str = os.getenv(
        'DATABASE_URL',
        'sqlite+aiosqlite:///network_db/network.db')
    jwt_secret: str = os.getenv('JWT_SECRET_KEY', 'some_key')
    jwt_algorithm: str = os.getenv('JWT_ALGORITHM', 'HS256')
    jwt_effect_seconds: int = int(os.getenv('JWT_EFFECT_SECONDS', 86400))


settings = Settings()
