# chunker Checklist

Master tracker: [SPEC.md](../SPEC.md).

## End-of-Task Test Gate

Before marking any task complete, add or update its focused automated test, run it successfully, and run shared-contract validation when output behavior changes. Do not begin the next task until those checks pass.

## P0 Setup

- [x] Create the `chunker/` project directory and this checklist.
- [x] Review the shared `.env.example` configuration used by chunking and derivative generation.
- [x] Add the shared versioned `ChunkEnvelope` contract and passing serialization/lineage tests.
- [x] Add project packaging, dependency declaration, and test layout.

## Planned Work

- [x] Create the CLI and settings loader.
- [x] Convert source documents with Docling and preserve provenance.
- [x] Create semantic chunks with a deterministic fallback.
- [x] Write validated JSONL and manifest output.
- [x] Add derivative artifact generation and tests.