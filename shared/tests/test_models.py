from uuid import uuid4

import pytest
from pydantic import ValidationError

from shared.models import ChunkEnvelope, ChunkType, FileType, Locator, ModelInfo


def valid_fields() -> dict:
    return {
        "document_sha256": "a" * 64,
        "source_path": "data/inbox/handbook.pdf",
        "file_name": "handbook.pdf",
        "file_type": FileType.PDF,
        "page_count": 2,
        "chunk_type": ChunkType.SEMANTIC,
        "chunk_index": 0,
        "text": "Employees must complete security training annually.",
        "token_count": 7,
        "locator": Locator(page_start=1, page_end=1, char_start=0, char_end=52),
        "model_info": ModelInfo(
            embedding_provider="ollama",
            embedding_model="bge-m3",
            embedding_dimension=1024,
        ),
        "embedding": [0.0] * 1024,
    }


def test_chunk_envelope_serializes_to_jsonl_compatible_payload() -> None:
    envelope = ChunkEnvelope(**valid_fields())

    restored = ChunkEnvelope.model_validate_json(envelope.model_dump_json())

    assert restored == envelope
    assert restored.schema_version == "1.0"


def test_derivative_chunk_requires_parent_lineage() -> None:
    fields = valid_fields() | {"chunk_type": ChunkType.QA_PAIR}

    with pytest.raises(ValidationError, match="parent_chunk_id"):
        ChunkEnvelope(**fields)


def test_derivative_chunk_accepts_parent_lineage() -> None:
    fields = valid_fields() | {"chunk_type": ChunkType.QA_PAIR, "parent_chunk_id": uuid4()}

    envelope = ChunkEnvelope(**fields)

    assert envelope.parent_chunk_id is not None


def test_envelope_rejects_invalid_hash_and_reversed_locator_range() -> None:
    fields = valid_fields() | {"document_sha256": "not-a-sha256"}

    with pytest.raises(ValidationError, match="document_sha256"):
        ChunkEnvelope(**fields)

    with pytest.raises(ValidationError, match="page_end"):
        Locator(page_start=2, page_end=1)