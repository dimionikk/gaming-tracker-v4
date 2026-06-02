from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    USER_DB_URL: str

    # JWT
    JWT_PUBLIC_KEY: str

    # App
    APP_PORT: int = 8001

    model_config = {"env_file": ".env"}


settings = Settings()