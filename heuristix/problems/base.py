"""Abstract base class for optimization problems."""
from __future__ import annotations

from abc import ABC, abstractmethod


class Problem(ABC):
    """Interface that every problem type must implement."""

    @abstractmethod
    def get_skeleton(self) -> str:
        """Return Python source code for the evaluation skeleton.

        The skeleton must define a `run_evaluation(heuristic_fn, instance_name)` function
        that returns a dict of metrics.
        """
        ...

    @abstractmethod
    def get_heuristic_template(self) -> str:
        """Return the function signature and docstring the LLM should produce."""
        ...

    @abstractmethod
    def evaluate(self, heuristic_code: str, instance_name: str) -> dict:
        """Evaluate a heuristic on a specific instance. Returns metric dict."""
        ...

    @abstractmethod
    def get_instances(self, subset: str = "quick") -> list[str]:
        """Return instance names for a given subset (quick, full, etc.)."""
        ...

    @abstractmethod
    def describe(self) -> str:
        """Return a natural-language description of the problem for LLM prompts."""
        ...
