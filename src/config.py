from dotenv import load_dotenv

from pydantic import EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(dotenv_path='.env')
load_dotenv(dotenv_path='db.env')


class DataBaseSettings(BaseSettings):
    """Конфиги базы данных."""

    model_config = SettingsConfigDict(case_sensitive=False, env_prefix='POSTGRES_')
    host: str
    port: str
    db: str
    user: str
    password: str
    test_db: str


class AppSettings(BaseSettings):
    """Конфиги приложения."""

    model_config = SettingsConfigDict(case_sensitive=False)

    debug: bool
    crypt_context_schema: str
    crypt_context_deprecated: str
    redis_broker: str
    redis_backend: str
    smtp_server: str
    smtp_port: int
    smtp_username: EmailStr
    smtp_password: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    test_base_url: str


db_settings = DataBaseSettings()
app_settings = AppSettings()
