from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    AUTH_DB_URL: str

    # Redis
    REDIS_URL: str

    # JWT
    JWT_PRIVATE_KEY: str
    JWT_PUBLIC_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # App
    APP_PORT: int = 8000

    model_config = {"env_file": ".env"} 


settings = Settings()