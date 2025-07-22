from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    mapbox_token: str
    openweather_key: str
    database_url: str

    cache_host: str
    cache_port: int
    cache_password: str
    cache_ttl_seconds: int

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

settings = Settings()
