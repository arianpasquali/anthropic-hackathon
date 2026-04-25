from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://klimaatkracht:klimaatkracht_dev@localhost:5432/klimaatkracht"
    anthropic_api_key: str = ""
    methodology_version: str = "KKM-2026.1"

    model_config = {"env_file": ".env"}


settings = Settings()
