"""Evaluation cascade — quick test then full evaluation."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from heuristix.problems.base import Problem


class EvaluationCascade:
    """Two-stage evaluation: quick instances first, full if promising."""

    def __init__(
        self,
        problem: Problem,
        timeout: int = 30,
        quick_threshold: float = float("inf"),
    ):
        from heuristix.evaluation.runner import EvaluationRunner

        self.runner = EvaluationRunner(problem, timeout=timeout)
        self.quick_threshold = quick_threshold

    def evaluate(
        self,
        code: str,
        quick_instances: list[str],
        full_instances: list[str],
        threshold: float | None = None,
    ) -> dict[str, float]:
        """Run cascade evaluation.

        1. Evaluate on quick_instances.
        2. If makespan <= threshold, evaluate on full_instances.
        3. Return the full scores (or quick scores if rejected early).
        """
        threshold = threshold if threshold is not None else self.quick_threshold

        # Stage 1: quick evaluation
        quick_scores = self.runner.evaluate(code, quick_instances)
        quick_makespan = quick_scores.get("makespan", float("inf"))

        # Early reject if above threshold
        if quick_makespan > threshold and threshold < float("inf"):
            return quick_scores

        # Stage 2: full evaluation (includes quick instances)
        if set(quick_instances) == set(full_instances):
            return quick_scores

        full_scores = self.runner.evaluate(code, full_instances)
        return full_scores
