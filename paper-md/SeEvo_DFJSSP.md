# Automatic Programming via Large Language Models With Population Self-Evolution for Dynamic Fuzzy Job Shop Scheduling Problem

**Journal:** IEEE Transactions on Fuzzy Systems, Vol. 34, No. 3, March 2026, pp. 896–908
**DOI:** 10.1109/TFUZZ.2025.3650586
**Source Code:** https://github.com/huangjincollab/LHH DFJSP SeEvo

---

## Authors and Affiliations

- **Jin Huang** — Ph.D. candidate, Mechanical Engineering, HUST. Research interests: operations research, reinforcement learning, large language models. Email: huangjin_@hust.edu.cn
- **Qihao Liu** — Ph.D. (Industrial Engineering, HUST, 2022), Postdoctoral Research Associate, School of Mechanical Science and Engineering, HUST. Research interests: process planning and shop scheduling. Email: lllqh@hust.edu.cn
- **Xinyu Li** (Member, IEEE) — Professor, Department of Industrial Manufacturing Systems Engineering, State Key Laboratory of Intelligent Manufacturing Equipment Technology, School of Mechanical Science Engineering, HUST. Ph.D. (Industrial Engineering, HUST, 2009). Author of 100+ refereed papers. Research interests: intelligent algorithm, big data, machine learning. **Corresponding author.** Email: lixinyu@mail.hust.edu.cn
- **Liang Gao** (Senior Member, IEEE) — Professor, Department of Industrial Manufacturing System Engineering, HUST. B.Sc. (Xidian University, 1996), Ph.D. (HUST, 2002), both in mechatronic engineering. Author of 400+ refereed papers. Research interests: operations research and optimization, big data, machine learning. Co-Editor-in-Chief for IET Collaborative Intelligent Manufacturing; Associate Editor for Swarm and Evolutionary Computation and Journal of Industrial and Production Engineering. Email: gaoliang@mail.hust.edu.cn
- **Yue Teng** — Ph.D. candidate, Mechanical Engineering, HUST. B.E. (Industrial Engineering, HUST, 2020). Research interests: operations research, evolutionary algorithms, engineering application methods. Email: yt9883@gmail.com

All authors are with the **National Intelligent Design and CNC Technology Innovation Center, School of Mechanical Science and Engineering, Huazhong University of Science and Technology (HUST), Wuhan 430074, China**.

**Funding:** National Natural Science Foundation of China (Grant 52188102); Strategic Science and Technology Talent Training Program of Hubei Province (Grant 2024DJA033); Key Research and Development Program of Zhejiang Province (Grant 2024C01139); Fundamental Research Funds for the Central Universities (Grant 2024BRA004).

**Dates:** Received 21 August 2025; revised 9 November 2025; accepted 22 December 2025; published 5 January 2026; current version 3 March 2026.

---

## Abstract

Heuristic dispatching rules (HDRs) are widely used for solving the dynamic fuzzy job shop scheduling problem (DFJSSP). However, their performance is highly sensitive to specific scenarios and often necessitates expert customization. To overcome this, automated design methods such as genetic programming (GP) and gene expression programming (GEP) have been proposed. Despite their success, these methods face challenges such as high randomness in the search process. Recently, the combination of large language models (LLMs) with evolutionary algorithms has opened new possibilities for prompt engineering and automated algorithm design.

To improve the ability of LLMs in automatic HDR design, this article introduces a novel **population self-evolutionary (SeEvo) framework**, which draws inspiration from the self-reflective design strategies employed by human experts. Notably, this framework employs a novel **teacher-student learning mechanism**, allowing the LLM (student) to generate robust HDRs. Guided by a teacher model with complete knowledge of actual processing times, the student learns to infer fuzzy uncertainties from historical deviations, enabling it to effectively anticipate and adapt to fuzzy impacts.

Experimental results demonstrate that SeEvo significantly outperforms GP, GEP, deep reinforcement learning methods, and more than ten commonly used HDRs from the literature, particularly in previously unseen and dynamic scenarios.

**Index Terms:** Automatic heuristic dispatching rules (HDRs) design, dynamic fuzzy job shop scheduling problem (DFJSSP), large language models (LLMs), self-evolutionary (SeEvo).

---

## I. Introduction

### 1.1 Problem Context and Motivation

The core challenge in production scheduling is the efficient allocation of limited resources to complete tasks in a timely manner while optimizing performance metrics. The **job shop scheduling problem (JSSP)** is an NP-hard formulation of this challenge. For static JSSP, where all parameters such as processing times and job orders are predetermined, traditional exact methods (dynamic programming, branch-and-bound) are computationally infeasible for large-scale instances. Researchers have largely shifted toward metaheuristic algorithms, which yield near-optimal solutions within reasonable timeframes.

However, real-world manufacturing environments are rarely static and often subject to dynamic uncertainties:
- Unexpected machine breakdowns
- Arrival of new orders
- Fuzzy (uncertain) processing times

This has led to growing interest in the **dynamic fuzzy job shop scheduling problem (DFJSSP)**. In dynamic and uncertain production environments, HDRs are often preferred for their low computational complexity and rapid responsiveness. The primary challenge lies in designing effective HDRs, traditionally requiring expert knowledge and extensive trial-and-error.

### 1.2 Prior Work and Limitations

**Evolutionary hyperheuristics:**
- GP and GEP have demonstrated potential in automating HDR design and optimization
- Limitation: rely primarily on stochastic search operators (random mutation and crossover) for exploration

**Deep Reinforcement Learning (DRL):**
- Emerged as a complementary paradigm, with strong capabilities in learning scheduling policies through environment interaction
- Inference times typically under one second after training — well-suited for real-time decisions (e.g., electronics assembly)
- Limitation: relies on environment-driven policy learning with fixed neural network policies

**LLM-based approaches (recent):**
- Combining prompt engineering with iterative feedback enables generation of highly adaptive domain-specific HDRs
- Research has demonstrated LLM potential for automatic algorithm design (e.g., online BPP)
- Application to DFJSSP remains largely unexplored

**Critical bottleneck of existing LLM approaches:** They rely on lengthy iterative evolution processes that typically require tens of minutes to generate high-performance rules, making them impractical for dynamic environments where workshop conditions can change within minutes.

### 1.3 Key Insight: Fuzzy Uncertainty as an Information Gap Problem

The paper reframes the fuzzy scheduling problem: rather than treating deviations as dynamic events that trigger reactive adjustments, fuzzy uncertainty is treated as a **decision-making task under incomplete information**. The goal is to develop a scheduling model that can infer and anticipate the effects of uncertainty — proactively rather than reactively.

### 1.4 Contributions

1. **Novel LLM-based evolutionary framework for DFJSSP:** Introduces a training paradigm that teaches the LLM to generate robust HDRs by learning from the gap between planned and actual processing times, enhancing resilience to stochastic uncertainty.

2. **Population self-evolution strategy (SeEvo):** A novel population self-evolution strategy within the LLM-based framework that significantly improves exploration and exploitation capabilities of generated heuristics. Allows continuous refinement of HDRs based on real-time feedback during scheduling, enhancing efficiency in dynamic environments.

3. **Comprehensive evaluation:** SeEvo's effectiveness is demonstrated through extensive comparisons with commonly used HDRs, GP, GEP, and DRL methods. Results demonstrate superior generalization across unseen and dynamic DFJSSP, outperforming other dynamic scheduling methods.

---

## II. Background

### 2.1 Related Works: Fuzzy Job Shop Scheduling Problem

**Exact methods:** Dynamic programming and branch-and-bound guarantee optimal solutions but are limited to small-scale problems due to high computational complexity.

**Metaheuristic methods:** Genetic algorithms, tabu search, simulated annealing — widely adopted for larger scale problems. Notable examples:
- Differential evolution with improved selection mechanism for FJSSP
- Hybrid local simulated annealing combined with NSGA-II for multiobjective FJSSP
- Hybrid particle swarm optimization with genetic algorithms
- Self-learning discrete artificial bee colony algorithm for fuzzy welding seam scheduling (using LR fuzzy numbers)

**Limitation of metaheuristics:** Face significant challenges in highly dynamic environments (frequent order arrivals, machine breakdowns) — difficult to achieve high-quality solutions within acceptable computational times.

**HDRs:** Gained popularity due to simplicity, efficiency, and responsiveness to real-time changes. However, effectiveness is highly dependent on specific scenarios and requires extensive expert knowledge for customization.

**Hyperheuristics (GP and GEP):** Enable automatic learning of scheduling heuristics without domain-specific prior knowledge. Suitable for DJSSP. However:
- Large feature space of DFJSSP exponentially increases search space, hindering exploration efficiency
- Heuristics may not generalize well to unseen DFJSSP instances

**DRL methods:** Significant attention for workshop scheduling. Categorized as:
- *Rule-selection-based DRL:* agents select from predefined rules
- *End-to-end DRL:* directly maps states to job-machine assignments via graph neural networks (GNNs)

Representative end-to-end methods employ:
- Heterogeneous graph neural networks (metapath-based architectures, dual-shop frameworks, structure-aware encoders)
- Attention mechanisms
- For DFJSSP: uncertain processing times addressed via uniform distributions, asymmetric triangular intervals, and LR fuzzy numbers

DRL scheduling policies exhibit strong size-invariant properties enabling generalization to unseen instances. Some researchers have incorporated GP-based action spaces into DRL frameworks, combining strengths of both paradigms.

**Key distinction from SeEvo:** DRL learns implicit neural network policies through extensive environment interaction and requires manual design of reward functions, action spaces, and state representations. SeEvo's language-heuristic approach leverages LLMs' pretrained knowledge to generate interpretable heuristic code through evolutionary search guided by natural language.

### 2.2 Automatic Algorithm Design With LLMs

The field aims to reduce human effort in developing high-performance algorithms. The hyperheuristic approach searches the space of heuristics rather than solution space.

**Traditional generative hyperheuristics (GP, GEP):** construct algorithms by evolving from a predefined set of components.

**LLMs as algorithm designers:** LLMs can automatically design the internal logic of a heuristic, often requiring only the function signature (name, inputs, outputs). This moves beyond fixed component sets — a conceptual leap from *combinatorial selection* to *creative generation*.

**Key precedents:**
- **Liu et al. (2023):** Algorithmic self-evolution framework (GPT-4o) to automatically evolve TSP heuristics
- **Romera-Paredes et al. (2024, Nature):** Combined fine-tuned PaLM2 (340B) with evolutionary framework; introduced multi-island collaborative program library update mechanism; achieved optimal results for online BPP
- **Mischler et al. (2024, Nature Machine Intelligence):** LLMs exhibit increasingly brain-like processing capabilities, providing theoretical support for their application in optimization tasks

**ReEvo framework [19]:** Advanced language-heuristic approach that simulates human expert reflection through short-term reflection (comparative learning of individual differences) and long-term reflection (summarizing short-term reflections). Performed well on TSP. Limitations:
- Primarily designed for static problems (does not distinguish training/test sets)
- Has not fully explored population self-evolution potential
- Complexity of DFJSSP far exceeds TSP (multiple jobs, multiple machines, dynamic events: fuzzy times, dynamic order arrivals, machine breakdowns)

---

## III. Framework: Language-Heuristic-Based DFJSSP

### 3.1 Overview

The Language-Heuristic-Based DFJSSP framework (Fig. 1) consists of two stages:

1. **Self-evolution stage** (training phase)
2. **Online application stage** (deployment phase)

The framework addresses DFJSSP with:
- Randomly arriving orders
- Fuzzy processing times
- Machine breakdowns

A job shop simulation environment handles these uncertainties and dynamic conditions. A language-heuristic-based SeEvo method is developed to evolve HDRs.

### 3.2 Problem Formulation and Input Features

During the self-evolution stage, the DFJSSP environment consists of a job pool and a set of machines. Statistical data of incoming jobs is input into the LLM, including the following features for each job:

| Feature | Symbol | Description |
|---------|--------|-------------|
| Processing time (current operation) | `pt` | Processing time of current operation |
| Remaining work time | `wkr` | Total remaining work time |
| Remaining processing time (excl. current op) | `rm` | Remaining processing time excluding current operation |
| Subsequent operation processing time | `so` | Processing time of subsequent operations |
| Total processing time | `twk` | Total processing time across all operations |
| Exponential moving average | `ema` | EMA-based fuzzy deviation tracker (see Section 3.3) |
| Due date | `dd` | Job due date |
| Estimated tardiness | `et` | Estimated tardiness |

Based on these statistical features, the LLM generates the HDR used for job sequencing. Only top-ranked jobs are available for the scheduling process. When a job's operation is completed, the machine becomes available and selects a new job from the pool.

### 3.3 Teacher-Student Learning Mechanism for Fuzzy Uncertainty

A core innovation is handling fuzzy deviation between planned and actual processing times.

**The problem:** In real-world scenarios, the scheduling algorithm knows only the planned processing time `p_ij`, while actual time `p'_ij` remains uncertain.

**The solution — Teacher-Student paradigm:**
- **Teacher:** The simulation environment, which has complete knowledge of actual processing time `p'_ij`
- **Student:** The LLM, which knows only planned processing time `p_ij` and other observable states

**The EMA (Exponential Moving Average) mechanism:** The key mechanism enabling the student to anticipate fuzzy uncertainties. The relative deviation `(p'_ij / p_ij) - 1` is tracked using the exponential fuzzy time smoothing formula:

```
phi_ij = kappa_ij * delta_ij + (1 - kappa_ij) * phi_{i-1,j}     (Equation 1)
```

Where:
- `kappa_ij` = fuzzy adaptive adjustment coefficient (set to **0.2** in experiments)
- `delta_ij` = latest relative deviation
- `phi_ij` = updated smoothing factor

The updated smoothing factor `phi_ij` is mapped back to time-related metrics (pt, wkr), creating the `ema` feature. By injecting `ema` into the LLM's prompt, the HDR can leverage historical deviation trends, enabling implicit accounting for future time fluctuations — enhancing robustness and foresight.

### 3.4 Two-Stage Framework Operation

**Self-evolution stage (training):**
- Processes numerous cases to accumulate experience and refine HDRs
- Trained on 20 selected cases in experiments
- One case replaced after each iteration
- Generates substantial training data and updates HDRs iteratively

**Online application stage (deployment):**
- Utilizes the best HDRs generated during self-evolution
- Applies HDRs to real-world scenarios in a single inference pass
- After one iteration of the self-evolution framework, high-quality HDRs are produced for practical use
- Example: tested with 100 jobs and 20 machines, framework provides a high-quality solution within **40 seconds**

This two-stage design directly addresses the timeliness bottleneck of prior LLM-based approaches: the costly evolution happens offline, and deployment is fast.

---

## IV. Population Self-Evolution Method (SeEvo)

### 4.1 Framework Overview

The SeEvo framework is a language-driven heuristic evolution method (Fig. 2). LLMs play two key roles:
1. Generating guiding prompts for the population
2. Creating individual heuristic code segments

Unlike traditional hyperheuristic methods, SeEvo relies on independent generation of heuristic code fragments, continuously refined through the evolutionary process. SeEvo follows a multistage iterative procedure, with each phase contributing to progressive refinement of the heuristic population.

### 4.2 Individual Encoding and Initialization

**Encoding:** Individuals are code fragments (HDRs) rather than fixed-length representations. No constraints on encoding length or predefined function sets. The only requirement: LLM-generated code must adhere to specific function names, input parameters, and output parameters.

**Example seed function (`Seed_func`):**
- Function name: `get_combined_expression_v1`
- Inputs: `pt`, `wkr`, `rm`, `so`, `twk`, `ema`, `dd`, `et`
- Output: `combined_expression_data` (generated by combining input parameters)

**Initialization:** Facilitated by the LLM prompt generator, which uses `seed_func` along with detailed generation instructions specifying function name and associated heuristic logic. Seed heuristics guide the LLM in generating initial HDRs in promising search directions.

### 4.3 Reflection-Evolution Loop

The framework operates through an iterative loop: individuals are evaluated, reflected upon, and evolved to generate superior candidates. Three reflection mechanisms and three evolution operators orchestrate this process.

#### Reflection Operators

**1. Individual Co-Evolution Reflection (R_co):**
Compares two randomly selected HDRs to analyze performance disparities. The reflector LLM takes two parent individuals H_i and H_j along with their performance metrics (Perf_i, Perf_j) and generates a comparative reflection:

```
R_co = LLMReflect(Prompt_co-reflect, H_i, H_j, Perf_i, Perf_j)     (Equation 2)
```

R_co subsequently serves as guidance for the crossover operator.

**2. Individual Self-Evolution Reflection (R_self):**
The core contribution of SeEvo. Following crossover offspring generation, compares each offspring H_child with its corresponding parent H_parent. The performance differential `Delta_P = Perf(H_child) - Perf(H_parent)` is analyzed:

```
R_self = LLMReflect(Prompt_self-reflect, H_parent, H_child, Delta_P)     (Equation 3)
```

- When `Delta_P <= 0`: R_self functions as failure analysis to prevent recurring errors
- When `Delta_P > 0`: R_self reinforces successful strategies

R_self subsequently guides the self-evolution process within the crossover operator.

**3. Collective Evolution Reflection (R_coll):**
The framework's long-term memory. Synthesizes all local reflections into accumulated evolutionary knowledge. At the conclusion of each generation t, all local insights form a reflection set:

```
R_gen_t = {R^1_co, ..., R^M_co} union {R^1_self, ..., R^N_self}
```

This is synthesized with memory from the previous generation:

```
R^(t)_coll = LLMSynthesize(Prompt_collective, R^(t-1)_coll, R_gen_t)     (Equation 4)
```

The updated R^(t)_coll guides all evolution operators in the subsequent generation.

#### Evolution Operators

**4. Crossover:**
Performs intelligent semantic fusion guided by both local and global reflections, operating through two distinct processes:

**Co-evolution crossover:** Receives parent HDRs (H_i, H_j), their co-evolution reflection (R_co), and collective wisdom R^(t-1)_coll:

```
H_child = LLMCrossover(Prompt_cross, H_i, H_j, R_co, R^(t-1)_coll)     (Equation 5)
```

This dual-guidance mechanism enables strategy-level reasoning to coherently synthesize complementary strengths from both parents.

**Self-evolution refinement:** After co-evolution crossover, each offspring H_child is refined using its self-evolution reflection and collective memory:

```
H^new_child = LLMCrossover(Prompt_cross, H_parent, H_child, R_self, R^(t-1)_coll)     (Equation 6)
```

Through this two-stage crossover, the algorithm learns from both successful and failed evolutionary attempts, progressively improving offspring quality via reflection-guided refinement.

**5. Mutation:**
Transforms random perturbation into knowledge-driven exploration. Leverages collective memory R^(t)_coll to guide strategic modifications of elite individuals H_elite:

```
H_mutant = LLMMutate(Prompt_mutate, H_elite, R^(t)_coll)     (Equation 7)
```

This enables intelligent modifications grounded in accumulated evolutionary knowledge.

**6. Individual Evaluation:**
Each HDR undergoes rigorous evaluation with respect to the scheduling task. Optimization objectives encompass:
- Makespan minimization
- Tardiness minimization

This evaluation mechanism ensures continuous refinement of the population toward optimal solutions.

### 4.4 Relationship Between SeEvo and ReEvo

SeEvo extends the ReEvo framework by adding Individual Self-Evolution Reflection (R_self) and the two-stage crossover refinement process. The ablation study (Section V.F) validates that removing self-evolution (reverting to ReEvo) degrades performance, particularly on complex scheduling problems.

---

## V. Experimental Evaluation

### 5.1 Experimental Setup

**Benchmark datasets:**
- **Static:** Taillard (TA) and Demirkol (DMU) publicly available benchmark datasets
- **Dynamic:** DFJSSP environment with randomly generated order variations, machine breakdowns, and fuzzy processing times (simulation)

**Objectives evaluated:** Makespan minimization and tardiness minimization

**LLM APIs used:**
- `gpt-4.1-mini-2025-04-14`
- `Qwen-Turbo`
- `DeepSeek-V3`
- Note: DeepSeek-R1 excluded due to slow response time

**Comparison methods:**
- GEP algorithm
- GP algorithm
- 10+ common HDRs (see Sections 5.3–5.5)
- End-to-end DRL methods: DRL-Chen [16], DRL-Zhang [39], DRL-Liu [26]

**Note on GP/GEP comparison:** GP and GEP in literature are primarily for flexible JSSP. The paper references them only for job selection, using similar statistical feature selections as in SeEvo. To avoid unfair comparison, 80 training cases are introduced for GP/GEP (20 generations per round), with cases replaced after each round. Population size for GP/GEP is set to 20, matching SeEvo.

**Implementation:** All methods implemented in Python, executed on Ubuntu 20.04 with Intel Xeon W-3365 CPU @ 2.70 GHz.

### 5.2 Dataset Generation Details

**Static dataset:** SeEvo's generalization performance assessed on randomly generated training cases:
- Job sizes: 20 to 100 jobs
- Machine counts: 10 to 20 machines
- Processing times: randomly assigned between 50 and 100 units

**Dynamic dataset:** 20 training cases generated:
- Jobs per batch: 20 to 50 (randomly)
- Subbatches per batch: 2 to 3
- Arrival times: uniformly distributed within [1, 500] and [501, 1000]
- Machines: 5 to 20
- Processing times: randomly assigned between 50 and 100 units
- Machine breakdowns: 1 to 2 per case
- Breakdown durations: 1 to 500 time units
- Repair times: 10 to 50 units
- Fuzzy noise: **gamma-distributed perturbation** (shape parameter = 1.0, scale parameter = 0.10)

**Training protocol:** 20 randomly generated cases used; one case replaced after each iteration. During testing, crossover and mutation probabilities remain constant; number of generations reduced to one.

### 5.3 Parameter Selection (Taguchi Design)

Parameter selection is performed using **Taguchi orthogonal experimental design** (L9 orthogonal array). Four parameters are tuned:

| Parameter | Levels Tested | Optimal Value |
|-----------|--------------|---------------|
| Population size | {10, 15, 20} | **20** |
| Maximum iterations | {10, 15, 20} | **20** |
| Mutation rate | {0.5, 0.7, 0.9} | **0.9** |
| LLM temperature | {0, 0.5, 1.0} | **1.0** |

Each parameter combination is independently evaluated three times across four training cases (two static + two dynamic). Analysis performed using Minitab 18 (Fig. 3: Main effect plot).

**Note:** Population size and maximum iterations are intentionally constrained to balance performance improvements against computational costs of LLM API calls.

### 5.4 Generalization Performance on Public Benchmarks (Makespan Optimization)

**Scope:** 160 benchmark cases from TA and DMU datasets, covering eight distinct problem sizes.
- TA test set sizes: 15×15 to 100×20
- DMU test set sizes: 20×15 to 50×20

#### Performance on DMU Benchmark (Table II, Table III)

**Comparison methods (Table II):** Random selection, SPT (Shortest Processing Time), STPT (Shortest Total Processing Time), MPSR (Most Process Sequence Remaining), MWKR (Most Work Remaining), FDD/MWKR (Minimum ratio of flow due date to most work remaining), MOPNR (Most Operations Remaining), MTGP, GEP, DRL-Liu [26], DRL-Zhang [39], SeEvo.

**Table II results:** SeEvo outperforms other methods in **14 out of 16** test cases; ranks second in remaining two cases with minimal differences (only one unit behind in DMU29).

**Table III results (arithmetic mean makespan per problem size):** SeEvo outperforms all alternatives, followed by GP and GEP, which surpass traditional HDRs and DRL-Zhang [39].

#### Performance on TA Benchmark (Table IV, Table V)

**Comparison methods:** DRL-Chen [16], DRL-Zhang [39], DRL-Liu [26], SPT/TWKR, MWKR, FDD/MWKR, MOPNR, GP, GEP.

**Table IV results:** SeEvo outperforms other approaches in **13 out of 16** test cases; ranks second in remaining three cases.

**Table V results (arithmetic mean per problem size):** SeEvo demonstrates generalization ability across all TA datasets.

#### LLM Comparison (Inference Performance)

| LLM | Ranking | Time (100 jobs, 20 machines) | Relative API Cost |
|-----|---------|------------------------------|-------------------|
| gpt-4.1-mini | Best | ~42 s | 3x (baseline) |
| DeepSeek-V3 | Second | ~122 s | ~1x (one-third of GPT) |
| Qwen-Turbo | Third | ~40 s | — |

DeepSeek-V3 offers substantially lower API costs (approximately one-third of gpt-4.1-mini), making it practical for cost-sensitive applications where response time is not critical.

**Known limitation:** A gap remains between SeEvo's results and optimal solutions on static benchmark cases. Suggested future direction: deploy local LLMs with vector databases to match similar training instances.

### 5.5 Performance Evaluation in Dynamic Cases (Makespan Optimization)

**Evaluation scope:** 100 test cases in dynamic environment (fuzzy processing times, randomly arriving orders, machine breakdowns and repairs).

**Comparison methods (Fig. 4):** SeEvo vs. 9 common HDRs (SPT, TWKR, SRM, SSO, LPT, LPT/TWK, SPT×TWK, SPT+SSO, SPT/LSO), GP, GEP — total 14 methods.

**Performance metric — Gap Ratio:**

```
Gap ratio (%) = (Obj_{i,j} - Obj_{i,best}) / Obj_{i,best} * 100     (Equation 8)
```

Where:
- `Obj_{i,j}` = objective value of algorithm j on problem case i
- `Obj_{i,best}` = minimum objective value among all 14 compared methods for that case

**Results (Fig. 4):**
- SeEvo consistently demonstrates significant advantages under dynamic conditions
- Smallest relative gap among all methods
- **Maximum gap ratio does not exceed 5%**
- In most cases, gap ratio remains **below 1%**

**Attribution of SeEvo's dynamic performance:**
1. Integrates extensive domain knowledge enabling generation of generalized HDRs
2. Training on 20 randomly sized order batches enhances generalization to new scenarios
3. Effective decision-making with a single iteration
4. Self-evolution improves both exploration and exploitation through three reflection mechanisms

### 5.6 Performance Evaluation in Dynamic Cases (Tardiness Optimization)

**Evaluation scope:** 100 test cases with fuzzy processing times, random job arrivals, machine breakdowns and repairs.

**Due date definition:**
- Each job's due date = sum of its operation processing times
- For newly arriving orders: due date = arrival time + total processing time of all operations

**Note on experimental setup:** Due dates were intentionally set shorter to create clearer distinctions in tardiness levels across methods. Longer due dates would result in many cases with zero tardiness, limiting method differentiation.

**Comparison methods (Fig. 5):** EDD (Earliest Due Date), estimated maximum tardiness, SPT, TWKR, SRM, SSO, LPT/TWK, SPT×TWK, SPT+SSO, GP, GEP — total 14 methods.

**Results (Fig. 5):**
- SeEvo consistently achieves the smallest relative gap
- **Maximum gap ratio does not exceed 6%**
- In most cases, gap ratio remains **below 1%**
- SeEvo slightly outperforms DeepSeek-V3 and Qwen-Turbo variants

### 5.7 Ablation Studies

#### Ablation Study 1: Individual Self-Evolution (SeEvo vs. ReEvo)

**Setup:** Remove individual self-evolution process from SeEvo → resulting method called "ReEvo." Compare exploration and exploitation capabilities:
- Training: 50 iterations on static training datasets (Tables II and IV)
- Each method independently executed **10 times**
- Results shown with mean values and standard deviations (shaded areas) in Fig. 6

**Fig. 6 convergence curves (8 subfigures):**
- DMU: (a) Overall Comparison, (b) GPT-4.1-mini Comparison, (c) DeepSeek-V3 Comparison, (d) Qwen-Turbo Comparison
- TA: (e) Overall Comparison, (f) GPT-4.1-mini Comparison, (g) DeepSeek-V3 Comparison, (h) Qwen-Turbo Comparison

**Key findings:**
- All LLM-based methods significantly outperform traditional GP and GEP baselines — guided exploration is substantially more effective than random search
- SeEvo variants consistently outperform ReEvo counterparts in mid-to-late iteration stages (both datasets)
- **DMU dataset (complex):** Convergence curves of SeEvo and ReEvo exhibit limited overlap after **15–20 iterations** — gap is more pronounced
- **TA dataset (simpler):** Higher degree of overlap, suggesting self-evolution advantages are particularly evident on complex problems

**Generalization test (Table VI):** ReEvo evaluated on TA test sets for two problem sizes:
- 30 jobs × 20 machines (10 cases)
- 50 jobs × 20 machines (10 cases)
- Objective: minimization of completion time

Table VI shows SeEvo outperforms ReEvo and two end-to-end DRL methods [26].

**Explanation of SeEvo's advantage over DRL in generalization:** Unlike DRL with fixed neural network policies trained on specific data distributions, SeEvo continuously evolves its HDR library through iterative refinement guided by LLM reasoning. The combination of evolutionary diversity and semantic reasoning enables SeEvo to better anticipate and respond to variations in problem scales and processing time distributions.

#### Ablation Study 2: EMA Feature Validation

**Setup:** Compare performance of heuristics generated with vs. without the `ema` feature on 100 randomly generated dynamic instances.

**Results (Figs. 7 and 8):**

*Fig. 7 — Violin plots (gap ratio distribution and stability):*
- Policies incorporating `ema`: significantly lower median gap (better performance) AND narrower distribution → enhanced robustness

*Fig. 8 — Best solution quality and average makespan:*
- SeEvo with `ema`: secured far greater number of best solutions
- Consistently lower average makespan

**Conclusion:** The `ema` feature is critical for generating robust heuristics that effectively mitigate uncertainty.

---

## VI. HDR Complexity Analysis and Hardware Comparison

### Generated HDR Examples

**Fig. 9** shows HDRs generated by two API models on the TA72 case:
- Upper portion (lighter): HDR from DeepSeek-V3
- Lower portion (darker): HDR from GPT-4.1-mini-2025-04-14

**Fig. 10** shows HDRs generated by GP and GEP on the TA72 case.

### Complexity Analysis

| HDR Source | Time Complexity | Notes |
|-----------|----------------|-------|
| GPT-4.1-mini | O(n) | Computationally efficient and more logical |
| GP | O(n) | Extreme nesting leads to high computational overhead and limited interpretability |
| GEP | O(n) | — |
| DeepSeek-V3 | O(n²) | Due to iterative structures — less efficient |
| Human-designed (SPT, LPT, EDD) | O(n) | Tailored for specific problems; lack scalability and flexibility |

SeEvo-generated HDRs strike a balance: computationally efficient and more logical than GP-generated rules, while more flexible than human-designed HDRs.

### Hardware Requirements

| Method | Hardware Requirement |
|--------|---------------------|
| DRL methods [26] | Intel Core i7 4.0GHz CPU + NVIDIA GeForce GTX TITAN X GPU |
| SeEvo (API-based) | No high-end GPU required — runs on CPU with API calls |
| SeEvo (local LLM) | High-performance GPU (e.g., NVIDIA GeForce RTX 4090D) for full capability |

SeEvo significantly reduces reliance on high-performance GPUs compared to DRL methods. Although external API usage incurs cost, SeEvo depends on LLMs' enhanced analytical capabilities.

---

## VII. Discussion

### 7.1 Context-Dependence of Scheduling Methods

The superiority of any scheduling method is highly context-dependent and should be evaluated based on specific case characteristics. No single dynamic scheduling approach currently demonstrates absolute superiority across all scenarios — different methods may excel under different problem configurations, constraints, and operational conditions.

### 7.2 Limitations

1. **External API dependency:** LLMs used via costly external API calls without direct fine-tuning for specific DFJSSP knowledge
2. **Single HDR in dynamic cases:** Only a single HDR is employed in dynamic cases, limiting performance and preventing achievement of the absolute superiority observed in static cases
3. **Gap from optimal solutions:** A gap remains between SeEvo results and optimal solutions on static benchmark cases

### 7.3 LLM-Based Scheduling as a Research Direction

LLM-based approaches represent a promising research direction warranting further exploration, particularly given their potential for:
- Semantic understanding
- Adaptive reasoning in complex scheduling environments
- Creative generation of novel heuristics

---

## VIII. Conclusion and Future Work

### 8.1 Conclusion

This article proposes a dynamic evolutionary framework leveraging LLMs to address poor generalization and reliance on random search in automatic algorithm design for DFJSSP. The innovative SeEvo method is comprehensively validated through both static and dynamic fuzzy processing time case studies (primary focus: makespan optimization).

**Key findings:**
- SeEvo outperforms commonly used HDRs, GP, GEP, and DRL methods in static generalization performance
- In dynamic fuzzy processing time experiments, SeEvo exhibits substantial advantages in most cases
- Success in fuzzy environments is a direct result of the teacher-student learning framework: the LLM learns to anticipate time deviation impacts via the `ema` feature
- SeEvo consistently shows notable advantages in tardiness optimization over HDRs, GP, and GEP

These findings highlight the potential of LLMs in generating adaptive HDRs, benefiting from advanced language understanding and generative capabilities to address scheduling under uncertainty.

### 8.2 Future Work

Three directions are identified:

1. **Local LLM deployment:** Transition to locally deployed LLMs (e.g., Qwen-7B/8B) to reduce computational costs and enable larger scale experiments. Apply fine-tuning techniques such as **direct preference optimization (DPO)** to enhance domain-specificity of generated HDRs.

2. **Improved generalization on static datasets:** Incorporate a **SimGNN-based approach** to select optimal HDRs by matching graph-structural similarity of new problems with a case database.

3. **Multi-HDR ensemble for dynamic environments:** Utilize a combination of multiple HDRs to enable further optimization of performance in real-time scenarios.

---

## Key Figures and Tables Reference

| Figure/Table | Description |
|-------------|-------------|
| Fig. 1 | Language-heuristic-based DJSSP framework (two-stage: self-evolution + online application) |
| Fig. 2 | Population self-evolution method diagram showing all operators and reflection mechanisms |
| Fig. 3 | Main effect plot for SeEvo on four parameters (Taguchi analysis) |
| Fig. 4 | Gap ratio of 14 scheduling methods in DFJSSP scenarios for makespan optimization (100 dynamic test cases) |
| Fig. 5 | Gap ratio of 14 scheduling methods in DFJSSP scenarios for tardiness optimization (100 dynamic test cases) |
| Fig. 6 | Convergence curves (8 subfigures): SeEvo vs. ReEvo vs. GP/GEP on DMU and TA datasets (10 runs, mean ± std) |
| Fig. 7 | EMA feature ablation: Gap ratio distribution (violin plots) — with vs. without ema |
| Fig. 8 | EMA feature ablation: Best solution quality and average makespan comparison |
| Fig. 9 | HDRs generated by DeepSeek-V3 and GPT-4.1-mini on TA72 case |
| Fig. 10 | HDRs generated by GP and GEP on TA72 case |
| Table I | SeEvo parameters (Taguchi design) |
| Table II | Experimental results on DMU benchmark (16 cases, individual comparison) |
| Table III | DMU benchmark results — arithmetic mean makespan per problem size |
| Table IV | Experimental results on TA benchmark (16 cases, individual comparison) |
| Table V | TA benchmark results — arithmetic mean makespan per problem size |
| Table VI | Ablation study: SeEvo vs. ReEvo vs. DRL on TA generalization test (30×20 and 50×20) |

---

## References (Selected Key Citations)

| # | Reference | Relevance |
|---|-----------|-----------|
| [1] | Shady et al. (2023), Int. J. Prod. Res. — GEP for reactive scheduling | GEP baseline |
| [2] | Zhang et al. (2019), J. Cleaner Prod. — mathematical modeling for energy-efficient job shop | GEP reference |
| [4] | Wang et al. (2019), IEEE Trans. Fuzzy Syst. — NSGA-II with local simulated annealing for bi-criteria robust JSSP | Fuzzy scheduling |
| [7] | Gao et al. (2020), IEEE Trans. Fuzzy Syst. — DE with improved selection for fuzzy JSSP | Fuzzy scheduling |
| [9] | Wang et al. (2023), J. Manuf. Syst. — data-driven simulation-optimization for GP-based HDRs in dynamic JSSP | GP baseline |
| [10] | Wu et al. (2024), Eng. Appl. Artif. Intell. — DRL for dynamic JSSP with uncertain processing time | DRL comparison |
| [12] | Li et al. (2022), Rob. Comput. Integr. Manuf. — hybrid DQN for flexible JSSP | GP/DRL |
| [13] | Nie et al. (2013), Comput. Ind. Eng. — reactive scheduling with GEP | GEP baseline |
| [16] | Chen et al. (2023), IEEE Trans. Ind. Inf. — DRL with attention mechanism and disjunctive graph embedding for JSSP | DRL-Chen comparison |
| [17] | Romera-Paredes et al. (2024), Nature — LLMs + evolutionary framework for combinatorial optimization (BPP) | LLM precedent |
| [19] | Ye et al. (2024), NeurIPS — ReEvo: LLMs as hyper-heuristics with reflective evolution | Direct predecessor |
| [24] | Yu et al. (2024), IEEE Trans. Fuzzy Syst. — self-learning discrete ABC for LR fuzzy welding shop scheduling | Fuzzy scheduling |
| [26] | Liu et al. (2024), IEEE Trans. Ind. Inf. — dynamic JSSP via graph attention networks and DRL | DRL-Liu comparison |
| [33] | Shinn et al. (2023), NeurIPS — Reflexion: language agents with verbal reinforcement learning | Self-reflection mechanism |
| [35] | Liu et al. (2023), arXiv:2311.15249 — algorithm evolution using LLM for TSP | LLM algorithm design |
| [37] | Mischler et al. (2024), Nat. Mach. Intell. — contextual feature extraction hierarchies in LLMs and the brain | Theoretical support |
| [39] | Zhang et al. (2020), NeurIPS — learning to dispatch for JSSP via DRL | DRL-Zhang comparison |
