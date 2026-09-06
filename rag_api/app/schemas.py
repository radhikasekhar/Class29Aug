from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from shared.models import ChunkType, FileType


class DocumentStatus(StrEnum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    CHUNKED = "chunked"
    INDEXED = "indexed"
    FAILED = "failed"


class CollectionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None


class CollectionUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None


class CollectionResponse(CollectionCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID


class DocumentUpsert(BaseModel):
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    source_path: str = Field(min_length=1)
    file_name: str = Field(min_length=1)
    file_type: FileType
    title: str | None = None
    markdown: str | None = None
    page_count: int = Field(default=0, ge=0)
    status: DocumentStatus = DocumentStatus.UPLOADED
    collection_id: UUID | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class DocumentUpdate(BaseModel):
    title: str | None = None
    markdown: str | None = None
    page_count: int | None = Field(default=None, ge=0)
    status: DocumentStatus | None = None
    collection_id: UUID | None = None
    metadata: dict[str, Any] | None = None


class DocumentResponse(DocumentUpsert):
    model_config = ConfigDict(from_attributes=True)

    id: UUID


class ChunkCreate(BaseModel):
    document_id: UUID
    parent_chunk_id: UUID | None = None
    chunk_type: ChunkType
    chunk_index: int = Field(ge=0)
    text: str = Field(min_length=1)
    token_count: int = Field(ge=0)
    locator: dict[str, Any] = Field(default_factory=dict)
    embedding: list[float] = Field(min_length=1024, max_length=1024)
    model_info: dict[str, Any] = Field(default_factory=dict)
    context_prefix: str | None = None
    level: int = Field(default=0, ge=0)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ChunkBulkCreate(BaseModel):
    chunks: list[ChunkCreate] = Field(min_length=1)


class ChunkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    document_id: UUID
    parent_chunk_id: UUID | None
    chunk_type: ChunkType
    chunk_index: int
    text: str
    token_count: int
    locator: dict[str, Any]
    model_info: dict[str, Any]
    context_prefix: str | None
    level: int
    metadata: dict[str, Any]


class ChunkBulkResponse(BaseModel):
    chunks: list[ChunkResponse]


class SearchRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int = Field(default=8, ge=1, le=100)
    chunk_types: list[ChunkType] | None = None
    collection_id: UUID | None = None
    document_id: UUID | None = None


class SearchResult(ChunkResponse):
    score: float