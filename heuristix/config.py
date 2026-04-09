"""Configuration loader — YAML config with dataclass defaults."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class AmureDoConfig:
    url: str = "http://localhost:9090"
    timeout: float = 30


@dataclass
class LLMConfig:
    provider: str = "claude_cli"
    model: str = ""
    api_key: str = ""
    temperature: float = 0.7


@dataclass
class MetricsConfig:
    primary: str = "makespan"
    secondary: list[str] = field(default_factory=lambda: ["flowtime", "utilization"])
    weights: dict[str, float] = field(
        default_factory=lambda: {"makespan": 1.0, "flowtime": 0.3, "utilization": 0.2}
    )


@dataclass
class EvaluationConfig:
    cascade: bool = True
    quick_instances: list[str] = field(default_factory=lambda: ["ft06"])
    full_instances: list[str] = field(default_factory=lambda: ["ft06", "ft10", "ft20"])
    timeout_per_instance: int = 30
    metrics: MetricsConfig = field(default_factory=MetricsConfig)


@dataclass
class EvolutionConfig:
    population_size: int = 10
    generations: int = 30
    tournament_size: int = 3
    mutation_rate: float = 0.7
    crossover_rate: float = 0.3
    elitism: int = 2


@dataclass
class KnowledgeConfig:
    distill_every: int = 1
    top_k_compare: int = 3
    bottom_k_compare: int = 3
    maturity_threshold: int = 3


@dataclass
class ProblemConfig:
    name: str = "jssp"


@dataclass
class HeuristiXConfig:
    amure_do: AmureDoConfig = field(default_factory=AmureDoConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    evolution: EvolutionConfig = field(default_factory=EvolutionConfig)
    evaluation: EvaluationConfig = field(default_factory=EvaluationConfig)
    knowledge: KnowledgeConfig = field(default_factory=KnowledgeConfig)
    problem: ProblemConfig = field(default_factory=ProblemConfig)


def _merge_dict(target: dict, source: dict) -> dict:
    """Recursively merge source into target."""
    for key, value in source.items():
        if key in target and isinstance(target[key], dict) and isinstance(value, dict):
            _merge_dict(target[key], value)
        else:
            target[key] = value
    return target


def _dict_to_dataclass(cls: type, data: dict[str, Any]) -> Any:
    """Recursively convert a dict to nested dataclasses."""
    if not isinstance(data, dict):
        return data
    field_types = {f.name: f.type for f in cls.__dataclass_fields__.values()}  # type: ignore[attr-defined]
    kwargs: dict[str, Any] = {}
    for key, value in data.items():
        if key not in field_types:
            continue
        ft = field_types[key]
        # Resolve string type annotations
        if isinstance(ft, str):
            ft = eval(ft, vars(__import__("builtins")))  # noqa: S307
        if isinstance(value, dict) and hasattr(ft, "__dataclass_fields__"):
            kwargs[key] = _dict_to_dataclass(ft, value)
        else:
            kwargs[key] = value
    return cls(**kwargs)


def load_config(path: str | Path | None = None) -> HeuristiXConfig:
    """Load config from YAML file, merging with defaults."""
    if path is None:
        path = os.environ.get("HEURISTIX_CONFIG", "configs/default.yaml")
    path = Path(path)

    if path.exists():
        with open(path) as f:
            raw = yaml.safe_load(f) or {}
    else:
        raw = {}

    # Build defaults as dict, merge, then convert
    defaults = HeuristiXConfig()
    return _dict_to_dataclass(HeuristiXConfig, raw) if raw else defaults
