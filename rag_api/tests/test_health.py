from fastapi.testclient import TestClient

from rag_api.app.main import create_app
from rag_api.app.settings import Settings


class FakeDatabase:
    def __init__(self, ready: bool) -> None:
        self.ready = ready
        self.opened = False

    def open(self) -> None:
        self.opened = True

    def close(self) -> None:
        self.opened = False

    def is_ready(self) -> bool:
        return self.ready


def make_client(ready: bool) -> TestClient:
    return TestClient(create_app(settings=Settings(), database=FakeDatabase(ready)))


def test_health_returns_ok_without_database_connection() -> None:
    with make_client(ready=False) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_returns_ready_when_database_is_available() -> None:
    with make_client(ready=True) as client:
        response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_ready_returns_service_unavailable_when_database_is_unavailable() -> None:
    with make_client(ready=False) as client:
        response = client.get("/ready")

    assert response.status_code == 503
    assert response.json() == {"status": "not_ready"}