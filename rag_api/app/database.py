import logging
from collections.abc import Iterator
from contextlib import contextmanager

from psycopg import Connection
from psycopg_pool import ConnectionPool

from rag_api.app.settings import Settings

logger = logging.getLogger(__name__)


class Database:
    """Owns the API's psycopg connection pool."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._pool: ConnectionPool | None = None

    def open(self) -> None:
        if self._pool is None:
            self._pool = ConnectionPool(
                conninfo=self._settings.database_url,
                min_size=1,
                max_size=5,
                timeout=self._settings.db_connect_timeout,
                open=True,
            )

    def close(self) -> None:
        if self._pool is not None:
            self._pool.close()
            self._pool = None

    @contextmanager
    def connection(self) -> Iterator[Connection]:
        if self._pool is None:
            raise RuntimeError("Database pool is not open")
        with self._pool.connection() as connection:
            yield connection

    @contextmanager
    def transaction(self) -> Iterator[Connection]:
        with self.connection() as connection:
            with connection.transaction():
                yield connection

    def is_ready(self) -> bool:
        if self._pool is None:
            return False
        try:
            with self._pool.connection() as connection:
                connection.execute("SELECT 1")
        except Exception:
            logger.warning("Database readiness check failed", exc_info=True)
            return False
        return True