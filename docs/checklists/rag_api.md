# rag_api Checklist

Main progress tracker: [SPEC.md](../SPEC.md).

## End-of-Task Test Gate (Repeat for Every Task)

Before checking off **each** task below, complete this sequence:

- [ ] Add or update a focused automated test proving the task works.
- [ ] Run the focused test successfully.
- [ ] Run a PostgreSQL/pgvector integration check for persistence, migration, or search behavior.
- [ ] Review the result and fix failures before marking the task complete.
- [ ] Only then begin the next task or section.

## Foundation and Persistence

- [ ] Create the FastAPI application and Pydantic settings.
- [ ] Implement the raw psycopg v3 connection pool and SQL modules.
- [ ] Implement the migration runner and PostgreSQL/pgvector schema.
- [ ] Add health and readiness endpoints.
- [ ] Configure CORS, request-size limits, timeouts, and structured logging.
- [ ] Validate required configuration at startup and fail clearly on invalid embedding dimensions.
- [ ] Track applied migrations and prevent out-of-order schema changes.

## Data Integrity

- [ ] Enforce document status transitions and valid file types.
- [ ] Enforce `document_id`, locator, and parent-chunk lineage requirements.
- [ ] Verify parent chunks belong to the same source document.
- [ ] Use transactions for multi-record document and chunk operations.
- [ ] Define deletion behavior for documents, chunks, collections, and embeddings.

## Ingestion API

- [ ] Implement document, chunk, and collection CRUD endpoints.
- [ ] Implement idempotent document upsert by SHA-256.
- [ ] Implement bulk chunk upsert with lineage validation.
- [ ] Add `POST /documents/upload` to store raw files in the inbox.

## Retrieval API

- [ ] Add configured Ollama and OpenAI embedding providers.
- [ ] Implement `/search/vector` with filters.
- [ ] Implement `/search/hybrid` using full-text search and RRF fusion.
- [ ] Return document metadata, chunk text, and provenance locators.
- [ ] Reject query embeddings that do not match indexed model metadata.
- [ ] Validate `top_k`, chunk types, document filters, and collection filters.
- [ ] Return deterministic ranking behavior for equal scores.
- [ ] Expose no source content or database credentials in error responses.

## Operations and Release

- [ ] Log request ID, route, latency, result count, and error category without logging secrets.
- [ ] Publish database connection, migration, and provider health in readiness checks.
- [ ] Document API endpoints, JSON schemas, response codes, and local startup steps.
- [ ] Verify HNSW and GIN indexes exist after migrations.

## Verification

- [ ] Add request and response validation tests.
- [ ] Add CRUD, bulk-upsert, filter, and failure-mode tests.
- [ ] Add PostgreSQL/pgvector migration and search integration tests.
- [ ] Verify vector and hybrid known-answer queries return the expected document in the top five.
- [ ] Test invalid filters, provider outages, dimension mismatches, and transaction rollback.
- [ ] Test source-lineage constraints and cascade/delete behavior.
- [ ] Run `pytest rag_api/tests` successfully.