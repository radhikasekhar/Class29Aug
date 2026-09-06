# Enterprise RAG Platform Runbook

Follow these steps from the repository root, `C:\Asphero\RAG_Project`.

## 1. Prepare the Development Environment

Use the workspace virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install "pytest>=8" "fastapi>=0.115" "psycopg[binary,pool]>=3.2" "pydantic-settings>=2.7" "python-multipart>=0.0.9" "streamlit>=1.57" "httpx>=0.27"
```

Optional dependencies for PDF/DOCX conversion and semantic chunking:

```powershell
python -m pip install docling chonkie
```

## 2. Configure Local Settings

Create an untracked `.env` file from the template:

```powershell
Copy-Item .env.example .env
```

For the bundled Docker database, retain these values:

```dotenv
DB_HOST=localhost
DB_PORT=5433
DB_NAME=rag
DB_USER=rag
DB_PASSWORD=rag_dev_password
```

Change the password in both the database and `.env` for a non-default local environment. Do not commit `.env`.

## 3. Start the Platform

The Docker executable on this development machine is not on every PowerShell `PATH`. Use its full path:

```powershell
& "C:\Program Files\Docker\Docker\resources\bin\docker.exe" compose --env-file .env.example up --build -d
& "C:\Program Files\Docker\Docker\resources\bin\docker.exe" compose --env-file .env.example ps
```

The initial run downloads the Ollama image, approximately 3.7 GB. Wait until `db`, `ollama`, `api`, and `ui` are running. The database migration SQL is mounted into PostgreSQL and runs automatically on a new database volume.

## 4. Pull Ollama Models

Pull the configured embedding and generation models:

```powershell
& "C:\Program Files\Docker\Docker\resources\bin\docker.exe" compose exec ollama ollama pull bge-m3
& "C:\Program Files\Docker\Docker\resources\bin\docker.exe" compose exec ollama ollama pull qwen3
& "C:\Program Files\Docker\Docker\resources\bin\docker.exe" compose exec ollama ollama list
```

## 5. Verify Services

```powershell
Invoke-WebRequest http://localhost:8000/health
Invoke-WebRequest http://localhost:8000/ready
Start-Process http://localhost:8000/docs
Start-Process http://localhost:8501
```

Expected services:

| Service | Address |
|---|---|
| PostgreSQL/pgvector | `localhost:5433` |
| Ollama | `http://localhost:11434` |
| FastAPI | `http://localhost:8000` |
| Streamlit | `http://localhost:8501` |

## 6. Ingest Documents

Place non-sensitive source documents in `data/inbox/`. Then run the chunker and ingestion client:

```powershell
python -m chunker --input data/inbox --out data/outbox --chunk-types semantic
python -m ingest_client --outbox data/outbox --api http://localhost:8000 --state data/ingest-state.json
```

For derivatives, add supported types:

```powershell
python -m chunker --input data/inbox --out data/outbox --chunk-types semantic,contextual,qa_pair,factoid,summary
```

Run the ingestion command a second time to confirm completed documents are skipped by SHA-256 state tracking.

## 7. Use the Application

Open `http://localhost:8501`, choose the Ollama provider/model, and ask a question about an ingested document. The response should contain retrieval-backed citations with page locations.

## 8. Run Automated Tests

Run all project tests before committing or deploying:

```powershell
python -m pytest shared/tests chunker/tests ingest_client/tests rag_api/tests rag_ui/tests
```

Expected current result: 18 passing tests.

Run an individual project suite while developing:

```powershell
python -m pytest chunker/tests
python -m pytest ingest_client/tests
python -m pytest rag_api/tests
python -m pytest rag_ui/tests
```

## 9. Stop or Reset Services

Stop services while retaining local data:

```powershell
& "C:\Program Files\Docker\Docker\resources\bin\docker.exe" compose down
```

Remove local PostgreSQL and Ollama data only when an intentional reset is required:

```powershell
& "C:\Program Files\Docker\Docker\resources\bin\docker.exe" compose down -v
```