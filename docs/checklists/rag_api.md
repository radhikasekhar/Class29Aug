# rag_api Checklist

Master tracker: [SPEC.md](../SPEC.md).

## End-of-Task Test Gate

Before marking any task complete, add or update its focused automated test, run it successfully, and run PostgreSQL/pgvector integration checks for persistence or search changes. Do not begin the next task until those checks pass.

## P0 Setup

- [x] Create the `rag_api/` project directory and this checklist.
- [x] Add the shared `api` service placeholder to `docker-compose.yml`.
- [x] Review the shared database and provider configuration in `.env.example`.
- [x] Add and apply PostgreSQL/pgvector migrations for collections, documents, chunks, and indexes.
- [x] Add project packaging, dependency declaration, and test layout.

## Planned Work

- [x] Create the FastAPI app and psycopg v3 data layer.
- [x] Add health and readiness endpoint tests.
- [x] Add migrations and CRUD endpoints.
- [x] Add collection, document, and chunk lifecycle integration tests.
- [x] Add `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, and `DB_PASSWORD` settings support and tests.
- [x] Add vector and hybrid RRF search endpoints.
- [x] Add validated document upload endpoint and tests.