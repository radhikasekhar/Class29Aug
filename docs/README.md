# Enterprise RAG Platform — Documentation

This folder contains all design and specification documents for the enterprise RAG solution.

## Files

### [SPEC.md](SPEC.md)
**The authority document.** Complete 14-section high-level design covering:
- System architecture, data model, lineage, and all 4 projects
- Project 1 (chunker): docling + chonkie + Ollama derivatives
- Project 2 (ingest_client): idempotent batch ingestion
- Project 3 (rag_api): FastAPI with raw SQL, hybrid search, RRF
- Project 4 (rag_ui): Streamlit chat with citations
- Phased delivery plan (P0–P4) with exit criteria per phase
- Configuration and deployment (Docker Compose)

**4 Mermaid diagrams**: system architecture, chunking pipeline, query flow, phase dependencies.

**Read this first** to understand the full system design.

---

### [PROMPTS.md](PROMPTS.md)
**Conversation log & implementation guide.** Captures:
- All 8 prompts and clarifying questions from the design session
- Locked design decisions (embeddings, API topology, search strategy, etc.)
- Repository structure and phased delivery table
- Data model features (documents, chunks, lineage)
- Implementation prompts for each phase (P0–P4)
- Configuration variables (.env.example)
- Quick start script

**Use this** to understand what was discussed and to guide implementation.

---

## Quick Navigation

### For Architecture Understanding
→ Start with [SPEC.md](SPEC.md) **Section 2** (System Architecture) and review the 4 Mermaid diagrams.

### For Implementation Sequencing
→ [SPEC.md](SPEC.md) **Section 11** (Phased Delivery) + [PROMPTS.md](PROMPTS.md) Implementation Prompts section.

### For Data Model Details
→ [SPEC.md](SPEC.md) **Section 4** (Data Model & Lineage) — documents, chunks, collections, indexes, lineage rules.

### For Configuration
→ [PROMPTS.md](PROMPTS.md) Configuration Variables section, or [SPEC.md](SPEC.md) **Section 9** (Configuration).

### For API Endpoints
→ [SPEC.md](SPEC.md) **Section 7** (Project 3 — rag_api) — full endpoint list and hybrid search SQL.

---

## Phased Delivery At A Glance

| Phase | Goal | Duration |
|---|---|---|
| **P0** | Scaffold | 1–2 days |
| **P1** | Core ingest (PDF→DB) | 2–3 days |
| **P2** | Search + UI | 2–3 days |
| **P3** | Derivatives + hybrid | 3–4 days |
| **P4** | RAPTOR + hardening | 2–3 days |

---

## Status

- ✅ Specification complete (SPEC.md finalized)
- ✅ Prompts & decisions recorded (PROMPTS.md)
- ⏳ Ready for P0 Scaffold implementation

---

## Key Design Principles

1. **Single API service** — one FastAPI app owns all DB access; chunker and UI are clients
2. **Lineage is non-negotiable** — every chunk traces to source document + locator
3. **File-based handoff** — chunker → JSONL → API (decoupled, testable)
4. **Provider-agnostic AI** — embeddings & LLM configurable (Ollama default, OpenAI optional)
5. **Raw SQL** — psycopg v3, no SQLAlchemy
6. **Hybrid search** — pgvector + tsvector, fused with RRF (Reciprocal Rank Fusion)

---

## Contact / Questions

For clarifications on design, see the decision rationale in [PROMPTS.md](PROMPTS.md) or request adjustments to [SPEC.md](SPEC.md).

**Next step**: Approve SPEC.md and initiate P0 Scaffold.
