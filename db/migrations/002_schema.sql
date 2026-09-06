CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TYPE document_file_type AS ENUM ('pdf', 'docx', 'html', 'txt');
CREATE TYPE document_status AS ENUM ('uploaded', 'processing', 'chunked', 'indexed', 'failed');
CREATE TYPE chunk_kind AS ENUM ('semantic', 'contextual', 'summary', 'raptor', 'qa_pair', 'factoid');

CREATE TABLE collections (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name text NOT NULL UNIQUE,
    description text,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE documents (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    sha256 text NOT NULL UNIQUE CHECK (sha256 ~ '^[a-f0-9]{64}$'),
    source_path text NOT NULL,
    file_name text NOT NULL,
    file_type document_file_type NOT NULL,
    title text,
    markdown text,
    page_count integer NOT NULL DEFAULT 0 CHECK (page_count >= 0),
    status document_status NOT NULL DEFAULT 'uploaded',
    collection_id uuid REFERENCES collections(id) ON DELETE SET NULL,
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE chunks (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id uuid NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    parent_chunk_id uuid REFERENCES chunks(id) ON DELETE CASCADE,
    chunk_type chunk_kind NOT NULL,
    chunk_index integer NOT NULL CHECK (chunk_index >= 0),
    text text NOT NULL CHECK (length(trim(text)) > 0),
    token_count integer NOT NULL DEFAULT 0 CHECK (token_count >= 0),
    context_prefix text,
    level integer NOT NULL DEFAULT 0 CHECK (level >= 0),
    locator jsonb NOT NULL DEFAULT '{}'::jsonb,
    embedding vector(1024) NOT NULL,
    tsv tsvector GENERATED ALWAYS AS (to_tsvector('english', text)) STORED,
    model_info jsonb NOT NULL DEFAULT '{}'::jsonb,
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE NULLS NOT DISTINCT (document_id, chunk_type, chunk_index, parent_chunk_id)
);

CREATE INDEX documents_collection_id_idx ON documents (collection_id);
CREATE INDEX chunks_document_id_idx ON chunks (document_id);
CREATE INDEX chunks_chunk_type_idx ON chunks (chunk_type);
CREATE INDEX chunks_parent_chunk_id_idx ON chunks (parent_chunk_id);
CREATE INDEX chunks_tsv_idx ON chunks USING gin (tsv);
CREATE INDEX chunks_embedding_hnsw_idx ON chunks USING hnsw (embedding vector_cosine_ops);