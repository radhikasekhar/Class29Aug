# Development Machine Setup

This guide prepares a Windows development machine for the Enterprise RAG Platform. It supports the four independently runnable projects: `chunker`, `ingest_client`, `rag_api`, and `rag_ui`.

The repository is currently at the planning stage. Commands marked **After P0** require the scaffold described in [PROMPTS.md](PROMPTS.md) to exist first.

## 1. Prerequisites

Install the following tools and confirm the listed commands work in PowerShell.

| Tool | Required version | Purpose | Verification command |
|---|---:|---|---|
| Git | 2.40+ | Source control | `git --version` |
| Python | 3.12+ | Application runtime and test runner | `python --version` |
| pip | Current | Python package installation | `python -m pip --version` |
| Docker Desktop | Current | PostgreSQL/pgvector, Ollama, API, and UI services | `docker version` |
| Docker Compose | v2 | Local multi-service startup | `docker compose version` |
| Ollama | Current | On-device embeddings and LLM generation | `ollama --version` |
| VS Code | Current | Recommended editor | Open the repository folder |

Docker Desktop must be running before starting the platform. Allocate at least 8 GB RAM to Docker; 16 GB or more is recommended when running an Ollama model locally.

## 2. Clone and Open the Repository

```powershell
git clone <repository-url> C:\Asphero\RAG_Project
Set-Location C:\Asphero\RAG_Project
code .
```

Confirm the active branch and working tree before making changes:

```powershell
git branch --show-current
git status
```

## 3. Python Environments

Each project is independently deployable. Create one virtual environment per project after P0 adds the project folders.

```powershell
# After P0
python -m venv chunker\.venv
python -m venv ingest_client\.venv
python -m venv rag_api\.venv
python -m venv rag_ui\.venv
```

Activate the environment for the project being developed:

```powershell
.\rag_api\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

If PowerShell blocks activation for your user account, run this once in a non-administrator PowerShell session:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## 4. Configure Environment Variables

**After P0**, create your untracked local configuration file from the example:

```powershell
Copy-Item .env.example .env
```

Use the following baseline values for an Ollama-first local setup. Do not commit `.env` or place real OpenAI keys in source files.

```dotenv
POSTGRES_DB=rag
POSTGRES_USER=rag
POSTGRES_PASSWORD=change-this-local-password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

OLLAMA_BASE_URL=http://localhost:11434
EMBEDDING_PROVIDER=ollama
EMBEDDING_MODEL=bge-m3
EMBEDDING_DIM=1024
LLM_PROVIDER=ollama
LLM_MODEL=qwen3

CHUNK_SIZE=800
CHUNK_OVERLAP=100
TOP_K=8

# Optional. Set only when using OpenAI.
OPENAI_API_KEY=
```

The embedding dimension is a schema-level decision. Keep `EMBEDDING_DIM` consistent with the vector column created by the database migration. Changing the model or dimension requires re-embedding the corpus.

## 5. Start Local Dependencies

Start Ollama and pull the models selected in `.env`:

```powershell
ollama serve
```

In a second PowerShell terminal:

```powershell
ollama pull bge-m3
ollama pull qwen3
ollama list
```

**After P0**, start the containerized platform services from the repository root:

```powershell
docker compose up --build -d
docker compose ps
docker compose logs --follow
```

Expected local endpoints after the relevant services are implemented:

| Service | URL | Check |
|---|---|---|
| PostgreSQL/pgvector | `localhost:5432` | `docker compose ps` shows healthy |
| Ollama | `http://localhost:11434` | `ollama list` shows selected models |
| FastAPI | `http://localhost:8000` | `Invoke-WebRequest http://localhost:8000/health` |
| FastAPI OpenAPI | `http://localhost:8000/docs` | Open in a browser |
| Streamlit | `http://localhost:8501` | Open in a browser |

Stop services when finished:

```powershell
docker compose down
```

Use `docker compose down -v` only when you intentionally want to delete local database data.

## 6. Database Setup

**After P0**, apply migrations using the API migration runner or the documented migration command. Confirm extensions, tables, and indexes were created:

```powershell
docker compose exec db psql -U $env:POSTGRES_USER -d $env:POSTGRES_DB -c "\dx"
docker compose exec db psql -U $env:POSTGRES_USER -d $env:POSTGRES_DB -c "\dt"
```

The expected schema includes the `vector` extension plus `collections`, `documents`, and `chunks` tables. The `chunks.embedding` vector dimension must match `EMBEDDING_DIM`.

## 7. Development Workflow

Work in phase order; do not begin a later phase until its checklist and test gate pass.

1. Review [SPEC.md](SPEC.md) and the project checklist under [checklists](checklists).
2. Activate the project virtual environment and install the project dependencies from its `pyproject.toml` or requirements file.
3. Implement one checklist task.
4. Add or update the focused test for that task.
5. Run the focused test and the relevant project test suite.
6. Run contract or integration tests when changing project boundaries.
7. Mark the checklist task complete only after checks pass.

Project test commands, once their test suites exist:

```powershell
pytest chunker/tests
pytest ingest_client/tests
pytest rag_api/tests
pytest rag_ui/tests
```

## 8. First End-to-End Run

**After P1**, use a non-sensitive sample document to exercise ingestion:

```powershell
python -m chunker --input data/inbox --out data/outbox --chunk-types semantic
python -m ingest_client --outbox data/outbox --api http://localhost:8000
```

Verify re-ingestion is idempotent by running the second command again and confirming document and chunk counts do not increase.

**After P2**, start the UI and query the sample document:

```powershell
streamlit run rag_ui/app.py
```

The expected outcome is a grounded response with citations that resolve to the source document and page locator.

## 9. Troubleshooting

| Symptom | Check | Resolution |
|---|---|---|
| `docker compose` cannot connect | Docker Desktop status | Start Docker Desktop and wait for the engine to be ready. |
| Ollama request fails | `ollama list` and `OLLAMA_BASE_URL` | Start `ollama serve`; pull the configured model; confirm port 11434 is free. |
| API cannot connect to PostgreSQL | `docker compose ps` and `.env` values | Confirm `db` is healthy and application containers use the Compose hostname, not `localhost`. |
| Vector insert fails | `EMBEDDING_DIM` and selected model | Align schema vector dimension with the configured embedding model; recreate/re-embed only with an intentional migration plan. |
| PowerShell blocks venv activation | Execution policy | Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`. |
| Tests use external services unexpectedly | Test configuration | Mock Ollama/OpenAI for unit tests; reserve Docker Compose for integration tests. |

## 10. Pre-Commit Check

Before committing, run the focused project test suite and inspect the pending change:

```powershell
git diff --check
pytest <project>/tests
git status
```

Never commit `.env`, API keys, raw internal documents, database volumes, or generated outbox artifacts.