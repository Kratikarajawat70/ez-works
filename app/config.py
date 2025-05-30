from pydantic_settings import BaseSettings
from pydantic import HttpUrl

class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    FERNET_KEY: str
    EMAIL_USER: str
    EMAIL_PASSWORD: str
    base_url: HttpUrl  # add this line

    class Config:
        env_file = ".env"

settings = Settings()
