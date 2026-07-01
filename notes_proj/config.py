from pydantic_settings import BaseSettings,SettingsConfigDict
from typing import Optional
from pathlib import Path
import os
base_path=Path(__file__).resolve().parent.parent #file's loc is ../Notes/notes_proj/config while .env is in ../Notes/.env so to get /Notes as base path we do .parent.parent on the current file path
class BaseConfig(BaseSettings):
    ENV_STATE:Optional[str]=None
    model_config=SettingsConfigDict(env_file=base_path/".env",extra="ignore")
class GlobalConfig(BaseConfig):
    DATABASE_URL:Optional[str]=None
    DB_FORCE_ROLLBACK:bool=False
    SECRET_KEY:Optional[str]=None
    APP_PASSWORD:Optional[str]=None
    MAIL_USERNAME:Optional[str]=None
    MAIL_PORT:Optional[int]=None
    MAIL_SERVER:Optional[str]=None
    MAIL_STARTTLS:bool=True
    MAIL_SSL_TLS:bool=False
    ASYNC_DATABASE_URL:Optional[str]=None
config=GlobalConfig()