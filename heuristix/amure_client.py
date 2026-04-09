"""amure-do HTTP client — bridge to Knowledge DB + Graph RAG."""
from __future__ import annotations

import httpx


class AmureClient:
    """HTTP client for the amure-do Rust server (knowledge graph + RAG + LLM routing)."""

    def __init__(self, base_url: str = "http://localhost:9090", timeout: float = 30):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(base_url=self.base_url, timeout=timeout)

    def health(self) -> dict:
        """Check amure-do health endpoint."""
        return self.client.get("/api/health").json()

    def is_connected(self) -> bool:
        """Return True if amure-do is reachable and healthy."""
        try:
            h = self.health()
            return h.get("status") == "ok"
        except Exception:
            return False

    # ── Graph CRUD ──────────────────────────────────────────────

    def add_node(
        self,
        kind: str,
        statement: str,
        keywords: list[str],
        metadata: dict | None = None,
        status: str = "Draft",
    ) -> dict:
        """Create a new knowledge node."""
        return self.client.post(
            "/api/graph/node",
            json={
                "kind": kind,
                "statement": statement,
                "keywords": keywords,
                "metadata": metadata or {},
                "status": status,
            },
        ).json()

    def update_node(
        self,
        node_id: str,
        status: str | None = None,
        metadata: dict | None = None,
        keywords: list[str] | None = None,
    ) -> dict:
        """Patch an existing node."""
        body: dict = {}
        if status:
            body["status"] = status
        if metadata:
            body["metadata"] = metadata
        if keywords:
            body["keywords"] = keywords
        return self.client.patch(f"/api/graph/node/{node_id}", json=body).json()

    def get_node(self, node_id: str) -> dict:
        """Retrieve a single node by ID."""
        return self.client.get(f"/api/graph/node/{node_id}").json()

    def delete_node(self, node_id: str) -> dict:
        """Delete a node."""
        return self.client.delete(f"/api/graph/node/{node_id}").json()

    def add_edge(self, source: str, target: str, kind: str, note: str = "") -> dict:
        """Create an edge between two nodes."""
        return self.client.post(
            "/api/graph/edge",
            json={"source": source, "target": target, "kind": kind, "note": note},
        ).json()

    # ── RAG Search ──────────────────────────────────────────────

    def search(
        self, query: str, top_k: int = 10, include_failed: bool = True
    ) -> list[dict]:
        """Semantic search over the knowledge graph."""
        resp = self.client.get(
            "/api/graph/search",
            params={"q": query, "top_k": top_k, "include_failed": include_failed},
        ).json()
        return resp.get("results", [])

    def walk(self, node_id: str, hops: int = 2) -> dict:
        """Walk the graph from a node up to N hops."""
        return self.client.get(
            f"/api/graph/walk/{node_id}", params={"hops": hops}
        ).json()

    def graph_summary(self) -> dict:
        """Get high-level graph statistics."""
        return self.client.get("/api/graph/summary").json()

    # ── Knowledge Utilization ───────────────────────────────────

    def check_failures(self, statement: str, keywords: list[str]) -> list[dict]:
        """Check if similar approaches have failed before."""
        resp = self.client.post(
            "/api/knowledge-util/check-failures",
            json={"statement": statement, "keywords": keywords},
        ).json()
        return resp.get("warnings", [])

    def detect_contradictions(self) -> dict:
        """Find contradictory claims in the knowledge graph."""
        return self.client.post(
            "/api/knowledge-util/detect-contradictions", json={}
        ).json()

    def suggest_combinations(self) -> dict:
        """Suggest promising combinations of existing knowledge."""
        return self.client.get("/api/knowledge-util/suggest-combinations").json()

    def auto_gap_claims(self) -> dict:
        """Automatically identify gaps and generate candidate claims."""
        return self.client.post(
            "/api/knowledge-util/auto-gap-claims", json={}
        ).json()

    # ── LLM (via amure-do) ─────────────────────────────────────

    def auto_tag(self, node_id: str) -> dict:
        """Use LLM to auto-tag a node with keywords."""
        return self.client.post(
            "/api/llm/auto-tag", json={"node_id": node_id}
        ).json()

    # ── Persistence ─────────────────────────────────────────────

    def save_graph(self) -> dict:
        """Persist the current graph state to disk."""
        return self.client.post("/api/graph/save", json={}).json()

    # ── Lifecycle ───────────────────────────────────────────────

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self.client.close()

    def __enter__(self) -> "AmureClient":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
