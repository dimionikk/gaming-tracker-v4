from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    FRIEND_DB_URL: str

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str

    # App
    APP_PORT: int = 8006

    model_config = {"env_file": ".env"}


settings = Settings()