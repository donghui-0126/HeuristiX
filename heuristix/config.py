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
class LLMRoleConfig:
    provider: str = ""
    model: str = ""
    api_key: str = ""
    temperature: float = 0.7


@dataclass
class LLMConfig:
    default: LLMRoleConfig = field(default_factory=LLMRoleConfig)
    roles: dict[str, LLMRoleConfig] = field(default_factory=dict)

    def get_role(self, role: str) -> LLMRoleConfig:
        """Get config for a role, falling back to default."""
        if role in self.roles:
            rc = self.roles[role]
            # Inherit missing fields from default
            return LLMRoleConfig(
                provider=rc.provider or self.default.provider,
                model=rc.model or self.default.model,
                api_key=rc.api_key or self.default.api_key,
                temperature=rc.temperature if rc.temperature != 0.7 else self.default.temperature,
            )
        return self.default


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
class EdgeMappingConfig:
    evolution_lineage: str = "DerivedFrom"
    insight_supports: str = "Support"
    insight_rebuts: str = "Rebut"
    strategy_refines: str = "Refines"
    strategy_depends: str = "DependsOn"
    strategy_contradicts: str = "Contradicts"


@dataclass
class KnowledgeConfig:
    distill_every: int = 1
    top_k_compare: int = 3
    bottom_k_compare: int = 3
    maturity_threshold: int = 3
    edge_mapping: EdgeMappingConfig = field(default_factory=EdgeMappingConfig)


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
    import sys as _sys
    _module_globals = _sys.modules[__name__].__dict__
    field_types = {f.name: f.type for f in cls.__dataclass_fields__.values()}  # type: ignore[attr-defined]
    kwargs: dict[str, Any] = {}
    for key, value in data.items():
        if key not in field_types:
            continue
        ft = field_types[key]
        # Resolve string type annotations using module globals
        if isinstance(ft, str):
            ft = eval(ft, _module_globals)  # noqa: S307
        if isinstance(value, dict) and hasattr(ft, "__dataclass_fields__"):
            kwargs[key] = _dict_to_dataclass(ft, value)
        else:
            kwargs[key] = value
    return cls(**kwargs)


def _load_llm_config(raw_llm: dict[str, Any]) -> LLMConfig:
    """Load LLMConfig supporting both legacy flat format and new role-based format."""
    # Legacy flat format: {provider, model, api_key, temperature}
    if "provider" in raw_llm and "default" not in raw_llm:
        role = LLMRoleConfig(
            provider=raw_llm.get("provider", ""),
            model=raw_llm.get("model", ""),
            api_key=raw_llm.get("api_key", ""),
            temperature=raw_llm.get("temperature", 0.7),
        )
        return LLMConfig(default=role)

    # New role-based format: {default: {...}, roles: {...}}
    default_data = raw_llm.get("default", {})
    default_role = LLMRoleConfig(
        provider=default_data.get("provider", ""),
        model=default_data.get("model", ""),
        api_key=default_data.get("api_key", ""),
        temperature=default_data.get("temperature", 0.7),
    )

    roles: dict[str, LLMRoleConfig] = {}
    for role_name, role_data in raw_llm.get("roles", {}).items():
        if isinstance(role_data, dict):
            roles[role_name] = LLMRoleConfig(
                provider=role_data.get("provider", ""),
                model=role_data.get("model", ""),
                api_key=role_data.get("api_key", ""),
                temperature=role_data.get("temperature", 0.7),
            )

    return LLMConfig(default=default_role, roles=roles)


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

    if not raw:
        return HeuristiXConfig()

    # Handle llm section separately (supports both legacy and new format)
    llm_config = LLMConfig()
    if "llm" in raw:
        llm_config = _load_llm_config(raw.pop("llm"))

    cfg = _dict_to_dataclass(HeuristiXConfig, raw)
    cfg.llm = llm_config
    return cfg
