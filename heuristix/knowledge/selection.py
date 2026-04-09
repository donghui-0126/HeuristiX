"""Select relevant knowledge from amure-do for evolution context injection."""
from __future__ import annotations

from typing import TYPE_CHECKING

from rich.console import Console

from heuristix.knowledge.embeddings import EmbeddingStore

if TYPE_CHECKING:
    from heuristix.amure_client import AmureClient
    from heuristix.evolution.population import Individual

_console = Console()


class KnowledgeSelector:
    """Query knowledge store to build context for mutation/crossover."""

    def __init__(
        self,
        amure_client: AmureClient | None = None,
        embedding_store: EmbeddingStore | None = None,
    ):
        self.amure = amure_client
        self.embeddings = embedding_store or EmbeddingStore()

    def get_context(
        self, individual: Individual, include_failures: bool = True
    ) -> dict[str, str]:
        """Build a knowledge context dict using embedding similarity.

        Returns:
            {"knowledge": str, "failures": str, "n_knowledge": int, "n_failures": int}
        """
        query = f"{individual.thought}\n{individual.code[:200]}"

        # 1. Search for relevant knowledge (prefer mature, fallback to all)
        knowledge_items: list[dict] = []
        try:
            knowledge_items = self.embeddings.search_mature(query, top_k=2)
            if not knowledge_items:
                # No mature items yet — search non-failure entries, prefer Active over Draft
                all_items = self.embeddings.search_insights(query, top_k=4)
                all_items.sort(key=lambda x: {"Accepted": 0, "Active": 1, "Draft": 2}.get(
                    x.get("metadata", {}).get("status", "Draft"), 3))
                knowledge_items = all_items[:2]
        except Exception:
            pass

        # 2. Search for failure warnings (top 2)
        failure_items: list[dict] = []
        if include_failures:
            try:
                failure_items = self.embeddings.search_failures(query, top_k=2)
            except Exception:
                pass

        # 2b. Enrich with graph context (best-effort)
        knowledge_items = self._enrich_with_graph(knowledge_items)
        failure_items = self._enrich_with_graph(failure_items)

        # 3. Fallback to amure-db token search if no embedding results
        if not knowledge_items and self.amure:
            try:
                keywords = self._extract_keywords(individual)
                kw_query = " ".join(keywords) if keywords else "job shop scheduling heuristic"
                results = self.amure.search(kw_query, top_k=5, include_failed=False)
                results.sort(
                    key=lambda r: {"Accepted": 0, "Active": 1, "Draft": 2}.get(
                        r.get("status", "Draft"), 3
                    )
                )
                for r in results[:2]:
                    status = r.get("status", "Draft")
                    statement = r.get("statement", "")
                    knowledge_items.append({
                        "one_liner": statement.split(".")[0] + "." if statement else "",
                        "text": statement,
                        "similarity": 0.0,
                        "metadata": {"status": status},
                    })
            except Exception:
                pass

        # 4. Format context
        knowledge_str = ""
        if knowledge_items:
            knowledge_str = "## Proven insights (from previous experiments):\n"
            for item in knowledge_items:
                graph_ctx = item.get("graph_context", "")
                knowledge_str += (
                    f"- [{item.get('one_liner', '')}] (sim={item.get('similarity', 0):.2f})\n"
                    f"  {item['text'][:150]}\n"
                )
                if graph_ctx:
                    knowledge_str += f"  Context: {graph_ctx}\n"

        failure_str = ""
        if failure_items:
            failure_str = "## AVOID these approaches (previously failed):\n"
            for item in failure_items:
                graph_ctx = item.get("graph_context", "")
                failure_str += (
                    f"- {item.get('one_liner', '')}\n"
                    f"  {item['text'][:150]}\n"
                )
                if graph_ctx:
                    failure_str += f"  Context: {graph_ctx}\n"

        # 5. Suggestions from amure-db (unchanged)
        suggestion_str = ""
        if self.amure:
            try:
                suggestions = self.amure.suggest_combinations()
                combos = suggestions.get("combinations", [])
                if combos:
                    suggestion_str = "\n".join(
                        f"- {c.get('description', str(c))}" for c in combos[:3]
                    )
            except Exception:
                pass

        # Log
        sim_strs = [f"{x.get('similarity', 0):.2f}" for x in knowledge_items]
        _console.print(
            f"  [dim][RAG] {len(knowledge_items)} insights "
            f"(sim: {', '.join(sim_strs)}), "
            f"{len(failure_items)} failures[/]"
        )

        return {
            "knowledge": knowledge_str,
            "failures": failure_str,
            "suggestions": suggestion_str,
            "n_knowledge": len(knowledge_items),
            "n_failures": len(failure_items),
        }

    def _enrich_with_graph(self, items: list[dict]) -> list[dict]:
        """Walk the graph from each item to add connected context."""
        if not self.amure:
            return items

        enriched = []
        for item in items:
            node_id = item.get("id", "")
            if not node_id:
                enriched.append(item)
                continue

            try:
                # Walk 1 hop from this node
                walk_data = self.amure.walk(node_id, hops=1)
                connected = walk_data.get("nodes", [])

                # Build context from connected nodes
                context_parts = []
                for n in connected:
                    if n.get("depth", 0) == 0:
                        continue  # skip self
                    kind = n.get("kind", "")
                    stmt = n.get("statement", "")[:60]
                    if kind == "Experiment":
                        context_parts.append(f"[Experiment] {stmt}")
                    elif kind == "Reason":
                        context_parts.append(f"[Reason] {stmt}")
                    elif kind == "Claim":
                        context_parts.append(f"[Related] {stmt}")

                item["graph_context"] = "; ".join(context_parts[:3]) if context_parts else ""
            except Exception:
                item["graph_context"] = ""

            enriched.append(item)
        return enriched

    def _extract_keywords(self, individual: Individual) -> list[str]:
        """Extract search keywords from an individual's thought and code."""
        keywords: list[str] = []

        # From thought
        if individual.thought:
            relevant_terms = [
                "spt", "lpt", "fifo", "lifo", "edd", "slack", "critical",
                "bottleneck", "makespan", "flowtime", "utilization", "load",
                "balance", "priority", "dispatch", "remaining", "duration",
                "machine", "job", "operation", "greedy", "ratio", "weighted",
            ]
            thought_lower = individual.thought.lower()
            for term in relevant_terms:
                if term in thought_lower:
                    keywords.append(term)

        # Always include base context
        if not keywords:
            keywords = ["jssp", "dispatching", "heuristic"]

        return keywords[:10]
