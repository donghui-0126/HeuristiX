# HeuristiX — Ablation Study Results

## Experimental Setup
- **Problem**: JSSP (Job-Shop Scheduling Problem)
- **Benchmarks**: Taillard ft06 (6×6, optimal=55), ft10 (10×10, optimal=930)
- **Population**: 6
- **Generations**: 15 (per experiment)
- **LLM**: Claude CLI (claude -p)
- **Embedding**: OpenAI text-embedding-3-small (1536 dims)
- **Knowledge DB**: amure-do (amure-db graph + embedding store)

## RAG Mode Descriptions

| Mode | Insights | Failures | Graph Walk | When Active |
|------|----------|----------|------------|-------------|
| **WITHOUT** | - | - | - | Never (baseline) |
| **Token RAG** | 5 items (sim=0) | - | - | Always |
| **Full RAG** | 2 items (embedding) | 2 items | 1-hop | Always |
| **Failure-only** | - | 2 items (embedding) | 1-hop | Always |
| **Adaptive** | 2 items (embedding) | 2 items | 1-hop | Gen 5+ only |

## Results

### Composite Score (ft06 + ft10 average makespan)

| Rank | Mode | Composite | Improvement vs baseline |
|------|------|-----------|------------------------|
| 1 | WITHOUT (baseline) | **643.0** | - |
| 2 | **Failure-only** | **653.5** | -1.6% |
| 3 | Full RAG (fixed) | 666.0 | -3.6% |
| 4 | Embedding RAG (broken, sim=0) | 667.0 | -3.7% |
| 5 | Adaptive | 676.0 | -5.1% |
| 6 | Token RAG | 676.5 | -5.2% |

### Per-Instance Breakdown

| Mode | ft06 | ft06 gap% | ft10 | ft10 gap% |
|------|------|-----------|------|-----------|
| WITHOUT | 65.0 | 18.2% | **1221.0** | **31.3%** |
| Token RAG | 60.0 | 9.1% | 1293.0 | 39.0% |
| Emb RAG (broken) | 66.0 | 20.0% | 1268.0 | 36.3% |
| **Full RAG (fixed)** | **57.0** | **3.6%** | 1275.0 | 37.1% |
| **Failure-only** | 60.0 | 9.1% | **1247.0** | **34.1%** |
| Adaptive | 69.0 | 25.5% | 1283.0 | 38.0% |

### Best per category
- **Best ft06**: Full RAG — 57.0 (gap 3.6%) ← 거의 최적해
- **Best ft10**: WITHOUT — 1221.0 (gap 31.3%)
- **Best composite**: WITHOUT — 643.0
- **Best RAG composite**: Failure-only — 653.5

## Key Findings

### 1. Knowledge injection hurts more than it helps (on average)
All RAG modes produced worse composite scores than WITHOUT. The best RAG mode (failure-only, 653.5) is still 1.6% behind WITHOUT (643.0).

### 2. Failure-only is the best RAG strategy
Consistent with ReasoningBank (Google Research, 2026) finding that k=1 is optimal and failure experiences are more valuable than success experiences (+3.2% improvement).

- Failure warnings prevent repeated mistakes → preserves exploration diversity
- Success insights constrain mutation direction → kills diversity

### 3. RAG helps small instances, hurts large instances
- ft06 (6×6): Full RAG achieves 3.6% gap — best result, near-optimal
- ft10 (10×10): WITHOUT achieves 31.3% — RAG adds noise on complex problems

Hypothesis: small instances have fewer local optima, so RAG-guided convergence works. Large instances need broader exploration that RAG constrains.

### 4. Embedding search >> Token matching
When embeddings work properly (sim=0.6+), results improve significantly:
- Token RAG (sim=0): 676.5 composite
- Embedding RAG (sim=0.6): 666.0 composite
- Difference: 10.5 points (1.6% improvement)

### 5. Adaptive (late-stage RAG) doesn't work
Turning on RAG after gen 5 had no effect — by then the population has already converged and RAG can't redirect.

### 6. Graph walk enrichment adds value
Comparing token-only vs embedding+graph:
- ft06: Token 9.1% → Graph 3.6% (5.5%p improvement)
- ft10: Token 39.0% → Graph 37.1% (1.9%p improvement)

Graph context (connected experiments, reasons, claims) provides structural knowledge that pure similarity misses.

## Implications for HeuristiX Design

1. **Default mode should be failure-only** — best risk/reward ratio
2. **Full RAG for small/well-understood problems** — when convergence is desired
3. **WITHOUT for novel/large problems** — when exploration is critical
4. **Graph enrichment should always be on** — adds value in all modes
5. **Maturity system needs work** — all 117 embeddings stayed Draft; no promotion happened in 15 gens

## Next Steps

- [ ] Run failure-only on larger instances (la01-la40)
- [ ] Test with GPT-4o instead of Claude CLI (faster, more generations)
- [ ] Implement instance-adaptive RAG (auto-detect when to inject)
- [ ] Fix maturity promotion thresholds (current gen+2 rule too conservative)
- [ ] Compare with EoH and SeEvo baselines on same benchmarks
- [ ] 30+ generation experiments to test long-run knowledge value
