from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # JWT
    JWT_PUBLIC_KEY: str

    # Redis
    REDIS_URL: str

    # Services
    AUTH_SERVICE_URL: str
    USER_SERVICE_URL: str
    STEAM_SERVICE_URL: str
    TIMER_SERVICE_URL: str
    STATS_SERVICE_URL: str

    # App
    APP_PORT: int = 8000

    model_config = {"env_file": ".env"}


settings = Settings()