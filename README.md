# HeuristiX

Knowledge-Evolutionary Framework for Automatic Heuristic Discovery.

HeuristiX evolves dispatching heuristics for the Job-Shop Scheduling Problem (JSSP) using LLMs and persistent knowledge accumulation in a graph database. Unlike existing approaches (FunSearch, EoH, AlphaEvolve) that discard failed solutions, HeuristiX retrieves and learns from past insights during evolution to avoid repeated failures and accelerate discovery.

## Key Idea

Existing LLM-based heuristic evolution loses knowledge: failed individuals are discarded, successful strategies aren't analyzed, and the same mistakes repeat across generations.

HeuristiX fixes this through:

1. **Knowledge accumulation** — Every generation's insights (why top heuristics work, why bottom ones fail) stored in amure-do's graph database
2. **Knowledge retrieval** — Graph RAG search retrieves relevant past insights during mutation/crossover, preventing repeated failures
3. **Knowledge maturity** — Draft → Active → Accepted (Mature) lifecycle for knowledge reliability
4. **Multi-metric evaluation** — Not just makespan, but flowtime, utilization, tardiness with configurable weights

## Architecture

```
HeuristiX (Python)              amure-do (Rust :9090)
┌─────────────────────┐         ┌─────────────────────────┐
│ Evolution Engine     │←─HTTP──→│ Knowledge DB (amure-db) │
│  - Population mgmt  │         │  - Graph RAG search     │
│  - LLM mutation     │         │  - Failure avoidance    │
│  - LLM crossover    │         │  - Contradiction detect │
│  - JSSP evaluation   │         │  - Gap discovery        │
│  - Distillation      │         │  - Dashboard (viz)      │
└─────────────────────┘         └─────────────────────────┘
```

## Quick Start

### 1. Start amure-do (knowledge backend)

```bash
cd /path/to/amure-do
./target/release/amure-do  # → http://localhost:9090
```

### 2. Install HeuristiX

```bash
cd /path/to/HeuristiX
pip install -e .
```

### 3. Run evolution

```bash
heuristix --config configs/default.yaml --generations 20
```

### 4. View knowledge graph

```
open http://localhost:9090/graph
```

## Evolution Loop

```
1. Initialize population (LLM generates N random heuristics)
2. Evaluate on JSSP instances (multi-metric)
3. For each generation:
   a. Tournament selection
   b. Query amure-do for knowledge context + failure warnings
   c. LLM mutation (with knowledge injection)
   d. LLM crossover (with knowledge injection)
   e. Evaluation cascade (quick → full)
   f. Update population (elitism)
   g. Distill knowledge (compare top vs bottom → store insights)
   h. Check stagnation → request new directions from amure-do
4. Return best heuristic
```

## Configuration

Edit `configs/default.yaml`:

```yaml
# amure-do backend
amure_do:
  url: "http://localhost:9090"
  timeout: 30

# LLM provider
llm:
  provider: "claude_cli"  # or openai, ollama
  model: ""
  api_key: ""
  temperature: 0.7

# Evolution parameters
evolution:
  population_size: 10      # N heuristics per generation
  generations: 30          # Total generations
  tournament_size: 3       # Selection tournament size
  mutation_rate: 0.7       # Probability of mutation
  crossover_rate: 0.3      # Probability of crossover
  elitism: 2               # Top N carried to next generation

# Evaluation strategy
evaluation:
  cascade: true            # Quick → Full evaluation
  quick_instances: ["ft06"]
  full_instances: ["ft06", "ft10", "ft20"]
  timeout_per_instance: 30

  metrics:
    primary: "makespan"
    secondary: ["flowtime", "utilization"]
    weights:
      makespan: 1.0
      flowtime: 0.3
      utilization: 0.2

# Knowledge management
knowledge:
  distill_every: 1         # Distill every N generations
  top_k_compare: 3         # Compare top K with bottom K
  bottom_k_compare: 3
  maturity_threshold: 3    # N validations for Mature status

# Target problem
problem:
  name: "jssp"
```

## Project Structure

```
HeuristiX/
  heuristix/
    __init__.py              # Package metadata
    config.py                # YAML config loader + dataclasses
    
    amure_client.py          # amure-do HTTP client (TODO)
    cli.py                   # CLI entry point (TODO)
    
    llm/
      provider.py            # LLM abstraction (Claude/OpenAI/Ollama) (TODO)
      prompts.py             # Prompt templates (TODO)
    
    evolution/
      population.py          # Individual + Population management (TODO)
      operators.py           # LLM mutation, crossover, init (TODO)
      manager.py             # Main evolution loop (TODO)
    
    knowledge/
      distillation.py        # Insight extraction → amure-do storage (TODO)
      selection.py           # Knowledge retrieval from amure-do (TODO)
    
    evaluation/
      runner.py              # Code execution (TODO)
      cascade.py             # Quick → Full evaluation (TODO)
      metrics.py             # Multi-metric computation (TODO)
    
    problems/
      base.py                # Problem abstract class (TODO)
      jssp/
        problem.py           # JSSP problem implementation (TODO)
        simulator.py         # JSSP simulator (schedule builder) (TODO)
        benchmarks.py        # Taillard instances (ft06, ft10 embedded) (TODO)
  
  configs/
    default.yaml             # Default configuration
  
  paper-md/                  # Reference papers (markdown)
    FunSearch.md
    Evolution_of_Heuristics.md
    AlphaEvolve.md
    SeEvo_DFJSSP.md
    ReasoningBank.md
    ReasoningBank_상세설명.md
  
  tests/                     # Test suite (TODO)
  
  pyproject.toml             # Package metadata + dependencies
```

## Problem: Job-Shop Scheduling

Given:
- `m` machines
- `n` jobs
- Each job consists of `m` operations (one per machine)
- Operation `(j,i)` must be processed on machine `i` for duration `p[j][i]`
- Operation `(j,i)` must follow `(j,i-1)` in the same job
- Each machine can process one operation at a time

Objective: Schedule all operations to **minimize makespan** (total completion time), plus secondary metrics (flowtime, utilization, tardiness).

**Dispatching rule** (the heuristic to evolve):
```python
def heuristic(available_ops: list, machine_loads: dict, current_time: int) -> int:
    """
    Select next operation to schedule from available_ops.
    
    Args:
        available_ops: List of (job_id, op_index) tuples ready to schedule
        machine_loads: Dict {machine_id: next_free_time}
        current_time: Current simulation time
    
    Returns:
        Index of selected operation in available_ops
    """
```

## Comparison with Existing Work

| Feature | FunSearch | EoH | AlphaEvolve | ReasoningBank | HeuristiX |
|---------|-----------|-----|-------------|---------------|-----------|
| Knowledge persistence | ✗ | ✗ | ✗ | ✓ (flat) | ✓ (graph) |
| Failure memory | ✗ | ✗ | ✗ | ✓ | ✓ + graph walk |
| Knowledge maturity | ✗ | ✗ | ✗ | ✗ | ✓ |
| Multi-metric evaluation | ✗ | ✗ | ✓ | ✗ | ✓ |
| Graph RAG retrieval | ✗ | ✗ | ✗ | cosine only | token+BFS+MMR |
| Thought + Code evolution | ✗ | ✓ | ✗ | ✗ | ✓ (planned) |

## Dependencies

- Python 3.10+
- `httpx` — HTTP client for amure-do
- `pyyaml` — YAML config parsing
- `numpy` — Metrics computation
- `rich` — Console formatting

Optional:
- `pytest` — Testing
- `matplotlib` — Visualization

## References

- **FunSearch** (Nature 2024) — LLM + evaluator for mathematical discovery
- **EoH: Evolution of Heuristics** (ICML 2024) — Thought + Code simultaneous evolution
- **AlphaEvolve** (DeepMind 2025) — Diff-based code evolution, evaluation cascade
- **SeEvo** (IEEE TFS 2026) — 3-stage reflection for Dynamic FJSSP
- **ReasoningBank** (arXiv 2026) — Success/failure experience memory for agents

See `paper-md/` for detailed summaries.

## License

MIT
