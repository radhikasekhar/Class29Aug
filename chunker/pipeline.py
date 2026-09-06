import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from uuid import uuid4

import httpx

from chunker.settings import Settings
from shared.models import ChunkEnvelope, ChunkType, FileType, Locator, ModelInfo

SUPPORTED_TYPES = {".pdf": FileType.PDF, ".docx": FileType.DOCX, ".html": FileType.HTML, ".htm": FileType.HTML, ".txt": FileType.TXT}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def convert(path: Path) -> tuple[str, FileType, int]:
    file_type = SUPPORTED_TYPES.get(path.suffix.lower())
    if file_type is None:
        raise ValueError(f"Unsupported file type: {path.suffix}")
    if file_type is FileType.TXT:
        return path.read_text(encoding="utf-8"), file_type, 1
    if file_type is FileType.HTML:
        source = path.read_text(encoding="utf-8")
        return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", source)).strip(), file_type, 1
    try:
        from docling.document_converter import DocumentConverter
    except ImportError as error:
        raise RuntimeError("Install docling to convert PDF and DOCX documents") from error
    result = DocumentConverter().convert(str(path))
    markdown = result.document.export_to_markdown()
    return markdown, file_type, max(1, markdown.count("\f") + 1)


def split_text(text: str, size: int, overlap: int) -> list[tuple[str, int, int]]:
    cleaned = re.sub(r"\s+", " ", text).strip()
    if not cleaned:
        return []
    chunks: list[tuple[str, int, int]] = []
    start = 0
    while start < len(cleaned):
        end = min(len(cleaned), start + size)
        if end < len(cleaned):
            boundary = cleaned.rfind(" ", start, end)
            end = boundary if boundary > start else end
        chunks.append((cleaned[start:end].strip(), start, end))
        if end == len(cleaned):
            break
        start = max(end - overlap, start + 1)
    return chunks


class Provider:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def embed(self, text: str) -> list[float]:
        if self.settings.embedding_provider != "ollama":
            raise RuntimeError("Only Ollama embeddings are implemented in v1")
        response = httpx.post(
            f"{self.settings.ollama_base_url}/api/embed",
            json={"model": self.settings.embedding_model, "input": text},
            timeout=60,
        )
        response.raise_for_status()
        embedding = response.json()["embeddings"][0]
        if len(embedding) != self.settings.embedding_dim:
            raise ValueError("Embedding dimension does not match EMBEDDING_DIM")
        return embedding

    def generate(self, prompt: str) -> str:
        response = httpx.post(
            f"{self.settings.ollama_base_url}/api/generate",
            json={"model": self.settings.llm_model, "prompt": prompt, "stream": False},
            timeout=120,
        )
        response.raise_for_status()
        return response.json()["response"].strip()


def process_document(path: Path, output_dir: Path, settings: Settings, provider: Provider, chunk_types: set[ChunkType]) -> Path:
    markdown, file_type, page_count = convert(path)
    document_hash = sha256(path)
    model_info = ModelInfo(
        embedding_provider=settings.embedding_provider,
        embedding_model=settings.embedding_model,
        embedding_dimension=settings.embedding_dim,
        generator_provider=settings.llm_provider,
        generator_model=settings.llm_model,
        prompt_version="1.0",
    )
    envelopes: list[ChunkEnvelope] = []
    for index, (text, char_start, char_end) in enumerate(split_text(markdown, settings.chunk_size, settings.chunk_overlap)):
        source_id = uuid4()
        locator = Locator(page_start=1, page_end=page_count, char_start=char_start, char_end=char_end)
        semantic = ChunkEnvelope(
            chunk_id=source_id, document_sha256=document_hash, source_path=str(path), file_name=path.name,
            file_type=file_type, title=path.stem, page_count=page_count, chunk_type=ChunkType.SEMANTIC,
            chunk_index=index, text=text, token_count=len(text.split()), locator=locator,
            model_info=model_info, embedding=provider.embed(text),
        )
        envelopes.append(semantic)
        for artifact_type, prompt in {
            ChunkType.CONTEXTUAL: f"Give a concise document context for this passage:\n{text}",
            ChunkType.QA_PAIR: f"Write one question and answer grounded in this passage:\n{text}",
            ChunkType.FACTOID: f"Extract one atomic fact from this passage:\n{text}",
        }.items():
            if artifact_type in chunk_types:
                artifact = provider.generate(prompt)
                envelopes.append(semantic.model_copy(update={"chunk_id": uuid4(), "chunk_type": artifact_type, "text": artifact, "token_count": len(artifact.split()), "embedding": provider.embed(artifact), "parent_chunk_id": source_id}))
    if ChunkType.SUMMARY in chunk_types and envelopes:
        summary = provider.generate("Summarize this document:\n" + "\n".join(item.text for item in envelopes if item.chunk_type is ChunkType.SEMANTIC))
        envelopes.append(envelopes[0].model_copy(update={"chunk_id": uuid4(), "chunk_type": ChunkType.SUMMARY, "chunk_index": len(envelopes), "text": summary, "token_count": len(summary.split()), "embedding": provider.embed(summary)}))
    output_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = output_dir / f"{document_hash}.jsonl"
    jsonl_path.write_text("\n".join(item.model_dump_json() for item in envelopes) + "\n", encoding="utf-8")
    manifest = {"document_sha256": document_hash, "source_path": str(path), "chunk_count": len(envelopes), "counts": Counter(item.chunk_type for item in envelopes), "model_info": model_info.model_dump()}
    (output_dir / f"{document_hash}.manifest.json").write_text(json.dumps(manifest, default=str, indent=2), encoding="utf-8")
    return jsonl_path