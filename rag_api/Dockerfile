FROM python:3.14-slim

WORKDIR /app
COPY shared /app/shared
COPY rag_api /app/rag_api
RUN pip install --no-cache-dir "fastapi>=0.115,<1" "psycopg[binary,pool]>=3.2,<4" "pydantic-settings>=2.7,<3" "uvicorn[standard]>=0.30,<1" "python-multipart>=0.0.9"

EXPOSE 8000
CMD ["uvicorn", "rag_api.app.main:app", "--host", "0.0.0.0", "--port", "8000"]