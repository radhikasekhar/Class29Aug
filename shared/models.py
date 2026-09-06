"""Versioned JSONL contracts for the chunker-to-ingest-client handoff."""

from enum import StrEnum
from typing import Annotated, Any, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator


Sha256 = Annotated[str, StringConstraints(pattern=r"^[a-f0-9]{64}$")]


class FileType(StrEnum):
    PDF = "pdf"
    DOCX = "docx"
    HTML = "html"
    TXT = "txt"


class ChunkType(StrEnum):
    SEMANTIC = "semantic"
    CONTEXTUAL = "contextual"
    SUMMARY = "summary"
    RAPTOR = "raptor"
    QA_PAIR = "qa_pair"
    FACTOID = "factoid"


class Locator(BaseModel):
    """Source position used to render traceable citations."""

    model_config = ConfigDict(extra="forbid")

    page_start: int | None = Field(default=None, ge=1)
    page_end: int | None = Field(default=None, ge=1)
    char_start: int | None = Field(default=None, ge=0)
    char_end: int | None = Field(default=None, ge=0)
    heading_path: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_ranges(self) -> "Locator":
        if self.page_start is not None and self.page_end is not None and self.page_end < self.page_start:
            raise ValueError("page_end must be greater than or equal to page_start")
        if self.char_start is not None and self.char_end is not None and self.char_end < self.char_start:
            raise ValueError("char_end must be greater than or equal to char_start")
        return self


class ModelInfo(BaseModel):
    """Models and prompt versions required to reproduce an artifact."""

    model_config = ConfigDict(extra="forbid")

    embedding_provider: str = Field(min_length=1)
    embedding_model: str = Field(min_length=1)
    embedding_dimension: int = Field(gt=0)
    generator_provider: str | None = None
    generator_model: str | None = None
    prompt_version: str | None = None


class ChunkEnvelope(BaseModel):
    """One JSONL record emitted by chunker and consumed by ingest_client."""

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1.0"] = "1.0"
    chunk_id: UUID = Field(default_factory=uuid4)
    document_sha256: Sha256
    source_path: str = Field(min_length=1)
    file_name: str = Field(min_length=1)
    file_type: FileType
    title: str | None = None
    page_count: int = Field(ge=0)
    chunk_type: ChunkType
    chunk_index: int = Field(ge=0)
    text: str = Field(min_length=1)
    token_count: int = Field(ge=0)
    locator: Locator
    model_info: ModelInfo
    embedding: list[float] = Field(min_length=1)
    parent_chunk_id: UUID | None = None
    context_prefix: str | None = None
    level: int = Field(default=0, ge=0)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_lineage(self) -> "ChunkEnvelope":
        derivative_types = {ChunkType.CONTEXTUAL, ChunkType.QA_PAIR, ChunkType.FACTOID, ChunkType.RAPTOR}
        if self.chunk_type in derivative_types and self.parent_chunk_id is None:
            raise ValueError("derivative chunks require parent_chunk_id")
        if not self.text.strip():
            raise ValueError("text must not be blank")
        return self