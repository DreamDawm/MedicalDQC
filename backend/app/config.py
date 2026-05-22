from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://dataqc:dataqc@localhost:5432/dataqc"
    redis_url: str = "redis://localhost:6379/0"
    report_dir: str = "./reports"
    secret_key: str = "change-me-in-production"

    class Config:
        env_file = ".env"


settings = Settings()
