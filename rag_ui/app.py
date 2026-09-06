import json
import os
from collections.abc import Iterator

import httpx
import streamlit as st


API_URL = os.getenv("RAG_API_BASE_URL", "http://localhost:8000")
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")


def search(query: str, top_k: int, chunk_types: list[str]) -> list[dict]:
    response = httpx.post(f"{API_URL}/search/hybrid", json={"query": query, "top_k": top_k, "chunk_types": chunk_types}, timeout=30)
    response.raise_for_status()
    return response.json()


def answer_stream(question: str, sources: list[dict], model: str) -> Iterator[str]:
    context = "\n\n".join(f"Source: {item['text']}" for item in sources)
    with httpx.stream("POST", f"{OLLAMA_URL}/api/generate", json={"model": model, "prompt": f"Answer only from the sources.\n{context}\n\nQuestion: {question}", "stream": True}, timeout=120) as response:
        response.raise_for_status()
        for line in response.iter_lines():
            if line:
                yield json.loads(line)["response"]


st.set_page_config(page_title="Internal search", page_icon=":material/search:", layout="wide")
st.title("Internal document search")
st.session_state.setdefault("messages", [])

with st.sidebar:
    provider = st.selectbox("Provider", ["Ollama", "OpenAI"], key="provider")
    model = st.text_input("Model", value="qwen3", key="model")
    top_k = st.slider("Retrieved chunks", min_value=1, max_value=20, value=8, key="top_k")
    chunk_types = st.multiselect("Chunk types", ["semantic", "contextual", "summary", "qa_pair", "factoid", "raptor"], default=["semantic"], key="chunk_types")
    st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.2, key="temperature")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if question := st.chat_input("Ask about internal documents", submit_mode="disable"):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)
    with st.chat_message("assistant"):
        try:
            with st.status("Searching documents", expanded=False) as status:
                sources = search(question, top_k, chunk_types)
                status.update(label=f"Retrieved {len(sources)} chunks", state="complete")
            if not sources:
                st.info("No matching documents were found.")
                response = "No matching documents were found."
            elif provider != "Ollama":
                response = "OpenAI answer streaming is not configured for this deployment."
                st.warning(response)
            else:
                response = st.write_stream(answer_stream(question, sources, model))
            for source in sources:
                locator = source.get("locator", {})
                with st.expander(f"{source.get('file_name', 'Source')} - page {locator.get('page_start', '?')}"):
                    st.write(source["text"])
        except httpx.HTTPError as error:
            response = "Retrieval is unavailable."
            st.error(f"{response} {error}")
    st.session_state.messages.append({"role": "assistant", "content": response})