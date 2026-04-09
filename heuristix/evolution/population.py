"""Population management — Individual = thought + code + scores."""
from __future__ import annotations

import random
import uuid
from dataclasses import dataclass, field


@dataclass
class Individual:
    """A single heuristic candidate: thought (explanation) + code + evaluation scores."""

    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    thought: str = ""
    code: str = ""
    scores: dict[str, float] = field(default_factory=dict)
    generation: int = 0
    parent_ids: list[str] = field(default_factory=list)
    node_id: str = ""  # amure-do knowledge graph node ID

    @property
    def primary_score(self) -> float:
        """Primary fitness metric (makespan — lower is better)."""
        return self.scores.get("makespan", float("inf"))

    @property
    def is_valid(self) -> bool:
        """True if the individual has been successfully evaluated."""
        return "makespan" in self.scores and self.scores["makespan"] < float("inf")

    def weighted_score(self, weights: dict[str, float]) -> float:
        """Compute a weighted aggregate score (lower is better)."""
        total = 0.0
        for metric, weight in weights.items():
            value = self.scores.get(metric, float("inf"))
            total += weight * value
        return total

    def dominates(self, other: Individual, weights: dict[str, float]) -> bool:
        """Multi-metric dominance check: True if self is better on all weighted metrics."""
        dominated_any = False
        for metric, weight in weights.items():
            self_val = self.scores.get(metric, float("inf")) * weight
            other_val = other.scores.get(metric, float("inf")) * weight
            if self_val > other_val:
                return False
            if self_val < other_val:
                dominated_any = True
        return dominated_any

    def summary(self) -> str:
        """One-line summary for logging."""
        score_str = ", ".join(f"{k}={v:.1f}" for k, v in sorted(self.scores.items()))
        return f"[{self.id}] gen={self.generation} {score_str}"


class Population:
    """Manages a collection of individuals with selection and replacement."""

    def __init__(self, max_size: int = 10, elitism: int = 2):
        self.max_size = max_size
        self.elitism = elitism
        self.individuals: list[Individual] = []
        self._generation: int = 0

    @property
    def generation(self) -> int:
        return self._generation

    @property
    def size(self) -> int:
        return len(self.individuals)

    @property
    def best(self) -> Individual | None:
        """Return the individual with the lowest primary score."""
        valid = [i for i in self.individuals if i.is_valid]
        if not valid:
            return None
        return min(valid, key=lambda i: i.primary_score)

    def add(self, individual: Individual) -> None:
        """Add an individual to the population."""
        self.individuals.append(individual)

    def tournament_select(self, k: int = 3) -> Individual:
        """Tournament selection: pick k random individuals, return the fittest."""
        candidates = random.sample(
            self.individuals, min(k, len(self.individuals))
        )
        valid = [c for c in candidates if c.is_valid]
        if not valid:
            return random.choice(candidates)
        return min(valid, key=lambda i: i.primary_score)

    def get_top(self, n: int) -> list[Individual]:
        """Return the top N individuals by primary score (lower is better)."""
        valid = sorted(
            [i for i in self.individuals if i.is_valid],
            key=lambda i: i.primary_score,
        )
        return valid[:n]

    def get_bottom(self, n: int) -> list[Individual]:
        """Return the bottom N individuals by primary score (higher is worse)."""
        valid = sorted(
            [i for i in self.individuals if i.is_valid],
            key=lambda i: i.primary_score,
            reverse=True,
        )
        return valid[:n]

    def get_diversity(self) -> float:
        """Rough diversity measure: ratio of unique primary scores."""
        if not self.individuals:
            return 0.0
        scores = {i.primary_score for i in self.individuals if i.is_valid}
        total_valid = sum(1 for i in self.individuals if i.is_valid)
        if total_valid == 0:
            return 0.0
        return len(scores) / total_valid

    def next_generation(self, offspring: list[Individual]) -> None:
        """Replace population with elites + offspring, capped at max_size."""
        self._generation += 1

        # Carry forward the elite individuals
        elites = self.get_top(self.elitism)

        # Tag offspring with current generation
        for ind in offspring:
            ind.generation = self._generation

        # Combine elites + offspring, keep the best up to max_size
        combined = elites + offspring
        valid = sorted(
            [i for i in combined if i.is_valid],
            key=lambda i: i.primary_score,
        )
        invalid = [i for i in combined if not i.is_valid]

        # Keep best valid individuals, fill remainder with invalid if needed
        self.individuals = valid[: self.max_size]
        remaining_slots = self.max_size - len(self.individuals)
        if remaining_slots > 0 and invalid:
            self.individuals.extend(invalid[:remaining_slots])

    def stats(self) -> dict[str, float]:
        """Return population statistics."""
        valid = [i for i in self.individuals if i.is_valid]
        if not valid:
            return {"best": float("inf"), "worst": float("inf"), "avg": float("inf"), "diversity": 0.0}
        scores = [i.primary_score for i in valid]
        return {
            "best": min(scores),
            "worst": max(scores),
            "avg": sum(scores) / len(scores),
            "diversity": self.get_diversity(),
        }
