# ingest_client Checklist

Master tracker: [SPEC.md](../SPEC.md).

## End-of-Task Test Gate

Before marking any task complete, add or update its focused automated test, run it successfully, and run an API integration check when request behavior changes. Do not begin the next task until those checks pass.

## P0 Setup

- [x] Create the `ingest_client/` project directory and this checklist.
- [x] Review the shared `.env.example` configuration used by API ingestion.
- [x] Add the shared versioned `ChunkEnvelope` contract and passing serialization/lineage tests.
- [x] Add project packaging, dependency declaration, and test layout.

## Planned Work

- [x] Create the CLI and API settings loader.
- [x] Validate JSONL input.
- [x] Implement idempotent document and batch chunk ingestion.
- [x] Add retry, resume, dry-run behavior, and tests.