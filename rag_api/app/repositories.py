from collections.abc import Sequence
from typing import Any
from uuid import UUID

from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from rag_api.app.database import Database
from rag_api.app.schemas import ChunkCreate, CollectionCreate, CollectionUpdate, DocumentUpdate, DocumentUpsert


def _vector_literal(values: Sequence[float]) -> str:
    return "[" + ",".join(str(value) for value in values) + "]"


def create_collection(database: Database, payload: CollectionCreate) -> dict[str, Any]:
    with database.connection() as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                "INSERT INTO collections (name, description) VALUES (%s, %s) RETURNING id, name, description",
                (payload.name, payload.description),
            )
            return cursor.fetchone()


def get_collection(database: Database, collection_id: UUID) -> dict[str, Any] | None:
    with database.connection() as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute("SELECT id, name, description FROM collections WHERE id = %s", (collection_id,))
            return cursor.fetchone()


def update_collection(database: Database, collection_id: UUID, payload: CollectionUpdate) -> dict[str, Any] | None:
    values = payload.model_dump(exclude_unset=True)
    if not values:
        return get_collection(database, collection_id)
    assignments = ", ".join(f"{column} = %s" for column in values)
    parameters = [*values.values(), collection_id]
    with database.connection() as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                f"UPDATE collections SET {assignments}, updated_at = now() WHERE id = %s RETURNING id, name, description",
                parameters,
            )
            return cursor.fetchone()


def delete_collection(database: Database, collection_id: UUID) -> bool:
    with database.connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM collections WHERE id = %s", (collection_id,))
            return cursor.rowcount == 1


def upsert_document(database: Database, payload: DocumentUpsert) -> dict[str, Any]:
    values = payload.model_dump()
    values["metadata"] = Jsonb(values["metadata"])
    columns = ", ".join(values)
    placeholders = ", ".join("%s" for _ in values)
    updates = ", ".join(f"{column} = EXCLUDED.{column}" for column in values if column != "sha256")
    query = f"""
        INSERT INTO documents ({columns}) VALUES ({placeholders})
        ON CONFLICT (sha256) DO UPDATE SET {updates}, updated_at = now()
        RETURNING id, sha256, source_path, file_name, file_type, title, markdown,
                  page_count, status, collection_id, metadata
    """
    with database.connection() as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(query, list(values.values()))
            return cursor.fetchone()


def get_document(database: Database, document_id: UUID) -> dict[str, Any] | None:
    with database.connection() as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """SELECT id, sha256, source_path, file_name, file_type, title, markdown,
                          page_count, status, collection_id, metadata
                   FROM documents WHERE id = %s""",
                (document_id,),
            )
            return cursor.fetchone()


def update_document(database: Database, document_id: UUID, payload: DocumentUpdate) -> dict[str, Any] | None:
    values = payload.model_dump(exclude_unset=True)
    if not values:
        return get_document(database, document_id)
    if "metadata" in values and values["metadata"] is not None:
        values["metadata"] = Jsonb(values["metadata"])
    assignments = ", ".join(f"{column} = %s" for column in values)
    parameters = [*values.values(), document_id]
    with database.connection() as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                f"""UPDATE documents SET {assignments}, updated_at = now() WHERE id = %s
                    RETURNING id, sha256, source_path, file_name, file_type, title, markdown,
                              page_count, status, collection_id, metadata""",
                parameters,
            )
            return cursor.fetchone()


def delete_document(database: Database, document_id: UUID) -> bool:
    with database.connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM documents WHERE id = %s", (document_id,))
            return cursor.rowcount == 1


def create_chunks(database: Database, chunks: list[ChunkCreate]) -> list[dict[str, Any]]:
    response: list[dict[str, Any]] = []
    with database.transaction() as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            for chunk in chunks:
                if chunk.parent_chunk_id is not None:
                    cursor.execute("SELECT document_id FROM chunks WHERE id = %s", (chunk.parent_chunk_id,))
                    parent = cursor.fetchone()
                    if parent is None or parent["document_id"] != chunk.document_id:
                        raise ValueError("parent_chunk_id must belong to the same document")
                cursor.execute(
                    """INSERT INTO chunks (
                           document_id, parent_chunk_id, chunk_type, chunk_index, text, token_count,
                           context_prefix, level, locator, embedding, model_info, metadata
                       ) VALUES (
                           %(document_id)s, %(parent_chunk_id)s, %(chunk_type)s, %(chunk_index)s,
                           %(text)s, %(token_count)s, %(context_prefix)s, %(level)s, %(locator)s,
                           %(embedding)s::vector, %(model_info)s, %(metadata)s
                       ) ON CONFLICT (document_id, chunk_type, chunk_index, parent_chunk_id)
                       DO UPDATE SET text = EXCLUDED.text, token_count = EXCLUDED.token_count,
                           context_prefix = EXCLUDED.context_prefix, level = EXCLUDED.level,
                           locator = EXCLUDED.locator, embedding = EXCLUDED.embedding,
                           model_info = EXCLUDED.model_info, metadata = EXCLUDED.metadata
                       RETURNING id, document_id, parent_chunk_id, chunk_type, chunk_index, text,
                                 token_count, locator, model_info, context_prefix, level, metadata""",
                    {
                        **chunk.model_dump(),
                        "locator": Jsonb(chunk.locator),
                        "embedding": _vector_literal(chunk.embedding),
                        "model_info": Jsonb(chunk.model_info),
                        "metadata": Jsonb(chunk.metadata),
                    },
                )
                response.append(cursor.fetchone())
    return response


def list_document_chunks(database: Database, document_id: UUID) -> list[dict[str, Any]]:
    with database.connection() as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """SELECT id, document_id, parent_chunk_id, chunk_type, chunk_index, text,
                          token_count, locator, model_info, context_prefix, level, metadata
                   FROM chunks WHERE document_id = %s ORDER BY chunk_index, created_at""",
                (document_id,),
            )
            return list(cursor.fetchall())


def delete_chunk(database: Database, chunk_id: UUID) -> bool:
    with database.connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM chunks WHERE id = %s", (chunk_id,))
            return cursor.rowcount == 1


def vector_search(database: Database, vector: list[float], top_k: int) -> list[dict[str, Any]]:
    with database.connection() as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """SELECT id, document_id, parent_chunk_id, chunk_type, chunk_index, text, token_count,
                          locator, model_info, context_prefix, level, metadata, 1 - (embedding <=> %s::vector) AS score
                   FROM chunks ORDER BY embedding <=> %s::vector LIMIT %s""",
                (_vector_literal(vector), _vector_literal(vector), top_k),
            )
            return list(cursor.fetchall())


def hybrid_search(database: Database, query: str, vector: list[float], top_k: int) -> list[dict[str, Any]]:
    with database.connection() as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """WITH vector_ranked AS (
                       SELECT id, row_number() OVER (ORDER BY embedding <=> %s::vector) AS rank
                       FROM chunks LIMIT %s
                   ), text_ranked AS (
                       SELECT id, row_number() OVER (ORDER BY ts_rank(tsv, plainto_tsquery('english', %s)) DESC) AS rank
                       FROM chunks WHERE tsv @@ plainto_tsquery('english', %s) LIMIT %s
                   ), fused AS (
                       SELECT id, sum(score) AS score FROM (
                           SELECT id, 1.0 / (60 + rank) AS score FROM vector_ranked
                           UNION ALL SELECT id, 1.0 / (60 + rank) AS score FROM text_ranked
                       ) ranks GROUP BY id
                   )
                   SELECT c.id, c.document_id, c.parent_chunk_id, c.chunk_type, c.chunk_index, c.text,
                          c.token_count, c.locator, c.model_info, c.context_prefix, c.level, c.metadata, fused.score
                   FROM fused JOIN chunks c ON c.id = fused.id ORDER BY fused.score DESC LIMIT %s""",
                (_vector_literal(vector), top_k * 3, query, query, top_k * 3, top_k),
            )
            return list(cursor.fetchall())