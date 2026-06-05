from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    CHAT_DB_URL: str

    # Redis
    REDIS_URL: str

    # App
    APP_PORT: int = 8009

    model_config = {"env_file": ".env"}


settings = Settings()