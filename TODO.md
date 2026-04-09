# HeuristiX — Implementation Roadmap

## Overview

This roadmap tracks the path from scaffolding (Phase 0, mostly done) through full production (Phase 4). Each phase has clear milestones to validate progress.

---

## Phase 0: Scaffolding ✓ COMPLETE

Project structure, configuration, and external interfaces.

- [x] Project structure (`heuristix/` + `configs/` + `tests/`)
- [x] `pyproject.toml` with dependencies
- [x] Config system (`config.py` with dataclasses + YAML loading)
- [x] Default configuration (`configs/default.yaml`)
- [x] Package metadata (`__init__.py`)
- [x] `.gitignore` for binary files

---

## Phase 1: Basic Evolution Loop

Core simulation + evolution. Goal: Reproduce EoH-style evolution on ft06.

### Evaluation Engine

- [ ] **JSSP Simulator** (`problems/jssp/simulator.py`)
  - [ ] Schedule builder (dispatch operations onto machines)
  - [ ] Makespan computation
  - [ ] Flowtime computation (sum of job completion times)
  - [ ] Machine utilization
  - [ ] Tardiness (if due dates provided)
  - [ ] Heuristic execution + error handling

- [ ] **Benchmark Loader** (`problems/jssp/benchmarks.py`)
  - [ ] Taillard ft06 (6 jobs, 6 machines, 36 operations)
  - [ ] Taillard ft10 (10 jobs, 10 machines, 100 operations)
  - [ ] Taillard ft20 (20 jobs, 5 machines, 100 operations)
  - [ ] Parser for standard format
  - [ ] Validation (operation matrix shape, durations)

- [ ] **Problem Interface** (`problems/base.py`, `problems/jssp/problem.py`)
  - [ ] Abstract `Problem` class (evaluate, get_metadata, etc.)
  - [ ] JSSP problem implementation
  - [ ] Multi-metric evaluation (primary + secondary weights)

- [ ] **Metrics Computation** (`evaluation/metrics.py`)
  - [ ] Weighted composite score: `α×makespan + β×flowtime + γ×utilization`
  - [ ] Metric aggregation across instances
  - [ ] Ranking + comparison

### Evolution Engine

- [ ] **Population Management** (`evolution/population.py`)
  - [ ] `Individual` class (heuristic code, metrics, generation born)
  - [ ] `Population` class (list of individuals, fitness tracking)
  - [ ] Tournament selection (k-way tournament, rank-based)
  - [ ] Elitism (keep top N)
  - [ ] Population statistics (min/max/mean/std fitness)

- [ ] **LLM Provider** (`llm/provider.py`)
  - [ ] Abstract `LLMProvider` interface
  - [ ] Claude CLI provider
  - [ ] OpenAI provider (optional)
  - [ ] Ollama provider (optional)
  - [ ] Error handling + retry logic

- [ ] **LLM Operators** (`evolution/operators.py`)
  - [ ] Initialize population (random heuristics from LLM)
  - [ ] Mutation (LLM edits heuristic, context injection placeholder)
  - [ ] Crossover (LLM blends two heuristics, context injection placeholder)
  - [ ] Syntax validation (heuristic must be valid Python)

- [ ] **Prompts** (`llm/prompts.py`)
  - [ ] Initialization prompt (generate random heuristic)
  - [ ] Mutation prompt (edit heuristic for improvement)
  - [ ] Crossover prompt (blend two heuristics)
  - [ ] Thought prompt (explain current heuristic + weaknesses)

- [ ] **Evolution Manager** (`evolution/manager.py`)
  - [ ] Main loop (init → eval → select → mutate → eval → repeat)
  - [ ] Generation tracking
  - [ ] Stagnation detection (fitness plateau)
  - [ ] Logging + progress reporting

### CLI + Integration

- [ ] **CLI Entry Point** (`cli.py`)
  - [ ] Load config from file or environment
  - [ ] Parse `--config`, `--generations`, `--seed` arguments
  - [ ] Run evolution loop
  - [ ] Save best heuristic to file
  - [ ] Print final metrics

- [ ] **Code Execution** (`evaluation/runner.py`)
  - [ ] Safe execution of heuristic code (subprocess)
  - [ ] Timeout + resource limits
  - [ ] Error capture + graceful fallback
  - [ ] Logging

### Phase 1 Milestone

**Milestone: Reproduce EoH-style evolution on ft06**

- Run: `heuristix --config configs/default.yaml --generations 5`
- Expected: 5 generations, population size 10, printed metrics per generation
- Validation:
  - [ ] All heuristics execute without error
  - [ ] Metrics computed correctly (makespan, flowtime, utilization)
  - [ ] Population improves (or at least doesn't regress on ft06)
  - [ ] Best heuristic saved to file
  - [ ] No amure-do dependency yet (stubs only)

---

## Phase 2: Knowledge Integration (amure-do)

Persistent knowledge accumulation + graph RAG retrieval.

### amure-do Client

- [ ] **HTTP Client** (`amure_client.py`)
  - [ ] POST `/insights` — store new insight
  - [ ] GET `/search?query=...` — graph RAG search
  - [ ] GET `/failures?pattern=...` — fetch known failure patterns
  - [ ] POST `/validate` — check contradiction
  - [ ] GET `/gaps` — find gaps in knowledge
  - [ ] Error handling + exponential backoff

### Knowledge Distillation

- [ ] **Insight Extraction** (`knowledge/distillation.py`)
  - [ ] Compare top K vs bottom K heuristics
  - [ ] Identify patterns (code structure, specific operators)
  - [ ] Extract insights: "Top heuristics use rule X, bottom ones don't"
  - [ ] Assign confidence scores
  - [ ] Format for amure-do storage

- [ ] **Knowledge Lifecycle** (`knowledge/distillation.py`)
  - [ ] `Draft` — newly extracted insight
  - [ ] `Active` — validated in 1+ generation
  - [ ] `Accepted` (Mature) — validated in N generations (config: `maturity_threshold`)
  - [ ] Lifecycle transitions based on validation

### Knowledge Retrieval + Injection

- [ ] **Knowledge Selection** (`knowledge/selection.py`)
  - [ ] Query amure-do for context before mutation
  - [ ] Retrieve top K relevant insights (graph RAG)
  - [ ] Retrieve failure warnings (what to avoid)
  - [ ] Format knowledge for prompt injection

- [ ] **Prompt Augmentation** (update `llm/prompts.py`)
  - [ ] Mutation prompt includes: top insights + failure warnings
  - [ ] Crossover prompt includes: complementary insights
  - [ ] Thought prompt asks to explain with knowledge context

### amure-do Integration into Evolution Loop

Update `evolution/manager.py`:
```
3. For each generation:
   a. Tournament selection
   b. Query amure-do for knowledge context + failure warnings  ← NEW
   c. LLM mutation (with knowledge injection)  ← UPDATED
   d. LLM crossover (with knowledge injection)  ← UPDATED
   e. Evaluation cascade (quick → full)
   f. Update population (elitism)
   g. Distill knowledge (compare top vs bottom → store insights)  ← NEW
   h. Check stagnation → request new directions from amure-do  ← NEW
```

### Phase 2 Milestone

**Milestone: Ablation — with/without Knowledge DB on ft10**

- Run 2 evolution experiments:
  1. With knowledge DB: `heuristix --config configs/default.yaml --knowledge-enabled`
  2. Without knowledge DB: `heuristix --config configs/default.yaml --knowledge-enabled false`
- Expected: Knowledge DB version shows fewer repeated failures + faster convergence
- Validation:
  - [ ] Knowledge distilled every generation (check amure-do `/graph`)
  - [ ] Knowledge injected into prompts (check logs)
  - [ ] Failure avoidance prevents repeat mistakes
  - [ ] With-DB version > without-DB version on ft10
  - [ ] Knowledge maturity transitions tracked

---

## Phase 3: Advanced Features

Evaluation cascade, thought-code co-evolution, stagnation handling.

### Evaluation Cascade

- [ ] **Cascade Runner** (`evaluation/cascade.py`)
  - [ ] Quick evaluation (ft06 only, fast validation)
  - [ ] Full evaluation (ft06 + ft10 + ft20, slower)
  - [ ] Promotion criteria (quick → full only if promising)
  - [ ] Time budgets per instance
  - [ ] Fallback on timeout

Update `evolution/manager.py`:
```
e. Evaluation cascade:
   - Quick eval on ft06 (fast filter)
   - If promising (top 50%): Full eval on ft06+ft10+ft20
   - Aggregate scores
```

### Thought-Code Co-Evolution

- [ ] **Thought Tracking** (`evolution/population.py`)
  - [ ] Store thought alongside heuristic code
  - [ ] Thought explains algorithm + key insight

- [ ] **Thought Prompts** (`llm/prompts.py`)
  - [ ] Generate thought before generating code
  - [ ] Mutation: evolve thought + code together
  - [ ] Crossover: blend two thoughts + blend code

- [ ] **Thought-Code Validation** (`evolution/operators.py`)
  - [ ] Ensure thought explains the code
  - [ ] Use thought in failure analysis

### Stagnation + Directed Search

- [ ] **Stagnation Detection** (`evolution/manager.py`)
  - [ ] Track fitness improvement per generation
  - [ ] Flag if plateau (no improvement for N generations)

- [ ] **Direction Requests** (`knowledge/selection.py`)
  - [ ] Query amure-do: "What new directions should we explore?"
  - [ ] amure-do returns gap analysis + recommendations
  - [ ] Inject recommendations into next mutation batch

- [ ] **Hierarchical Context** (`amure_client.py`)
  - [ ] Global context (all problems, all experiments)
  - [ ] Experiment context (ft06 vs ft10 vs ft20)
  - [ ] Heuristic context (individual family)

### Phase 3 Milestone

**Milestone: Full pipeline on ft06/ft10/ft20**

- Run: `heuristix --config configs/default.yaml --generations 30 --cascade`
- Expected: Evaluation cascade filters quick → full, thought-code co-evolution, stagnation recovery
- Validation:
  - [ ] Quick eval reduces computation (5x speedup vs full)
  - [ ] Thought-code pairs coherent (thought explains code)
  - [ ] Stagnation detected + new directions requested
  - [ ] Best final heuristic > baseline (ft06/ft10/ft20)

---

## Phase 4: Scaling + Paper

Large instances, ablations, baselines, paper writing.

### Large-Instance Evaluation

- [ ] **Taillard Extended** (`problems/jssp/benchmarks.py`)
  - [ ] Load all Taillard instances: ft06, ft10, ft20, la01-la40
  - [ ] Instance metadata (problem size, optimal/best known)

- [ ] **Adaptive Timeout** (`evaluation/cascade.py`)
  - [ ] Scale timeout by problem size
  - [ ] Budget constraints (e.g., 10 min per generation)

### Ablation Suite

- [ ] Experiment 1: Base (no knowledge)
- [ ] Experiment 2: + Knowledge DB
- [ ] Experiment 3: + Evaluation Cascade
- [ ] Experiment 4: + Thought-Code
- [ ] Experiment 5: Full pipeline
- [ ] Experiment 6: Different knowledge maturity thresholds
- [ ] Experiment 7: Different RAG search strategies (token/BFS/MMR)

Collect: final heuristic, convergence curve, computation time, knowledge utilization.

### Baseline Comparisons

- [ ] Compare with EoH (if code available)
- [ ] Compare with SeEvo (if code available)
- [ ] Compare with simple greedy baselines (SPT, LPT, FIFO)

### Visualization + Results

- [ ] **Convergence plots** — fitness vs generation
- [ ] **Knowledge graph viz** — insights + validations (from amure-do `/graph`)
- [ ] **Heuristic comparison** — side-by-side code + thought
- [ ] **Ablation summary** — bar chart of final makespan per variant
- [ ] **Timing breakdown** — evaluation vs LLM vs knowledge vs mutation

### Paper Writing

- [ ] Intro + Related Work
- [ ] Method section (knowledge-evolutionary framework)
- [ ] Experiments (ablation, baselines, large instances)
- [ ] Results + Analysis
- [ ] Discussion + Future Work

### Phase 4 Milestone

**Milestone: Full pipeline on Taillard la01-la40 + Paper submission**

- Run full ablation suite on ft06/ft10/ft20/la01-la40 (50 instances)
- Expected: HeuristiX > baselines, knowledge DB > no knowledge
- Validation:
  - [ ] All 50 instances solved without error
  - [ ] Knowledge DB improves convergence (statistical significance)
  - [ ] Evaluation cascade saves 5-10x computation
  - [ ] Thought-code explains final heuristic
  - [ ] Paper draft complete + ready for submission

---

## Cross-Phase Considerations

### Testing Strategy

- [ ] Unit tests for each module (JSSP simulator, metrics, operators, etc.)
- [ ] Integration tests (end-to-end evolution, ft06)
- [ ] Regression tests (baseline reproducibility)
- [ ] Performance benchmarks (simulator speed, LLM latency)

### Logging + Observability

- [ ] Generation logs (population stats, selected insights, mutations)
- [ ] Heuristic execution logs (failures, timeouts, invalid code)
- [ ] Knowledge distillation logs (extracted insights, confidence)
- [ ] Metrics summary (convergence, best fitness, computation time)

### Error Handling + Robustness

- [ ] LLM API failures → retry with exponential backoff
- [ ] amure-do unavailable → fallback to in-memory knowledge
- [ ] Invalid heuristic code → reject + resample
- [ ] Evaluation timeout → penalize fitness
- [ ] JSSP infeasibility → error handling (shouldn't happen)

### Documentation

- [ ] Code docstrings (module + function + class)
- [ ] Architecture guide (`ARCHITECTURE.md`)
- [ ] Configuration reference (`CONFIG.md`)
- [ ] How to add new problems (`EXTENDING.md`)
- [ ] How to add new LLM providers (`EXTENDING.md`)

---

## Summary by Timeline

| Phase | Weeks | Deliverable | Validates |
|-------|-------|-------------|-----------|
| 0 | 1 | Scaffolding | Structure, config |
| 1 | 3-4 | Basic evolution | EoH reproduction |
| 2 | 3-4 | Knowledge DB | Ablation: KB > no KB |
| 3 | 2-3 | Advanced features | Cascade, thought-code, stagnation |
| 4 | 3-4 | Full pipeline + paper | Large instances, baselines, publication |
| **Total** | **12-15 weeks** | **Production system** | **Paper submission** |

---

## How to Use This Roadmap

1. **Start with Phase 1**: Implement JSSP simulator + basic evolution loop. Get to "ft06 works" milestone.
2. **Move to Phase 2**: Integrate amure-do, distill knowledge, inject into mutations. Validate with ablation.
3. **Add Phase 3**: Cascade, thought-code, stagnation recovery. Full pipeline on ft06/ft10/ft20.
4. **Scale Phase 4**: Large instances, ablations, paper.

Each phase builds on the previous. Don't skip phases — skipping knowledge distillation (Phase 2) defeats the purpose of HeuristiX.

### Tracking Progress

- [ ] Phase 1 Milestone: `heuristix --config configs/default.yaml --generations 5` works on ft06
- [ ] Phase 2 Milestone: With-KB > without-KB on ft10 (ablation)
- [ ] Phase 3 Milestone: Full pipeline on ft06/ft10/ft20 (3 instances)
- [ ] Phase 4 Milestone: Paper + results on ft06/ft10/ft20/la01-la40 (50 instances)
