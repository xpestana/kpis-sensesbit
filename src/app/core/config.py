"""Configuración mínima: BD y HubSpot."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Solo variables necesarias para conectar a BD y leer HubSpot."""

    POSTGRES_URL: str = "postgresql+psycopg2://localhost:5432/kpis"
    HUBSPOT_API_KEY: str = ""
    ORIGIN_HOSTS: str = "http://localhost:9000,*"
    GLOBAL_SCHEMA: str = "shared"
    ORG_SCHEMA: str = "org_n74hvy7njcmb"  # Schema tenant para KPIs (Management, Producto)
    PROD: bool = False
    TOKEN_GRAFANA: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        cache_strings=False,
    )

    def __init__(self, **data):
        super().__init__(**data)
        url = self.POSTGRES_URL
        if url.startswith("postgresql+psycopg://"):
            self.POSTGRES_URL = url.replace(
                "postgresql+psycopg://", "postgresql+psycopg2://", 1
            )
        elif url.startswith("postgresql://") and "+" not in url.split("//")[0]:
            self.POSTGRES_URL = url.replace("postgresql://", "postgresql+psycopg2://", 1)


settings = Settings()
