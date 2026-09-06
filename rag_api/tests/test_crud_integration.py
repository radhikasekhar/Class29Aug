from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from rag_api.app.main import create_app
from rag_api.app.settings import Settings


class FakeEmbedder:
    def embed(self, text: str) -> list[float]:
        return [0.1] * 1024


@pytest.fixture
def client() -> Iterator[TestClient]:
    app = create_app(
        settings=Settings(
            db_host="localhost",
            db_port=5433,
            db_name="rag",
            db_user="rag",
            db_password="rag_dev_password",
        ),
        embedder=FakeEmbedder(),
    )
    with TestClient(app) as test_client:
        database = app.state.database
        with database.transaction() as connection:
            connection.execute("DELETE FROM chunks")
            connection.execute("DELETE FROM documents")
            connection.execute("DELETE FROM collections")
        yield test_client
        with database.transaction() as connection:
            connection.execute("DELETE FROM chunks")
            connection.execute("DELETE FROM documents")
            connection.execute("DELETE FROM collections")


def document_payload(collection_id: str) -> dict:
    return {
        "sha256": "a" * 64,
        "source_path": "data/inbox/handbook.pdf",
        "file_name": "handbook.pdf",
        "file_type": "pdf",
        "title": "Handbook",
        "markdown": "# Handbook",
        "page_count": 1,
        "collection_id": collection_id,
        "metadata": {"department": "people"},
    }


def chunk_payload(document_id: str) -> dict:
    return {
        "document_id": document_id,
        "chunk_type": "semantic",
        "chunk_index": 0,
        "text": "Employees must complete security training annually.",
        "token_count": 7,
        "locator": {"page_start": 1, "page_end": 1},
        "embedding": [0.1] * 1024,
        "model_info": {"embedding_model": "bge-m3"},
    }


def test_collection_document_and_chunk_lifecycle(client: TestClient) -> None:
    collection = client.post("/collections", json={"name": "Policies", "description": "Internal policies"})
    assert collection.status_code == 201
    collection_id = collection.json()["id"]

    updated_collection = client.patch(f"/collections/{collection_id}", json={"description": "Updated policies"})
    assert updated_collection.status_code == 200
    assert updated_collection.json()["description"] == "Updated policies"

    document = client.put("/documents", json=document_payload(collection_id))
    assert document.status_code == 200
    document_id = document.json()["id"]

    updated_document = client.patch(f"/documents/{document_id}", json={"status": "chunked"})
    assert updated_document.status_code == 200
    assert updated_document.json()["status"] == "chunked"

    created_chunks = client.post("/chunks/bulk", json={"chunks": [chunk_payload(document_id)]})
    assert created_chunks.status_code == 201
    chunk_id = created_chunks.json()["chunks"][0]["id"]

    listed_chunks = client.get(f"/documents/{document_id}/chunks")
    assert listed_chunks.status_code == 200
    assert [chunk["id"] for chunk in listed_chunks.json()] == [chunk_id]

    assert client.delete(f"/chunks/{chunk_id}").status_code == 204
    assert client.delete(f"/documents/{document_id}").status_code == 204
    assert client.delete(f"/collections/{collection_id}").status_code == 204


def test_document_upsert_is_idempotent(client: TestClient) -> None:
    collection_id = client.post("/collections", json={"name": "Engineering"}).json()["id"]
    first = client.put("/documents", json=document_payload(collection_id))
    second_payload = document_payload(collection_id) | {"title": "Updated Handbook"}
    second = client.put("/documents", json=second_payload)

    assert first.status_code == second.status_code == 200
    assert first.json()["id"] == second.json()["id"]
    assert second.json()["title"] == "Updated Handbook"


def test_chunk_rejects_wrong_embedding_dimension(client: TestClient) -> None:
    collection_id = client.post("/collections", json={"name": "Legal"}).json()["id"]
    document_id = client.put("/documents", json=document_payload(collection_id)).json()["id"]
    invalid_chunk = chunk_payload(document_id) | {"embedding": [0.0] * 10}

    response = client.post("/chunks/bulk", json={"chunks": [invalid_chunk]})

    assert response.status_code == 422


def test_vector_search_returns_indexed_chunk(client: TestClient) -> None:
    collection_id = client.post("/collections", json={"name": "Search"}).json()["id"]
    document_id = client.put("/documents", json=document_payload(collection_id)).json()["id"]
    chunk_response = client.post("/chunks/bulk", json={"chunks": [chunk_payload(document_id)]})
    assert chunk_response.status_code == 201
    assert len(client.get(f"/documents/{document_id}/chunks").json()) == 1

    response = client.post("/search/vector", json={"query": "security training", "top_k": 5})

    assert response.status_code == 200
    assert response.json()[0]["document_id"] == document_id


def test_hybrid_search_returns_indexed_chunk(client: TestClient) -> None:
    collection_id = client.post("/collections", json={"name": "Hybrid"}).json()["id"]
    document_id = client.put("/documents", json=document_payload(collection_id)).json()["id"]
    assert client.post("/chunks/bulk", json={"chunks": [chunk_payload(document_id)]}).status_code == 201

    response = client.post("/search/hybrid", json={"query": "security training", "top_k": 5})

    assert response.status_code == 200
    assert response.json()[0]["document_id"] == document_id


def test_upload_rejects_unsupported_file_type(client: TestClient) -> None:
    response = client.post("/documents/upload", files={"file": ("unsafe.exe", b"data")})

    assert response.status_code == 422