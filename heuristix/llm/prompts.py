"""Prompt templates for LLM-driven genetic operators and knowledge distillation."""

MUTATION_PROMPT = """You are evolving a heuristic function for Job-Shop Scheduling.

## Current heuristic (thought + code):
Thought: {thought}
```python
{code}
```

## Evaluation results:
{scores}

## Knowledge context (from previous experiments):
{knowledge_context}

## Warnings (failed approaches to avoid):
{failure_warnings}

## Task:
Improve this heuristic. First explain your reasoning (thought), then write the improved code.
The heuristic function signature must be:
  def heuristic(available_ops, machine_loads, current_time) -> int
It returns the INDEX of the selected operation from available_ops.

Output format:
THOUGHT: <your reasoning>
CODE:
```python
<improved heuristic function>
```
"""

CROSSOVER_PROMPT = """You are combining two heuristic functions for Job-Shop Scheduling.

## Parent A (thought + code):
Thought: {thought_a}
```python
{code_a}
```
Scores: {scores_a}

## Parent B (thought + code):
Thought: {thought_b}
```python
{code_b}
```
Scores: {scores_b}

## Knowledge context (from previous experiments):
{knowledge_context}

## Task:
Create a new heuristic that combines the best ideas from both parents.
The heuristic function signature must be:
  def heuristic(available_ops, machine_loads, current_time) -> int
It returns the INDEX of the selected operation from available_ops.

Output format:
THOUGHT: <your reasoning about what to combine>
CODE:
```python
<combined heuristic function>
```
"""

REFLECTION_PROMPT = """You are analyzing heuristic performance for Job-Shop Scheduling.

## Top performing heuristics:
{top_heuristics}

## Bottom performing heuristics:
{bottom_heuristics}

## Task:
Compare the top and bottom heuristics. What patterns make the top heuristics better?
What mistakes do the bottom heuristics make? Extract general insights.

Output format:
INSIGHTS:
- <insight 1>
- <insight 2>
- ...

PATTERNS_TO_FOLLOW:
- <pattern 1>
- <pattern 2>

PATTERNS_TO_AVOID:
- <anti-pattern 1>
- <anti-pattern 2>
"""

DISTILLATION_PROMPT = """You are extracting knowledge from heuristic evolution for Job-Shop Scheduling.

## Generation {generation} summary:
Best makespan: {best_makespan}
Average makespan: {avg_makespan}
Population diversity: {diversity}

## Top {top_k} heuristics:
{top_heuristics}

## Bottom {bottom_k} heuristics:
{bottom_heuristics}

## Task:
Extract concise knowledge claims from this generation:
1. What design principles made top heuristics succeed? (Claim nodes)
2. What reasoning explains the success? (Reason nodes)
3. What approaches should be avoided? (Rebut evidence)

Output format:
CLAIMS:
- <claim 1>
- <claim 2>

REASONS:
- <reason supporting claim 1>
- <reason supporting claim 2>

FAILURES:
- <failed approach description 1>
- <failed approach description 2>
"""

INIT_POPULATION_PROMPT = """You are creating an initial heuristic function for Job-Shop Scheduling.

## Problem description:
{problem_description}

## Heuristic template:
The function signature must be:
  def heuristic(available_ops, machine_loads, current_time) -> int

Parameters:
- available_ops: list of dicts, each with keys:
    - "job": job index
    - "op_idx": operation index within the job
    - "machine": machine this operation runs on
    - "duration": processing time
    - "remaining_ops": number of remaining operations for this job
    - "remaining_time": total remaining processing time for this job
- machine_loads: list of floats, current total load on each machine
- current_time: current simulation time (float)

Returns: integer index into available_ops (which operation to schedule next)

## Strategy hint:
{strategy_hint}

## Task:
Create a dispatching rule heuristic. First explain your reasoning, then write the code.

Output format:
THOUGHT: <your reasoning>
CODE:
```python
<heuristic function>
```
"""

# Strategy hints for diverse initial population
INIT_STRATEGIES = [
    "Use Shortest Processing Time (SPT) — prefer operations with smallest duration.",
    "Use Longest Processing Time (LPT) — prefer operations with longest duration.",
    "Use Most Remaining Operations (MRO) — prefer jobs with most remaining operations.",
    "Use Least Remaining Operations (LRO) — prefer jobs closest to completion.",
    "Use Shortest Remaining Time (SRT) — prefer jobs with least total remaining time.",
    "Use Longest Remaining Time (LRT) — prefer jobs with most total remaining time.",
    "Use Least Loaded Machine (LLM) — prefer operations on less loaded machines.",
    "Use a combined rule: balance SPT with machine load awareness.",
    "Use a ratio-based rule: (remaining_time / remaining_ops) weighted by machine load.",
    "Use a novel approach: combine job urgency (remaining_ops) with machine balance.",
]
