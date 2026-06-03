from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    STEAM_DB_URL: str

    # Steam API
    STEAM_API_KEY: str

    # App
    APP_PORT: int = 8003

    model_config = {"env_file": ".env"}


settings = Settings()