# Enterprise RAG Platform - Implementation Checklist

Use this document to track overall delivery. Mark a task complete by changing `- [ ]` to `- [x]`. A phase is complete only when its required automated tests pass.

## End-of-Task Test Gate (Repeat for Every Task)

Before checking off **each** task below, complete this sequence:

- [ ] Add or update a focused automated test proving the task works.
- [ ] Run the focused test successfully.
- [ ] Run applicable shared-contract or integration checks when the task crosses a project boundary.
- [ ] Review the result and fix failures before marking the task complete.
- [ ] Only then begin the next task, section, or delivery phase.

## Main Document Checklist

- [ ] Define shared architecture, data model, and JSONL/API contracts.
- [ ] Create the repository scaffold and shared configuration.
- [ ] Create PostgreSQL/pgvector migrations and verify they apply successfully.
- [ ] Configure Docker Compose for PostgreSQL/pgvector, Ollama, `rag_api`, and `rag_ui`.
- [ ] Add representative, non-sensitive PDF, HTML, and TXT test documents.
- [ ] Configure CI to run project, contract, and end-to-end tests.
- [ ] Verify the full `chunker -> ingest_client -> rag_api -> rag_ui` flow.

## Project 1: `chunker`

- [ ] Create the CLI entry point and configuration loader.
- [ ] Convert PDF, DOCX, and HTML with Docling; pass TXT through.
- [ ] Preserve page, character-offset, and heading-path provenance.
- [ ] Create semantic chunks with Chonkie.
- [ ] Write versioned JSONL output and per-document manifests.
- [ ] Generate contextual, summary, QA-pair, and factoid artifacts with Ollama.
- [ ] Add the RAPTOR interface stub and implement it in the hardening phase.
- [ ] Add unit and fixture tests for conversion, provenance, chunks, JSONL, and artifact parsing.
- [ ] Verify every output chunk has valid type, source locator, and lineage metadata.

## Project 2: `ingest_client`

- [ ] Create the CLI entry point and API configuration loader.
- [ ] Read and validate JSONL envelopes before making API requests.
- [ ] Upsert documents by SHA-256 and submit chunks in configurable batches.
- [ ] Implement retries, exponential backoff, dry-run, and resumable state tracking.
- [ ] Reject invalid envelopes without calling the API.
- [ ] Add unit tests for validation, batching, retry behavior, state, and idempotency.
- [ ] Verify repeat ingestion of the same outbox creates no duplicate records.

## Project 3: `rag_api`

- [ ] Create the FastAPI app, Pydantic settings, and raw psycopg v3 data layer.
- [ ] Implement the migration runner and PostgreSQL/pgvector schema.
- [ ] Implement document, chunk, and collection CRUD endpoints.
- [ ] Implement bulk chunk upsert with lineage validation.
- [ ] Add configured Ollama and OpenAI embedding providers.
- [ ] Implement `/search/vector` and `/search/hybrid` with full-text RRF fusion.
- [ ] Implement `/health` and `/ready` endpoints.
- [ ] Add API unit tests and PostgreSQL/pgvector integration tests.
- [ ] Verify a known-answer query returns its expected document in the top five results.

## Project 4: `rag_ui`

- [ ] Create the Streamlit chat app and settings loader.
- [ ] Add provider, model, top-k, chunk-type, collection, and temperature controls.
- [ ] Send search requests to `rag_api` and show retrieval failures.
- [ ] Maintain chat history with `st.session_state`.
- [ ] Stream grounded LLM answers.
- [ ] Render expandable citations with document name, page, and chunk text.
- [ ] Add Streamlit `AppTest` coverage for controls, requests, streaming, citations, and errors.
- [ ] Verify an end-to-end question produces an answer with page-level citations.

## Final Acceptance

- [ ] All four project test suites pass.
- [ ] Shared contract tests pass.
- [ ] Compose-backed end-to-end tests pass for PDF, HTML, and TXT samples.
- [ ] SHA-256 re-ingestion is idempotent.
- [ ] Hybrid search passes the known-answer evaluation set.
- [ ] Citations resolve to the correct source document and page.
