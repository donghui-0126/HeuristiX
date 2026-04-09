"""Select relevant knowledge from amure-do for evolution context injection."""
from __future__ import annotations

from typing import TYPE_CHECKING

from rich.console import Console

if TYPE_CHECKING:
    from heuristix.amure_client import AmureClient
    from heuristix.evolution.population import Individual

_console = Console()


class KnowledgeSelector:
    """Query amure-do to build knowledge context for mutation/crossover."""

    def __init__(self, amure_client: AmureClient):
        self.amure = amure_client

    def get_context(
        self, individual: Individual, include_failures: bool = True
    ) -> dict[str, str]:
        """Build a knowledge context dict for an individual.

        Returns:
            {"knowledge": str, "failures": str, "suggestions": str}
        """
        keywords = self._extract_keywords(individual)
        query = " ".join(keywords) if keywords else "job shop scheduling heuristic"

        # RAG search for relevant knowledge
        knowledge_parts: list[str] = []
        n_mature = 0
        n_active = 0
        try:
            results = self.amure.search(query, top_k=5, include_failed=False)
            # Sort results: Accepted first, then Active, then Draft
            results.sort(
                key=lambda r: {"Accepted": 0, "Active": 1, "Draft": 2}.get(
                    r.get("status", "Draft"), 3
                )
            )
            for r in results:
                status = r.get("status", "Draft")
                statement = r.get("statement", "")
                priority = {"Accepted": 3, "Active": 2, "Draft": 1}.get(status, 0)
                knowledge_parts.append((priority, f"[{status}] {statement}"))
                if status == "Accepted":
                    n_mature += 1
                elif status == "Active":
                    n_active += 1
            # Sort by priority descending
            knowledge_parts.sort(key=lambda x: x[0], reverse=True)
        except Exception:
            pass

        knowledge_str = "\n".join(
            f"- {text}" for _, text in knowledge_parts
        ) if knowledge_parts else ""

        # Check for failure warnings
        failure_str = ""
        failure_items: list[dict] = []
        if include_failures:
            try:
                statement = individual.thought or individual.code[:200]
                warnings = self.amure.check_failures(statement, keywords)
                if warnings:
                    failure_items = warnings
                    failure_str = "\n".join(
                        f"- {w.get('statement', w.get('warning', str(w)))}"
                        for w in warnings
                    )
            except Exception:
                pass

        # Suggestions for novel combinations
        suggestion_str = ""
        try:
            suggestions = self.amure.suggest_combinations()
            combos = suggestions.get("combinations", [])
            if combos:
                suggestion_str = "\n".join(
                    f"- {c.get('description', str(c))}" for c in combos[:3]
                )
        except Exception:
            pass

        # Log what knowledge is being injected
        if knowledge_parts:
            _console.print(
                f"  [dim][Knowledge] Injected {len(knowledge_parts)} items "
                f"({n_mature} mature, {n_active} active)[/]"
            )
            for _, text in knowledge_parts[:2]:
                _console.print(f"    [dim]-> {text[:70]}...[/]")
        if failure_items:
            _console.print(f"  [dim][Failures] {len(failure_items)} warnings[/]")

        return {
            "knowledge": knowledge_str,
            "failures": failure_str,
            "suggestions": suggestion_str,
        }

    def _extract_keywords(self, individual: Individual) -> list[str]:
        """Extract search keywords from an individual's thought and code."""
        keywords: list[str] = []

        # From thought
        if individual.thought:
            # Look for scheduling-relevant terms
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
