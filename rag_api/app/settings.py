from functools import cached_property

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from psycopg.conninfo import make_conninfo


class Settings(BaseSettings):
    """Runtime configuration for the RAG API."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", populate_by_name=True)

    db_host: str = Field(default="localhost", validation_alias=AliasChoices("DB_HOST", "POSTGRES_HOST"))
    db_port: int = Field(default=5432, ge=1, le=65535, validation_alias=AliasChoices("DB_PORT", "POSTGRES_PORT"))
    db_name: str = Field(default="rag", validation_alias=AliasChoices("DB_NAME", "POSTGRES_DB"))
    db_user: str = Field(default="postgres", validation_alias=AliasChoices("DB_USER", "POSTGRES_USER"))
    db_password: str = Field(default="postgres", validation_alias=AliasChoices("DB_PASSWORD", "POSTGRES_PASSWORD"))
    db_connect_timeout: int = Field(default=5, ge=1, le=60, validation_alias=AliasChoices("DB_CONNECT_TIMEOUT"))
    ollama_base_url: str = "http://localhost:11434"
    embedding_provider: str = "ollama"
    embedding_model: str = "bge-m3"
    embedding_dim: int = Field(default=1024, gt=0)

    @cached_property
    def database_url(self) -> str:
        return make_conninfo(
            host=self.db_host,
            port=self.db_port,
            dbname=self.db_name,
            user=self.db_user,
            password=self.db_password,
            connect_timeout=self.db_connect_timeout,
        )