from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    RABBITMQ_URL: str = "amqp://lms:lms@localhost:5672/"
    EVENTS_EXCHANGE: str = "lms.events"

    DB_HOST: str = "localhost"
    DB_PORT: int = 5433
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "postgres"

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    RECOMMENDATION_HOST: str = "localhost"
    RECOMMENDATION_PORT: int = 50051

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


setting = Settings()
