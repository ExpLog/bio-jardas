from typing import Annotated
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, ConfigDict, StringConstraints, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class DiscordConfig(BaseModel):
    token: str

    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)


class PostgresConfig(BaseModel):
    host: str
    port: int
    database: str
    user: str
    password: str

    connection_timeout: float = 60

    pool_size: int = 10
    pool_max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 300

    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    @property
    def url(self) -> URL:
        return URL.create(
            drivername="postgresql+psycopg_async",
            username=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.database,
        )

    @property
    def sync_url(self) -> URL:
        return URL.create(
            drivername="postgresql+psycopg",
            username=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.database,
        )


class GameConfig(BaseModel):
    shadow_ban_role: str
    member_role: str

    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)


class Settings(BaseSettings):
    discord: DiscordConfig
    postgres: PostgresConfig
    game: GameConfig

    timezone: str = "Europe/Lisbon"

    log_level: Annotated[str, StringConstraints(to_upper=True)]
    log_force_console_renderer: bool = False

    model_config = SettingsConfigDict(
        frozen=True,
        extra="ignore",
        case_sensitive=False,
        str_strip_whitespace=True,
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="_",
        env_nested_max_split=1,
    )

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, v: str):
        try:
            ZoneInfo(v)
        except ZoneInfoNotFoundError:
            raise ValueError(f"Unknown timezone: {v}")
        return v


SETTINGS = Settings()
