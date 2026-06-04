from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    ACTIVITY_DB_URL: str

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str

    # App
    APP_PORT: int = 8007

    model_config = {"env_file": ".env"}


settings = Settings()