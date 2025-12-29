from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

# Environment variables
class Settings(BaseSettings):
    db_url: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    model_config = SettingsConfigDict(env_file=".env")


settings: Settings = Settings()
engine: Engine = create_engine(
    url=settings.db_url,
    pool_pre_ping=True,  # Check connection health before use
)
SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)