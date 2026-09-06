import json
from pathlib import Path

from chunker.pipeline import Provider, process_document
from chunker.settings import Settings
from shared.models import ChunkEnvelope, ChunkType


class FakeProvider(Provider):
    def embed(self, text: str) -> list[float]:
        return [0.0] * 4

    def generate(self, prompt: str) -> str:
        return "Generated artifact"


def test_txt_chunker_writes_contract_valid_jsonl_and_manifest(tmp_path: Path) -> None:
    source = tmp_path / "policy.txt"
    source.write_text("Security training is required every year. Employees must report incidents.", encoding="utf-8")
    settings = Settings(embedding_dim=4, chunk_size=40, chunk_overlap=5)

    output = process_document(source, tmp_path / "out", settings, FakeProvider(settings), {ChunkType.SEMANTIC, ChunkType.QA_PAIR})

    records = [ChunkEnvelope.model_validate_json(line) for line in output.read_text(encoding="utf-8").splitlines()]
    manifest = json.loads(output.with_suffix(".manifest.json").read_text(encoding="utf-8"))
    assert records[0].locator.char_start == 0
    assert any(record.chunk_type is ChunkType.QA_PAIR and record.parent_chunk_id for record in records)
    assert manifest["chunk_count"] == len(records)