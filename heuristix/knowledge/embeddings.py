"""Embedding-based knowledge retrieval using OpenAI embeddings."""
from __future__ import annotations

import json
import os
from pathlib import Path

import httpx
import numpy as np

EMBEDDING_MODEL = "text-embedding-3-small"  # cheap, fast, 1536 dims
STORE_PATH = Path("data/embeddings.json")


class EmbeddingStore:
    """Local embedding store with cosine similarity search."""

    def __init__(self, api_key: str = ""):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self.entries: list[dict] = []  # {id, text, one_liner, embedding, metadata}
        self._load()

    def _load(self) -> None:
        """Load embeddings from disk."""
        if STORE_PATH.exists():
            data = json.loads(STORE_PATH.read_text())
            self.entries = data.get("entries", [])

    def _save(self) -> None:
        """Persist embeddings to disk."""
        STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
        STORE_PATH.write_text(json.dumps({"entries": self.entries}, ensure_ascii=False))

    def _embed(self, text: str) -> list[float]:
        """Get embedding from OpenAI API."""
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY required for embeddings")
        resp = httpx.post(
            "https://api.openai.com/v1/embeddings",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={"model": EMBEDDING_MODEL, "input": text},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()["data"][0]["embedding"]

    def _embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Batch embed multiple texts."""
        if not texts:
            return []
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY required for embeddings")
        resp = httpx.post(
            "https://api.openai.com/v1/embeddings",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={"model": EMBEDDING_MODEL, "input": texts},
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()["data"]
        # Sort by index to maintain order
        data.sort(key=lambda x: x["index"])
        return [d["embedding"] for d in data]

    def add(
        self,
        node_id: str,
        text: str,
        one_liner: str,
        metadata: dict | None = None,
    ) -> None:
        """Add a knowledge entry with embedding."""
        # Check if already exists
        for entry in self.entries:
            if entry["id"] == node_id:
                return  # skip duplicate

        embedding = self._embed(f"{one_liner}\n{text}")
        self.entries.append({
            "id": node_id,
            "text": text,
            "one_liner": one_liner,
            "embedding": embedding,
            "metadata": metadata or {},
        })
        self._save()

    def search(
        self,
        query: str,
        top_k: int = 5,
        filter_fn: object = None,
    ) -> list[dict]:
        """Semantic search using cosine similarity."""
        if not self.entries:
            return []

        query_emb = np.array(self._embed(query))

        results = []
        for entry in self.entries:
            if filter_fn and not filter_fn(entry):
                continue
            entry_emb = np.array(entry["embedding"])
            # Cosine similarity
            sim = float(
                np.dot(query_emb, entry_emb)
                / (np.linalg.norm(query_emb) * np.linalg.norm(entry_emb) + 1e-10)
            )
            results.append({**entry, "similarity": sim})

        results.sort(key=lambda x: x["similarity"], reverse=True)
        # Remove embedding from results (too large to pass around)
        for r in results:
            r.pop("embedding", None)
        return results[:top_k]

    def search_failures(self, query: str, top_k: int = 3) -> list[dict]:
        """Search only failure entries."""
        return self.search(
            query,
            top_k,
            filter_fn=lambda e: e.get("metadata", {}).get("is_failure", False),
        )

    def search_mature(self, query: str, top_k: int = 3) -> list[dict]:
        """Search only Accepted/Active entries (mature knowledge)."""
        return self.search(
            query,
            top_k,
            filter_fn=lambda e: e.get("metadata", {}).get("status")
            in ("Accepted", "Active"),
        )

    @property
    def size(self) -> int:
        return len(self.entries)

    def clear(self) -> None:
        """Clear all entries."""
        self.entries = []
        self._save()
