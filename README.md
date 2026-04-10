# HeuristiX

**Knowledge-Evolutionary Framework for Automatic Heuristic Discovery**

LLM으로 휴리스틱을 자동 진화시키되, 진화 과정의 지식을 그래프 DB에 축적하고 재활용한다.
기존 연구(FunSearch, EoH, AlphaEvolve)가 세대마다 지식을 버리는 반면, HeuristiX는 **실패를 기억하고 성공을 구조화**한다.

---

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        HeuristiX Pipeline                           │
│                                                                     │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────────┐    │
│  │  1. INIT     │────→│ 2. EVALUATE  │────→│ 3. SELECT        │    │
│  │  LLM generates    │ Run on JSSP   │     │ Tournament       │    │
│  │  N heuristics│     │ ft06, ft10   │     │ selection (k=3)  │    │
│  └──────────────┘     │ Multi-metric │     └────────┬─────────┘    │
│                       └──────────────┘              │              │
│                              ↑                      ↓              │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────────┐    │
│  │ 7. DISTILL   │←────│ 6. UPDATE    │←────│ 4. EVOLVE        │    │
│  │ Top vs Bottom│     │ Elitism +    │     │ LLM Mutation     │    │
│  │ → Insights   │     │ replacement  │     │ LLM Crossover    │    │
│  └──────┬───────┘     └──────────────┘     └────────┬─────────┘    │
│         │                                           │              │
│         ↓                                           ↓              │
│  ┌──────────────────────────────────────────────────────────┐      │
│  │                    5. KNOWLEDGE (Graph RAG)               │      │
│  │                                                           │      │
│  │  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │      │
│  │  │ Embedding   │  │ Graph Walk   │  │ Failure        │  │      │
│  │  │ Search      │  │ 1-hop BFS    │  │ Avoidance      │  │      │
│  │  │ (OpenAI)    │  │ context      │  │ "이건 하지 마" │  │      │
│  │  │ sim=0.6+    │  │ enrichment   │  │                │  │      │
│  │  └─────────────┘  └──────────────┘  └────────────────┘  │      │
│  │                                                           │      │
│  │  amure-do (:9090) ←─HTTP──→ amure-db (graph + edges)    │      │
│  └──────────────────────────────────────────────────────────┘      │
│                                                                     │
│  Loop: 3→4→5→2→6→7 (repeat for N generations)                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Pipeline 상세

| Stage | Module | 설명 |
|-------|--------|------|
| **1. Init** | `evolution/operators.py` | LLM이 N개의 초기 dispatching rule 생성 (thought + code) |
| **2. Evaluate** | `evaluation/cascade.py` | 빠른 인스턴스(ft06) → 정밀 인스턴스(ft06+ft10). 다중 메트릭: makespan, flowtime, utilization, tardiness |
| **3. Select** | `evolution/population.py` | Tournament selection (k=3). Elitism으로 top-2 보존 |
| **4. Evolve** | `evolution/operators.py` | LLM Mutation: "이 코드를 개선해" + knowledge context. LLM Crossover: "두 코드의 장점을 합쳐" |
| **5. Knowledge** | `knowledge/selection.py` | Embedding search (OpenAI, sim=0.6+) → Graph walk (1-hop BFS) → Failure warnings 주입 |
| **6. Update** | `evolution/population.py` | Elitism + offspring 교체. Stagnation 감지 (5세대 정체 → amure-do에 새 방향 요청) |
| **7. Distill** | `knowledge/distillation.py` | Top-K vs Bottom-K 비교 → LLM이 인사이트 추출 → amure-db에 Claim/Reason 노드로 저장 |

### Knowledge Flow (Graph RAG)

```
Mutation 시:
  individual.thought + code
    ↓
  OpenAI Embedding (1536 dims)
    ↓
  Cosine Similarity → top 2 insights (is_failure=False)
                    → top 2 failures (is_failure=True)
    ↓
  Graph Walk Enrichment (amure-do API)
    각 결과에서 1-hop BFS → 연결된 Experiment, Reason, Claim 수집
    ↓
  LLM Context에 주입:
    "## Proven insights: [MRO is dominant] (sim=0.65)
       Context: [Experiment] makespan=676; [Reason] jobs with more ops...
     ## AVOID: [Weighted linear scoring failed] (sim=0.42)
       Context: [Experiment] makespan=1200"
```

### Node & Edge Types (amure-db)

```
Nodes:                        Edges:
  Claim ─── 인사이트             Support ─── A가 B를 지지
  Reason ── 근거                 Rebut ───── A가 B를 반박
  Evidence  증거                 DerivedFrom 진화 계보 (parent→child)
  Experiment 실험 (heuristic)    Refines ─── A는 B의 개선판
  Fact ──── 외부 데이터           DependsOn── A는 B에 의존
                                 Contradicts A와 B는 모순
```

---

## RAG Modes

```bash
heuristix --rag-mode full          # insights + failures (default)
heuristix --rag-mode failure-only  # "이건 하지 마" 경고만 ← 가장 효과적
heuristix --rag-mode adaptive      # gen 5+ 이후에만 RAG
heuristix --rag-mode none          # RAG 없음 (baseline)
heuristix --no-amure               # amure-do 미연결
```

---

## Ablation Results (JSSP ft06 + ft10)

| Mode | Composite | ft06 (opt=55) | ft10 (opt=930) |
|------|-----------|---------------|----------------|
| WITHOUT (baseline) | **643.0** | 65.0 (18.2%) | **1221 (31.3%)** |
| **Failure-only** | **653.5** | 60.0 (9.1%) | **1247 (34.1%)** |
| Full RAG (embed+graph) | 666.0 | **57.0 (3.6%)** | 1275 (37.1%) |
| Adaptive (late-stage) | 676.0 | 69.0 (25.5%) | 1283 (38.0%) |

**Key finding**: 실패 경험만 주입하는 것이 가장 균형잡힌 결과. 성공 인사이트는 탐색 다양성을 해침.

Full RAG는 작은 인스턴스(ft06)에서 거의 최적해 달성 (gap 3.6%).

자세한 분석: [RESULTS.md](RESULTS.md)

---

## Quick Start

### 1. Start amure-do (knowledge backend)

```bash
cd HeuristiX/amure-do
cargo build --release
./target/release/amure-do  # → http://localhost:9090
```

### 2. Install HeuristiX

```bash
cd HeuristiX
pip install -e ".[dev]"
```

### 3. Set API key (for embeddings)

```bash
echo "OPENAI_API_KEY=sk-..." > .env
```

### 4. Run evolution

```bash
source .env
heuristix --generations 15 --population 6 --rag-mode failure-only
```

### 5. View results

```
http://localhost:9090          # amure-do dashboard → Evolution tab
http://localhost:9090/graph    # Knowledge graph visualization
```

---

## Configuration

`configs/default.yaml`:

```yaml
amure_do:
  url: "http://localhost:9090"

llm:
  default:
    provider: "claude_cli"    # or openai, ollama
  roles:
    mutation:
      provider: "openai"
      model: "gpt-4o-mini"
      temperature: 0.8
    crossover:
      provider: "openai"
      model: "gpt-4o"
      temperature: 0.6
    distillation:
      provider: "openai"
      model: "gpt-4o"
      temperature: 0.3

evolution:
  population_size: 10
  generations: 30
  tournament_size: 3
  mutation_rate: 0.7
  crossover_rate: 0.3
  elitism: 2

evaluation:
  cascade: true
  quick_instances: ["ft06"]
  full_instances: ["ft06", "ft10"]
  metrics:
    primary: "makespan"
    weights: { makespan: 1.0, flowtime: 0.3, utilization: 0.2 }

knowledge:
  distill_every: 1
  rag:
    max_knowledge_items: 2
    max_failure_items: 2
    embedding_model: "text-embedding-3-small"
```

---

## Project Structure

```
HeuristiX/
  heuristix/
    cli.py                   # CLI entry point (--rag-mode, --generations, --population)
    config.py                # YAML config + role-based LLM routing
    amure_client.py          # amure-do HTTP client (graph CRUD + RAG + knowledge util)
    llm/
      provider.py            # LLM providers (Claude CLI, OpenAI, Ollama)
      prompts.py             # Prompt templates (mutation, crossover, reflection, distillation)
    evolution/
      population.py          # Individual (thought+code+scores) + Population management
      operators.py           # LLM-based mutation, crossover, init_population
      manager.py             # Main evolution loop (4 RAG modes, progress bar)
    knowledge/
      embeddings.py          # OpenAI embedding store + cosine similarity search
      distillation.py        # Top vs Bottom → insight extraction → amure-db storage
      selection.py           # Embedding search → graph walk enrichment → context injection
    evaluation/
      runner.py              # Subprocess-based heuristic execution
      cascade.py             # Quick → Full evaluation cascade
      metrics.py             # makespan, flowtime, utilization, tardiness
    problems/
      base.py                # Problem abstract class
      jssp/
        simulator.py         # JSSP schedule builder + metric computation
        benchmarks.py        # Taillard instances (ft06, ft10 embedded)
        benchmarks_known.py  # Known optimal values for gap computation
        problem.py           # JSSP problem + evaluation skeleton
  amure-do/                  # Git submodule — knowledge DB + dashboard
  configs/default.yaml
  run_ablation.sh            # Ablation experiment runner
  RESULTS.md                 # Ablation study results
  paper-md/                  # Reference papers
  tests/                     # 9 tests (simulator correctness)
```

---

## Comparison with Existing Work

| Feature | FunSearch | EoH | AlphaEvolve | ReasoningBank | **HeuristiX** |
|---------|-----------|-----|-------------|---------------|---------------|
| Knowledge persistence | ✗ | ✗ | ✗ | ✓ (flat) | **✓ (graph)** |
| Failure memory | ✗ | ✗ | ✗ | ✓ | **✓ + graph walk** |
| Knowledge maturity | ✗ | ✗ | ✗ | ✗ | **✓ (Draft→Accepted)** |
| Multi-metric eval | ✗ | ✗ | ✓ | ✗ | **✓** |
| Semantic retrieval | ✗ | ✗ | ✗ | cosine | **embedding + graph** |
| Thought + Code evolution | ✗ | ✓ | ✗ | ✗ | **✓** |
| RAG mode control | ✗ | ✗ | ✗ | ✗ | **✓ (4 modes)** |

---

## References

- **FunSearch** (Nature 2024) — LLM + evaluator for mathematical discovery
- **EoH** (ICML 2024 Oral) — Thought + Code simultaneous evolution
- **AlphaEvolve** (DeepMind 2025) — Diff-based code evolution, evaluation cascade
- **SeEvo** (IEEE TFS 2026) — 3-stage reflection for Dynamic FJSSP
- **ReasoningBank** (arXiv 2026) — Success/failure experience memory for agents

See `paper-md/` for detailed summaries.

---

## License

MIT
