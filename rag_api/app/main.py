from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from pathlib import Path

from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile, status
from fastapi.responses import JSONResponse

from rag_api.app.database import Database
from rag_api.app.embeddings import Embedder
from rag_api.app.repositories import (
    create_chunks,
    create_collection,
    delete_chunk,
    delete_collection,
    delete_document,
    get_collection,
    get_document,
    list_document_chunks,
    update_collection,
    update_document,
    upsert_document,
    vector_search,
    hybrid_search,
)
from rag_api.app.schemas import (
    ChunkBulkCreate,
    ChunkBulkResponse,
    ChunkResponse,
    CollectionCreate,
    CollectionResponse,
    CollectionUpdate,
    DocumentResponse,
    DocumentUpdate,
    DocumentUpsert,
    SearchRequest,
    SearchResult,
)
from rag_api.app.settings import Settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    database: Database = app.state.database
    database.open()
    try:
        yield
    finally:
        database.close()


def get_database(request: Request) -> Database:
    return request.app.state.database


def get_embedder(request: Request) -> Embedder:
    return request.app.state.embedder


def create_app(settings: Settings | None = None, database: Database | None = None, embedder: Embedder | None = None) -> FastAPI:
    app_settings = settings or Settings()
    app = FastAPI(title="Enterprise RAG API", version="0.1.0", lifespan=lifespan)
    app.state.settings = app_settings
    app.state.database = database or Database(app_settings)
    app.state.embedder = embedder or Embedder(app_settings)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/ready")
    def ready(database: Database = Depends(get_database)) -> JSONResponse:
        if database.is_ready():
            return JSONResponse(content={"status": "ready"})
        return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content={"status": "not_ready"})

    @app.post("/collections", response_model=CollectionResponse, status_code=status.HTTP_201_CREATED)
    def create_collection_endpoint(payload: CollectionCreate, database: Database = Depends(get_database)) -> dict:
        return create_collection(database, payload)

    @app.get("/collections/{collection_id}", response_model=CollectionResponse)
    def get_collection_endpoint(collection_id: str, database: Database = Depends(get_database)) -> dict:
        collection = get_collection(database, collection_id)
        if collection is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")
        return collection

    @app.patch("/collections/{collection_id}", response_model=CollectionResponse)
    def update_collection_endpoint(
        collection_id: str, payload: CollectionUpdate, database: Database = Depends(get_database)
    ) -> dict:
        collection = update_collection(database, collection_id, payload)
        if collection is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")
        return collection

    @app.delete("/collections/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_collection_endpoint(collection_id: str, database: Database = Depends(get_database)) -> None:
        if not delete_collection(database, collection_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")

    @app.put("/documents", response_model=DocumentResponse)
    def upsert_document_endpoint(payload: DocumentUpsert, database: Database = Depends(get_database)) -> dict:
        return upsert_document(database, payload)

    @app.get("/documents/{document_id}", response_model=DocumentResponse)
    def get_document_endpoint(document_id: str, database: Database = Depends(get_database)) -> dict:
        document = get_document(database, document_id)
        if document is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        return document

    @app.patch("/documents/{document_id}", response_model=DocumentResponse)
    def update_document_endpoint(
        document_id: str, payload: DocumentUpdate, database: Database = Depends(get_database)
    ) -> dict:
        document = update_document(database, document_id, payload)
        if document is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        return document

    @app.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_document_endpoint(document_id: str, database: Database = Depends(get_database)) -> None:
        if not delete_document(database, document_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    @app.post("/chunks/bulk", response_model=ChunkBulkResponse, status_code=status.HTTP_201_CREATED)
    def create_chunks_endpoint(payload: ChunkBulkCreate, database: Database = Depends(get_database)) -> dict:
        try:
            return {"chunks": create_chunks(database, payload.chunks)}
        except ValueError as error:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(error)) from error

    @app.get("/documents/{document_id}/chunks", response_model=list[ChunkResponse])
    def list_document_chunks_endpoint(document_id: str, database: Database = Depends(get_database)) -> list[dict]:
        return list_document_chunks(database, document_id)

    @app.delete("/chunks/{chunk_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_chunk_endpoint(chunk_id: str, database: Database = Depends(get_database)) -> None:
        if not delete_chunk(database, chunk_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chunk not found")

    @app.post("/search/vector", response_model=list[SearchResult])
    def search_vector_endpoint(
        payload: SearchRequest, database: Database = Depends(get_database), embedder: Embedder = Depends(get_embedder)
    ) -> list[dict]:
        return vector_search(database, embedder.embed(payload.query), payload.top_k)

    @app.post("/search/hybrid", response_model=list[SearchResult])
    def search_hybrid_endpoint(
        payload: SearchRequest, database: Database = Depends(get_database), embedder: Embedder = Depends(get_embedder)
    ) -> list[dict]:
        return hybrid_search(database, payload.query, embedder.embed(payload.query), payload.top_k)

    @app.post("/documents/upload", status_code=status.HTTP_201_CREATED)
    def upload_document(file: UploadFile = File(...)) -> dict[str, str]:
        suffix = Path(file.filename or "").suffix.lower()
        if suffix not in {".pdf", ".docx", ".html", ".htm", ".txt"}:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Unsupported file type")
        inbox = Path("data/inbox")
        inbox.mkdir(parents=True, exist_ok=True)
        target = inbox / Path(file.filename or "upload").name
        target.write_bytes(file.file.read())
        return {"status": "uploaded", "path": str(target)}

    return app


app = create_app()