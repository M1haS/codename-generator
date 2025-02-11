from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Codename Generator API"
    app_version: str = "1.2.0"
    debug: bool = False
    database_url: str = "sqlite+aiosqlite:///./codenames.db"
    default_namespace: str = "global"
    recycle_cooldown_days: int = 30
    max_generate_batch: int = 50
    max_retries_on_collision: int = 100

    class Config:
        env_file = ".env"


settings = Settings()
