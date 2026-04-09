"""Extract insights from evolution and store in amure-do knowledge graph."""
from __future__ import annotations

import re
from typing import TYPE_CHECKING

from heuristix.llm.prompts import DISTILLATION_PROMPT

if TYPE_CHECKING:
    from heuristix.amure_client import AmureClient
    from heuristix.config import HeuristiXConfig
    from heuristix.evolution.population import Individual
    from heuristix.llm.provider import LLMProvider


class KnowledgeDistiller:
    """Extract insights from evolution generations and store in amure-do."""

    def __init__(
        self,
        amure_client: AmureClient,
        llm: LLMProvider,
        config: HeuristiXConfig | None = None,
    ):
        self.amure = amure_client
        self.llm = llm
        self.config = config

        # Use role-specific provider if config is available
        if config is not None:
            from heuristix.llm.provider import create_provider_for_role
            try:
                self.llm = create_provider_for_role(config, "distillation")
            except (ValueError, Exception):
                pass  # fall back to the passed llm

    def _edge_kind(self, mapping_key: str) -> str:
        """Resolve an edge kind from config edge_mapping, falling back to hardcoded defaults."""
        if self.config is not None:
            em = self.config.knowledge.edge_mapping
            return getattr(em, mapping_key, mapping_key)
        defaults = {
            "evolution_lineage": "DerivedFrom",
            "insight_supports": "Support",
            "insight_rebuts": "Rebut",
            "strategy_refines": "Refines",
            "strategy_depends": "DependsOn",
            "strategy_contradicts": "Contradicts",
        }
        return defaults.get(mapping_key, mapping_key)

    def distill_generation(
        self,
        top_k: list[Individual],
        bottom_k: list[Individual],
        generation: int,
    ) -> None:
        """Compare top vs bottom individuals, extract insights, store in graph."""
        if not top_k:
            return

        # Compute summary stats
        top_scores = [i.primary_score for i in top_k if i.is_valid]
        bottom_scores = [i.primary_score for i in bottom_k if i.is_valid]
        best_makespan = min(top_scores) if top_scores else float("inf")
        avg_makespan = (
            sum(top_scores + bottom_scores) / len(top_scores + bottom_scores)
            if (top_scores or bottom_scores)
            else float("inf")
        )

        # Format heuristics for the prompt
        top_str = self._format_individuals(top_k)
        bottom_str = self._format_individuals(bottom_k)

        prompt = DISTILLATION_PROMPT.format(
            generation=generation,
            best_makespan=f"{best_makespan:.1f}",
            avg_makespan=f"{avg_makespan:.1f}",
            diversity="N/A",
            top_k=len(top_k),
            bottom_k=len(bottom_k),
            top_heuristics=top_str,
            bottom_heuristics=bottom_str,
        )

        system = (
            "You are analyzing heuristic evolution results. "
            "Extract concise, actionable knowledge claims."
        )

        response = self.llm.generate(prompt, system=system)
        claims, reasons, failures = self._parse_distillation(response)

        supports_kind = self._edge_kind("insight_supports")
        rebuts_kind = self._edge_kind("insight_rebuts")

        # Store claims in amure-do
        for claim_text in claims:
            keywords = self._extract_keywords(claim_text)
            node = self.amure.add_node(
                kind="Claim",
                statement=claim_text,
                keywords=keywords,
                metadata={"generation": generation, "source": "distillation"},
                status="Draft",
            )
            node_id = node.get("id", "")

            # Link reasons as supporting evidence
            for reason_text in reasons:
                reason_node = self.amure.add_node(
                    kind="Reason",
                    statement=reason_text,
                    keywords=keywords,
                    metadata={"generation": generation},
                    status="Draft",
                )
                reason_id = reason_node.get("id", "")
                if node_id and reason_id:
                    self.amure.add_edge(
                        source=reason_id,
                        target=node_id,
                        kind=supports_kind,
                        note=f"Gen {generation} distillation",
                    )

        # Store failure insights as rebuttals
        for failure_text in failures:
            keywords = self._extract_keywords(failure_text)
            failure_node = self.amure.add_node(
                kind="Claim",
                statement=failure_text,
                keywords=["failure", "avoid"] + keywords,
                metadata={"generation": generation, "source": "distillation", "failed": True},
                status="Draft",
            )
            # Link failure as a rebuttal to claims if any
            failure_id = failure_node.get("id", "")
            if failure_id:
                for claim_text in claims:
                    # Re-query or re-use node_id isn't ideal; use edge to first claim if available
                    pass  # rebut edges are added via store_failure_rebuttal if needed

    def store_evolution_lineage(self, parent_id: str, child_id: str, generation: int) -> None:
        """Store parent→child evolution edge in amure-do."""
        self.amure.add_edge(
            source=parent_id,
            target=child_id,
            kind=self._edge_kind("evolution_lineage"),
            note=f"Evolution gen {generation}",
        )

    def store_heuristic(self, individual: Individual, generation: int) -> str:
        """Store a heuristic individual as a graph node."""
        node = self.amure.add_node(
            kind="Experiment",  # Heuristic is an "experiment" in amure-db terms
            statement=individual.thought,
            keywords=self._extract_keywords(individual.thought),
            metadata={
                "generation": generation,
                "code": individual.code,
                "scores": individual.scores,
                "parent_ids": individual.parent_ids,
            },
            status="Active" if individual.is_valid else "Draft",
        )
        return node.get("id", "")

    def update_maturity(self, node_id: str, validation_count: int) -> None:
        """Promote node status based on validation count: Draft -> Active -> Accepted."""
        if validation_count >= 3:
            status = "Accepted"
        elif validation_count >= 1:
            status = "Active"
        else:
            status = "Draft"
        self.amure.update_node(node_id, status=status)

    def _format_individuals(self, individuals: list[Individual]) -> str:
        """Format a list of individuals for prompt inclusion."""
        parts: list[str] = []
        for ind in individuals:
            scores = ", ".join(f"{k}={v:.1f}" for k, v in sorted(ind.scores.items()))
            parts.append(
                f"### {ind.id} (scores: {scores})\n"
                f"Thought: {ind.thought}\n"
                f"```python\n{ind.code}\n```"
            )
        return "\n\n".join(parts) if parts else "None available"

    def _parse_distillation(
        self, response: str
    ) -> tuple[list[str], list[str], list[str]]:
        """Parse LLM distillation response into claims, reasons, failures."""
        claims = self._extract_section(response, "CLAIMS")
        reasons = self._extract_section(response, "REASONS")
        failures = self._extract_section(response, "FAILURES")
        return claims, reasons, failures

    def _extract_section(self, text: str, header: str) -> list[str]:
        """Extract bullet points from a section."""
        pattern = rf"{header}:\s*\n((?:\s*-\s*.+\n?)+)"
        match = re.search(pattern, text, re.IGNORECASE)
        if not match:
            return []
        lines = match.group(1).strip().split("\n")
        return [re.sub(r"^\s*-\s*", "", line).strip() for line in lines if line.strip()]

    def _extract_keywords(self, text: str) -> list[str]:
        """Extract simple keywords from a text statement."""
        # Simple keyword extraction: take significant words
        stop_words = {"the", "a", "an", "is", "are", "was", "were", "be", "been",
                       "being", "have", "has", "had", "do", "does", "did", "will",
                       "would", "could", "should", "may", "might", "can", "to",
                       "of", "in", "for", "on", "with", "at", "by", "from", "and",
                       "or", "but", "not", "that", "this", "it", "as"}
        words = re.findall(r"[a-z]+", text.lower())
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        return list(dict.fromkeys(keywords))[:8]  # Unique, max 8
