FROM python:3.14-slim

WORKDIR /app
COPY rag_ui /app/rag_ui
RUN pip install --no-cache-dir "streamlit>=1.57" "httpx>=0.27,<1"

EXPOSE 8501
CMD ["streamlit", "run", "rag_ui/app.py", "--server.address=0.0.0.0", "--server.port=8501"]