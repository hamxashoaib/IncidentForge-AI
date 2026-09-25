from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://incidentforge:forgepassword123@localhost:5432/incidentforge_db"
    SYNC_DATABASE_URL: str = "postgresql://incidentforge:forgepassword123@localhost:5432/incidentforge_db"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
