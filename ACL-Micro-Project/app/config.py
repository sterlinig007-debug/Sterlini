from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    app_name: str = "ACL Micro Project Simulator"
    database_path: str = "data/acl_demo.db"
    secret_key: str = "change-this-for-production"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()
