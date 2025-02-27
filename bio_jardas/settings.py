from pydantic import BaseModel, ConfigDict, constr
from pydantic_settings import BaseSettings, SettingsConfigDict


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
    command_timeout: float = 60
    pool_min_size: int = 10
    pool_max_size: int = 10
    # Number of queries after a connection is closed and replaced
    # with a new connection
    pool_max_queries: int = 50000
    # Number of seconds after which inactive connections in the
    # pool will be closed. Pass `0` to disable this mechanism
    pool_max_inactive_connection_lifetime: float = 300

    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)


class Settings(BaseSettings):
    discord: DiscordConfig
    postgres: PostgresConfig
    log_level: constr(to_upper=True)

    model_config = SettingsConfigDict(
        frozen=True,
        case_sensitive=False,
        str_strip_whitespace=True,
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="_",
        env_nested_max_split=1,
    )


SETTINGS = Settings()
