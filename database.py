from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# env viravles
class Settings(BaseSettings):
    db_url: str
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
engine = create_engine(url=settings.db_url)
SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)