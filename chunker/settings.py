from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ollama_base_url: str = "http://localhost:11434"
    openai_api_key: str | None = None
    embedding_provider: str = "ollama"
    embedding_model: str = "bge-m3"
    embedding_dim: int = Field(default=1024, gt=0)
    llm_provider: str = "ollama"
    llm_model: str = "qwen3"
    chunk_size: int = Field(default=800, gt=0)
    chunk_overlap: int = Field(default=100, ge=0)
    data_input: Path = Path("data/inbox")
    data_output: Path = Path("data/outbox")