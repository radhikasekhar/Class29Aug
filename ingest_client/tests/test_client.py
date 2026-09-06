import json
from pathlib import Path

import httpx
import pytest

from ingest_client.client import IngestClient
from shared.models import ChunkEnvelope, ChunkType, FileType, Locator, ModelInfo


def envelope() -> ChunkEnvelope:
    return ChunkEnvelope(
        document_sha256="b" * 64, source_path="input.txt", file_name="input.txt", file_type=FileType.TXT,
        page_count=1, chunk_type=ChunkType.SEMANTIC, chunk_index=0, text="Policy content", token_count=2,
        locator=Locator(page_start=1, page_end=1), embedding=[0.0] * 1024,
        model_info=ModelInfo(embedding_provider="ollama", embedding_model="bge-m3", embedding_dimension=1024),
    )


def test_ingest_validates_and_resumes(tmp_path: Path) -> None:
    outbox = tmp_path / "document.jsonl"
    outbox.write_text(envelope().model_dump_json() + "\n", encoding="utf-8")
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200 if request.method == "PUT" else 201, json={"id": "00000000-0000-0000-0000-000000000001", "chunks": []})

    client = IngestClient("http://api", transport=httpx.MockTransport(handler))
    state = tmp_path / "state.json"
    assert client.ingest_file(outbox, state) == 1
    assert [request.url.path for request in requests] == ["/documents", "/chunks/bulk"]
    assert client.ingest_file(outbox, state) == 0


def test_ingest_rejects_invalid_jsonl_before_request(tmp_path: Path) -> None:
    outbox = tmp_path / "bad.jsonl"
    outbox.write_text(json.dumps({"bad": "payload"}), encoding="utf-8")
    client = IngestClient("http://api", transport=httpx.MockTransport(lambda request: pytest.fail("request made")))
    with pytest.raises(Exception):
        client.ingest_file(outbox, tmp_path / "state.json")