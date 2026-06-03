from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    STATS_DB_URL: str

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str

    # App
    APP_PORT: int = 8005

    model_config = {"env_file": ".env"}


settings = Settings()