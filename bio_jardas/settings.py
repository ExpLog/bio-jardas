from pydantic import BaseModel, ConfigDict, constr
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


class Settings(BaseSettings):
    discord: DiscordConfig
    postgres: PostgresConfig
    log_level: constr(to_upper=True)

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


SETTINGS = Settings()
