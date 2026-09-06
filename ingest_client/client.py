import json
from pathlib import Path
from time import sleep

import httpx

from shared.models import ChunkEnvelope


class IngestClient:
    def __init__(self, api_url: str, batch_size: int = 100, retries: int = 3, transport: httpx.BaseTransport | None = None) -> None:
        self.api_url = api_url.rstrip("/")
        self.batch_size = batch_size
        self.retries = retries
        self.transport = transport

    def _request(self, method: str, path: str, payload: dict) -> httpx.Response:
        for attempt in range(self.retries):
            with httpx.Client(base_url=self.api_url, transport=self.transport, timeout=30) as client:
                response = client.request(method, path, json=payload)
            if response.status_code < 500:
                response.raise_for_status()
                return response
            if attempt + 1 < self.retries:
                sleep(0.2 * (2**attempt))
        response.raise_for_status()
        return response

    def ingest_file(self, path: Path, state_path: Path, dry_run: bool = False) -> int:
        records = [ChunkEnvelope.model_validate_json(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        if not records:
            return 0
        document_hash = records[0].document_sha256
        if any(item.document_sha256 != document_hash for item in records):
            raise ValueError("A JSONL file must contain one document SHA-256")
        completed = set(json.loads(state_path.read_text(encoding="utf-8"))) if state_path.exists() else set()
        if document_hash in completed:
            return 0
        first = records[0]
        document = {
            "sha256": document_hash, "source_path": first.source_path, "file_name": first.file_name,
            "file_type": first.file_type, "title": first.title, "page_count": first.page_count, "metadata": {},
        }
        if dry_run:
            return len(records)
        document_id = self._request("PUT", "/documents", document).json()["id"]
        for offset in range(0, len(records), self.batch_size):
            batch = []
            for item in records[offset : offset + self.batch_size]:
                batch.append({
                    "document_id": document_id, "parent_chunk_id": item.parent_chunk_id,
                    "chunk_type": item.chunk_type, "chunk_index": item.chunk_index, "text": item.text,
                    "token_count": item.token_count, "locator": item.locator.model_dump(), "embedding": item.embedding,
                    "model_info": item.model_info.model_dump(), "context_prefix": item.context_prefix,
                    "level": item.level, "metadata": item.metadata,
                })
            self._request("POST", "/chunks/bulk", {"chunks": batch})
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps(sorted(completed | {document_hash})), encoding="utf-8")
        return len(records)