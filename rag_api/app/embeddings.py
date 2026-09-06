import httpx

from rag_api.app.settings import Settings


class Embedder:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def embed(self, text: str) -> list[float]:
        if self.settings.embedding_provider != "ollama":
            raise RuntimeError("Only Ollama embeddings are implemented in v1")
        response = httpx.post(
            f"{self.settings.ollama_base_url}/api/embed",
            json={"model": self.settings.embedding_model, "input": text}, timeout=60,
        )
        response.raise_for_status()
        vector = response.json()["embeddings"][0]
        if len(vector) != self.settings.embedding_dim:
            raise ValueError("Embedding dimension does not match configured database dimension")
        return vector