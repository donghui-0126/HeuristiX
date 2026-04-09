"""LLM-based genetic operators: mutation, crossover, population initialization."""
from __future__ import annotations

import re
import uuid

from heuristix.evolution.population import Individual
from heuristix.llm.prompts import (
    CROSSOVER_PROMPT,
    INIT_POPULATION_PROMPT,
    INIT_STRATEGIES,
    MUTATION_PROMPT,
)
from heuristix.llm.provider import LLMProvider


def _parse_thought_and_code(response: str) -> tuple[str, str]:
    """Extract THOUGHT and CODE blocks from LLM response."""
    thought = ""
    code = ""

    # Extract thought
    thought_match = re.search(r"THOUGHT:\s*(.*?)(?=CODE:|```python|$)", response, re.DOTALL)
    if thought_match:
        thought = thought_match.group(1).strip()

    # Extract code from fenced block
    code_match = re.search(r"```python\s*\n(.*?)```", response, re.DOTALL)
    if code_match:
        code = code_match.group(1).strip()
    else:
        # Fallback: look for def heuristic(
        func_match = re.search(r"(def heuristic\(.*)", response, re.DOTALL)
        if func_match:
            code = func_match.group(1).strip()

    return thought, code


def _format_scores(scores: dict[str, float]) -> str:
    """Format score dict as readable string."""
    if not scores:
        return "Not yet evaluated"
    return ", ".join(
        f"{k}: {v:.2f}" for k, v in sorted(scores.items())
        if isinstance(v, (int, float))
    )


def mutate(
    individual: Individual,
    llm: LLMProvider,
    knowledge_context: str = "",
    failure_warnings: str = "",
) -> Individual:
    """Mutate an individual using LLM-guided improvement."""
    prompt = MUTATION_PROMPT.format(
        thought=individual.thought or "No thought recorded",
        code=individual.code,
        scores=_format_scores(individual.scores),
        knowledge_context=knowledge_context or "No prior knowledge available.",
        failure_warnings=failure_warnings or "No known failure warnings.",
    )

    system = (
        "You are an expert in combinatorial optimization and Job-Shop Scheduling. "
        "Write clean, efficient Python code. The heuristic must be a pure function."
    )

    response = llm.generate(prompt, system=system)
    thought, code = _parse_thought_and_code(response)

    if not code:
        # If parsing failed, return a copy of the original
        return Individual(
            id=uuid.uuid4().hex[:12],
            thought=f"Mutation failed to parse: {response[:200]}",
            code=individual.code,
            parent_ids=[individual.id],
        )

    return Individual(
        id=uuid.uuid4().hex[:12],
        thought=thought,
        code=code,
        parent_ids=[individual.id],
    )


def crossover(
    parent_a: Individual,
    parent_b: Individual,
    llm: LLMProvider,
    knowledge_context: str = "",
) -> Individual:
    """Combine two parents using LLM-guided crossover."""
    prompt = CROSSOVER_PROMPT.format(
        thought_a=parent_a.thought or "No thought recorded",
        code_a=parent_a.code,
        scores_a=_format_scores(parent_a.scores),
        thought_b=parent_b.thought or "No thought recorded",
        code_b=parent_b.code,
        scores_b=_format_scores(parent_b.scores),
        knowledge_context=knowledge_context or "No prior knowledge available.",
    )

    system = (
        "You are an expert in combinatorial optimization and Job-Shop Scheduling. "
        "Combine the strengths of both parent heuristics into one improved function."
    )

    response = llm.generate(prompt, system=system)
    thought, code = _parse_thought_and_code(response)

    if not code:
        # Fallback: return a copy of the better parent
        better = parent_a if parent_a.primary_score <= parent_b.primary_score else parent_b
        return Individual(
            id=uuid.uuid4().hex[:12],
            thought=f"Crossover failed to parse: {response[:200]}",
            code=better.code,
            parent_ids=[parent_a.id, parent_b.id],
        )

    return Individual(
        id=uuid.uuid4().hex[:12],
        thought=thought,
        code=code,
        parent_ids=[parent_a.id, parent_b.id],
    )


def init_population(
    n: int,
    llm: LLMProvider,
    problem_description: str,
) -> list[Individual]:
    """Generate an initial diverse population using LLM with different strategy hints."""
    individuals: list[Individual] = []

    for i in range(n):
        strategy = INIT_STRATEGIES[i % len(INIT_STRATEGIES)]
        prompt = INIT_POPULATION_PROMPT.format(
            problem_description=problem_description,
            strategy_hint=strategy,
        )

        system = (
            "You are an expert in combinatorial optimization. "
            "Create a dispatching rule heuristic for Job-Shop Scheduling."
        )

        try:
            response = llm.generate(prompt, system=system)
            thought, code = _parse_thought_and_code(response)
        except Exception as e:
            thought = f"Init failed: {e}"
            code = ""

        if not code:
            # Provide a simple fallback heuristic
            code = _fallback_heuristic(i)
            thought = thought or f"Fallback heuristic (strategy: {strategy})"

        individuals.append(
            Individual(
                id=uuid.uuid4().hex[:12],
                thought=thought,
                code=code,
                generation=0,
            )
        )

    return individuals


def _fallback_heuristic(index: int) -> str:
    """Simple deterministic fallback heuristics for when LLM generation fails."""
    fallbacks = [
        # SPT
        'def heuristic(available_ops, machine_loads, current_time):\n    """Shortest Processing Time."""\n    return min(range(len(available_ops)), key=lambda i: available_ops[i]["duration"])',
        # LPT
        'def heuristic(available_ops, machine_loads, current_time):\n    """Longest Processing Time."""\n    return max(range(len(available_ops)), key=lambda i: available_ops[i]["duration"])',
        # MRO
        'def heuristic(available_ops, machine_loads, current_time):\n    """Most Remaining Operations."""\n    return max(range(len(available_ops)), key=lambda i: available_ops[i]["remaining_ops"])',
        # LRO
        'def heuristic(available_ops, machine_loads, current_time):\n    """Least Remaining Operations."""\n    return min(range(len(available_ops)), key=lambda i: available_ops[i]["remaining_ops"])',
        # FIFO
        'def heuristic(available_ops, machine_loads, current_time):\n    """First In First Out (by job index)."""\n    return min(range(len(available_ops)), key=lambda i: available_ops[i]["job"])',
    ]
    return fallbacks[index % len(fallbacks)]
