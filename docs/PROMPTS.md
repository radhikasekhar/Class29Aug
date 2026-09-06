---
name: enterprise-rag-specification
description: "Enterprise RAG Platform specification development workflow. Covers document chunking (docling + chonkie), derivative artifact generation (contextual, summary, QA pairs, factoids, RAPTOR), PostgreSQL/pgvector storage with full lineage tracking, FastAPI hybrid search (RRF), and Streamlit chat UI. Phased delivery P0–P4, configurable embeddings (OpenAI + Ollama), no SQLAlchemy."
---

# Enterprise RAG Platform — Specification & Implementation Prompts

**Date**: 2026-09-06 · **Status**: Live design · **Phase**: Specification complete (P0 Scaffold next)

---

## Core Design Decisions (Locked)

- **Embeddings**: both OpenAI + Ollama, configurable (default Ollama on-prem: bge-m3 / nomic-embed-text)
- **API topology**: single FastAPI service (CRUD + vector/hybrid search); chunker-ingest client and Streamlit are both clients
- **Search**: hybrid — pgvector dense + Postgres full-text (tsvector), fused with Reciprocal Rank Fusion (RRF)
- **Deployment**: Docker Compose (db, ollama, api, ui; CLI projects via native venv or compose profiles)
- **Scale**: < 1,000 documents — single node, no worker queue in v1
- **RAPTOR**: Phase 4 — schema/pipeline hooks designed now, implementation deferred
- **Ingestion**: CLI batch (primary) + API upload endpoint (files land in `data/inbox` for chunker)
- **Auth**: none (internal network)
- **DB access**: raw SQL via psycopg v3 + psycopg_pool — **NO SQLAlchemy**

---

## User Requests & Prompts (Today)

### 1. Initial Specification Request
**Prompt**: "create a specification document under C:\Asphero\RAG_Project - i want to build a enterprise level RAG solution for searching all my internal documents... multiple projects... Chunking & creating derivative artifacts: use docling to convert RAW docs, use chonkie to apply semantic chunking, for other derivative artifacts use ollama model runner. Create a highlevel spec for the above."

**Response**: High-level clarifying questions on:
- Embeddings provider (OpenAI, Ollama, or both)
- API topology (single or dual FastAPI services)
- Search strategy (vector-only or hybrid + RRF)
- Deployment approach (Docker Compose, local Windows, hybrid)
- Document scale
- RAPTOR timing (v1 vs. Phase 4)
- Ingestion methods (CLI batch, API upload, folder watcher)
- Auth requirements

**Decision Outcome**: All locked to above decisions.

---

### 2. Flow Chart Diagrams
**Prompt**: "add flow chat diagram to understand the flow"

**Response**: Delivered 4 Mermaid diagrams:
- System architecture (offline ingestion → Docker Compose serving)
- Chunking pipeline (raw doc → docling → chonkie → derivatives fan-out → JSONL outbox)
- Query request flow (user → Streamlit → API → hybrid search → LLM → streamed answer + citations)
- Phase dependency chart (P0 → P1 → P2 → P3 → P4)

---

### 3. Architecture Diagram
**Prompt**: "add architechture diagram"

**Response**: Full system architecture diagram showing:
- Offline ingestion: raw docs → docling → semantic chunking → Ollama derivatives
- Docker Compose platform: FastAPI + PostgreSQL/pgvector + Ollama
- Streamlit UI with configurable LLM (Ollama or OpenAI)
- Lineage tracking (documents → chunks → locators)

---

### 4. High-Level Design Document
**Prompt**: "write it as high level design document"

**Response**: Complete 14-section specification covering:
1. Purpose & Scope
2. System Architecture (with diagram)
3. Repository Layout
4. Data Model & Lineage (documents, chunks, collections tables; HNSW/GIN indexes)
5. Project 1 — chunker/ (docling, chonkie, Ollama derivatives)
6. Project 2 — ingest_client/ (JSONL → API, idempotent)
7. Project 3 — rag_api/ (FastAPI, raw SQL, hybrid search)
8. Project 4 — rag_ui/ (Streamlit chat, citations)
9. Configuration (pydantic-settings, .env.example)
10. Deployment (Docker Compose)
11. Phased Delivery (P0–P4 with exit criteria)
12. Non-Goals (v1)
13. Verification & Acceptance
14. Open Considerations

**Deliverable**: [docs/SPEC.md](docs/SPEC.md) — full 14-section design document with 4 Mermaid diagrams.

---

### 5. File Creation & Access
**Prompt**: "copy high level design document into docs folder"

**Response**: Created `docs/SPEC.md` with complete specification.

---

## Repository Structure (Per Specification)

```
RAG_Project/
├── docker-compose.yml          # db (pgvector), ollama, api, ui
├── .env.example                # shared config
├── docs/
│   └── SPEC.md                 # high-level design (this project's authority)
├── db/migrations/              # 001_init.sql, 002_schema.sql, etc.
├── shared/                     # pydantic contracts (Chunk, ChunkEnvelope, DTOs)
├── chunker/                    # Project 1 — CLI: python -m chunker --input ...
├── ingest_client/              # Project 2 — CLI: python -m ingest_client --outbox ...
├── rag_api/                    # Project 3 — FastAPI service
├── rag_ui/                     # Project 4 — Streamlit app
└── data/
    ├── inbox/                  # raw uploads
    ├── outbox/                 # chunker JSONL output
    └── samples/                # test corpus
```

---

## Phased Delivery Plan

| Phase | Scope | Exit Criteria |
|---|---|---|
| **P0 Scaffold** | folders, compose (db+ollama), migrations, shared contracts | `docker compose up` healthy |
| **P1 Core ingest** | rag_api CRUD, chunker (docling + semantic), ingest_client | PDF → chunks → DB end-to-end; sha256 idempotent |
| **P2 Search + UI** | embeddings at ingest, /search/vector, Streamlit chat (Ollama) | known-answer query → top-5 doc |
| **P3 Derivatives + hybrid** | contextual/summary/qa/factoid, /search/hybrid RRF, OpenAI option, citations | hybrid beats vector; citations resolve |
| **P4 RAPTOR + hardening** | RAPTOR impl, upload automation, eval harness | RAPTOR summaries retrievable |

---

## Key Data Model Features

**`documents` table**
- `id` (uuid PK), `sha256` (unique, idempotent re-ingest), `file_type`, `markdown` (docling output), `page_count`, `status` (uploaded/processing/chunked/indexed/failed), `collection_id` (FK)

**`chunks` table**
- `id` (uuid PK), `document_id` (FK), `parent_chunk_id` (self-FK for derivatives), `chunk_type` (semantic/contextual/summary/raptor/qa_pair/factoid), `text`, `embedding` (vector), `tsv` (generated tsvector), `locator` (jsonb: page/offset), `model_info` (reproducibility)

**Lineage rule**: every chunk → document + locator; derivatives → parent chunk via `parent_chunk_id`

**Indexes**: HNSW on embedding · GIN on tsv · btree on (document_id, chunk_type, parent_chunk_id)

---

## Implementation Prompts (For Upcoming Phases)

### Phase 0 Scaffold
```prompt
Create P0 Scaffold: 
- Folders: chunker/, ingest_client/, rag_api/, rag_ui/, db/migrations/, shared/
- docker-compose.yml with services: db (pgvector/pg16), ollama, (placeholder api & ui)
- .env.example with POSTGRES_*, OLLAMA_BASE_URL, OPENAI_API_KEY, EMBEDDING_*, LLM_*
- db/migrations/001_init.sql + 002_schema.sql (documents, chunks, collections tables with indexes)
- shared/models.py: ChunkEnvelope pydantic contract (for chunker → ingest_client handoff)
- Verify: `docker compose up` → all services healthy
```

### Phase 1 Core Ingest
```prompt
Implement P1 Core Ingest (PDF → chunks → DB end-to-end):
- chunker/: docling (PDF→markdown, page map) + chonkie SemanticChunker, output to JSONL
- rag_api/: FastAPI CRUD endpoints (PUT/GET/PATCH/DELETE /documents, POST /chunks/bulk)
- ingest_client/: read outbox JSONL, batch POST to API, idempotent by sha256
- Verify: upload PDF, run chunker, ingest, query DB; re-ingest same PDF → idempotent
```

### Phase 2 Search + UI
```prompt
Implement P2 Search + UI (embeddings + vector search + Streamlit):
- rag_api/: POST /search/vector (query → embedding → pgvector search, return top_k chunks)
- rag_ui/: Streamlit chat, call /search/vector, prompt with chunks, stream LLM answer (Ollama)
- Verify: known-answer query returns expected doc in top-5
```

### Phase 3 Derivatives + Hybrid
```prompt
Implement P3 Derivatives + Hybrid (contextual, summary, QA, factoids, RRF):
- chunker/: add --chunk-types contextual, summary, qa_pairs, factoids (all via Ollama)
- rag_api/: POST /search/hybrid (CTE vec + CTE fts + RRF score)
- rag_ui/: add sidebar filters (provider, model, chunk_type), hybrid search, citations UI
- Verify: hybrid beats vector-only on eval set; citations link to page
```

### Phase 4 RAPTOR + Hardening
```prompt
Implement P4 RAPTOR + Hardening:
- chunker/: implement RAPTOR tree (cluster → summarize → recurse) behind existing interface
- rag_api/: POST /documents/upload endpoint, auto-queue chunker
- Verify: RAPTOR level-1 summaries retrievable; upload→chunked doc appears; regression check passes
```

---

## Configuration Variables (.env.example)

```env
# Database
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_USER=rag_user
POSTGRES_PASSWORD=<random>
POSTGRES_DB=rag_db

# Ollama
OLLAMA_BASE_URL=http://ollama:11434

# OpenAI (optional, for UI LLM selection)
OPENAI_API_KEY=<your-key>

# Embedding
EMBEDDING_PROVIDER=ollama  # or openai
EMBEDDING_MODEL=bge-m3    # or nomic-embed-text, text-embedding-3-small
EMBEDDING_DIM=1024        # or 768, 1536 depending on model

# LLM Generation (chunker derivatives)
LLM_PROVIDER=ollama       # or openai
LLM_MODEL=qwen            # or llama, gemma
LLM_TEMPERATURE=0.7

# Chunking
CHUNK_SIZE=512
CHUNK_OVERLAP=50
TOP_K=5
```

---

## Quick Start (After P0 Scaffold)

```bash
# Terminal 1: spin up infrastructure
cd RAG_Project
docker compose up -d

# Terminal 2: chunk a PDF
cd chunker
python -m chunker --input ../data/samples --out ../data/outbox --chunk-types semantic

# Terminal 3: ingest to DB
cd ingest_client
python -m ingest_client --outbox ../data/outbox --api http://localhost:8000

# Terminal 4: run the UI
cd rag_ui
streamlit run app.py
```

---

## Related Files

- **Specification**: [docs/SPEC.md](docs/SPEC.md) — authority on design, data model, API, phases
- **Session Plan**: `/memories/session/plan.md` — locked decisions and planning
- **Untitled Prompt**: `untitled:plan-enterpriseRagSpecification.prompt.md` — working draft

---

## Next Action

**Approve SPEC.md or request adjustments, then initiate P0 Scaffold.**

Questions? Clarifications needed on data model, API endpoints, phasing, or config?
