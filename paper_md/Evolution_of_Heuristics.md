# Evolution of Heuristics: Towards Efficient Automatic Algorithm Design Using Large Language Model

**Published:** Proceedings of the 41st International Conference on Machine Learning (ICML 2024), Vienna, Austria. PMLR 235, 2024.

**arXiv:** arXiv:2401.02051v3 [cs.NE] 1 Jun 2024

**Source code:** https://github.com/FeiLiu36/EoH

---

## Authors and Affiliations

| Author | Affiliation |
|---|---|
| Fei Liu | Department of Computer Science, City University of Hong Kong |
| Xialiang Tong | Huawei Noah's Ark Lab |
| Mingxuan Yuan | Huawei Noah's Ark Lab |
| Xi Lin | Department of Computer Science, City University of Hong Kong |
| Fu Luo | School of System Design and Intelligent Manufacturing, Southern University of Science and Technology |
| Zhenkun Wang | School of System Design and Intelligent Manufacturing, Southern University of Science and Technology |
| Zhichao Lu | Department of Computer Science, City University of Hong Kong |
| Qingfu Zhang | Department of Computer Science, City University of Hong Kong |

**Correspondence:** Qingfu Zhang <qingfu.zhang@cityu.edu.hk>, Zhenkun Wang <wangzk3@sustech.edu.cn>

---

## Abstract

Heuristics are widely used for dealing with complex search and optimization problems. However, manual design of heuristics can be often very labour extensive and requires rich working experience and knowledge. This paper proposes **Evolution of Heuristic (EoH)**, a novel evolutionary paradigm that leverages both Large Language Models (LLMs) and Evolutionary Computation (EC) methods for Automatic Heuristic Design (AHD).

EoH represents the ideas of heuristics in natural language, termed **thoughts**. They are then translated into executable codes by LLMs. The evolution of both thoughts and codes in an evolutionary search framework makes it very effective and efficient for generating high-performance heuristics.

Experiments on three widely studied combinatorial optimization benchmark problems demonstrate that EoH outperforms commonly used handcrafted heuristics and other recent AHD methods including FunSearch. Particularly, the heuristic produced by EoH with a low computational budget (in terms of the number of queries to LLMs) significantly outperforms widely-used human hand-crafted baseline algorithms for the online bin packing problem.

---

## 1. Introduction

### Motivation

Heuristics are commonly used for tackling complex search and optimization problems. Over the last several decades, much effort has been devoted to designing effective heuristics, leading to:
- Simulated annealing (Van Laarhoven et al., 1987)
- Tabu search (Glover & Laguna, 1998)
- Iterated local search (Lourenco et al., 2003)

These hand-crafted methods have been successfully used in a wide spectrum of real-world applications. However:
- Different applications may require different algorithms and/or algorithm configurations
- Manually designing, modifying, and configuring a heuristic for a given problem can be very labor-intensive
- This demands rich expert experience and is a bottleneck in many application domains

To address this, **Automatic Heuristic Design (AHD)** has been proposed (Burke et al., 2013; Stutzle & Lopez-Ibanez, 2019). Genetic Programming (GP) has been used in AHD but requires a set of permissible primitives or mutation operations which can be very difficult to construct in practice (O'Neill et al., 2010).

LLMs are believed to be a powerful tool for generating new ideas and heuristics. However, standalone LLMs with prompt engineering can be insufficient for producing novel and useful ideas beyond existing knowledge (Mahowald et al., 2023). One representative prior work is **FunSearch** (Romera-Paredes et al., 2024), which models AHD as a search problem in the space of functions and uses LLMs in an evolutionary framework. However, FunSearch's mechanism is not very efficient and needs a very large amount of computational resources — typically around **1 million LLM queries** to generate a quality heuristic.

### Key Contributions

- **Novel paradigm EoH:** Uses LLMs to evolve both thoughts and codes for the automatic design of heuristics with minimum hand-craft design and no domain model training.
- **Prompt strategies:** Develops several simple yet effective prompt strategies to guide LLMs toward generating more diverse and effective heuristics. These are generally applicable to other LLM-assisted search methods.
- **Comprehensive evaluation:** Evaluates EoH on three widely-studied combinatorial optimization benchmark problems, demonstrating that EoH outperforms many existing AHD methods. In particular, EoH identifies heuristics with better performance than those designed by FunSearch while using much fewer LLM queries.

### Design Philosophy: Three Approaches Compared

```
(a) Manual Design:
    Human Expert --> [Reasoning over Thoughts] --> Heuristics

(b) Evolution of Codes only (FunSearch):
    LLM --> [Search over Code Space] --> Heuristics

(c) Evolution of both Thoughts and Codes (EoH, this paper):
    LLM --> [Thoughts + Codes, augmented by 5 prompt strategies] --> Heuristics
    Prompt Strategies:
      Exploration: E1, E2
      Modification: M1, M2, M3
```

---

## 2. Background and Related Works

### 2.1. Automatic Heuristic Design (AHD)

Automatic heuristic algorithm design is commonly known as **hyper-heuristics** (Burke et al., 2013; 2019; Stutzle & Lopez-Ibanez, 2019). With various effective methodologies and frameworks, one can tune heuristics or combine different algorithmic components in an automatic manner. Machine learning techniques have been applied to automatic algorithm design (Bengio et al., 2021; Chen et al., 2022; He et al., 2021; Li et al., 2023a).

**Genetic Programming (GP)** provides an explainable approach to algorithm design (Mei et al., 2022; Jia et al., 2022) but requires:
- Hand-crafted algorithmic components
- Domain knowledge
- A suitable set of permissible primitives (difficult to construct)

### 2.2. LLMs for Heuristic Design

The ability of large language models has increased significantly over the last few years (Naveed et al., 2023). Approaches include:

- **LLMs as optimizers** (Yang et al., 2023): directly generate new trial solutions through in-context learning. Faces challenges for complex problems with large search space.
- **LLMs for algorithm feature extraction** (Wu et al., 2023): extract deep algorithm features for heuristic selection.
- **LLMs as guides** (Shah et al., 2023): provide a guide for heuristic design.
- **LLMs for algorithmic component design** (Xiao & Wang, 2023)

Designing a competitive heuristic remains a challenge for standalone LLMs with prompt engineering alone.

### 2.3. LLMs + Evolutionary Computation (EC)

Evolutionary computation is a generic optimization principle inspired by natural evolution (Back et al., 1997; Eiben & Smith, 2015). Integration of EC in the prompt engineering of LLMs is very promising (Guo et al., 2023b; Lehman et al., 2023; Wu et al., 2024). Evolutionary methods have been adopted in:
- Code generation (Liventsev et al., 2023; Ma et al., 2023; Lehman et al., 2024; Hemberg et al., 2024)
- Text generation (Guo et al., 2023b; Fernando et al., 2023; Xu et al., 2023a)

**FunSearch** (Romera-Paredes et al., 2024) is the most related prior work:
- Evolutionary framework with LLMs to automatically search functions
- Algorithms outperform hard-crafted algorithms on some optimization problems
- **Limitation:** Computationally expensive; usually needs to generate **millions of programs** (i.e., queries to LLMs) to identify an effective heuristic function

> Note: EoH and its preliminary version (Liu et al., 2023b) were developed independently of Romera-Paredes et al. (2024).

---

## 3. Evolution of Heuristics (EoH)

### 3.1. Main Idea

EoH aims at evolving both thoughts and codes to mimic the heuristic development conducted by human experts for efficient automatic heuristic design.

**Three core principles:**

1. **Dual representation:** EoH maintains both a natural language description and its corresponding code implementation for each heuristic.
   - Natural language description: summarizes the main idea and provides a high-level understanding
   - Code: provides implementation details and settings that supplement the high-level thought
   - In each trial, LLMs first generate a heuristic in natural language, then generate the corresponding code

2. **Prompt strategies:** Several prompt strategies guide LLMs to do reasoning over existing thoughts and codes. These strategies are designed to learn from previous experiences and effectively explore the heuristic space. They can be regarded as fine-grained in-context learning approaches that combine thoughts and codes for heuristic search.

3. **Population evolution:** EoH evolves a population of candidate heuristics using LLMs in genetic operators (crossover and mutation) to produce new heuristics. Selection directs the search. Quality of each heuristic is evaluated on a set of problem instances.

**Key distinctions from prior work:**
- Unlike most evolutionary algorithms, an individual in EoH is a **heuristic** (not a candidate solution to a problem)
- Unlike classic AHD methods, EoH doesn't need any hand-crafted heuristic components or train new models
- Unlike FunSearch, EoH evolves **both thoughts and codes** and uses explicit prompt strategies

### 3.2. Evolution Framework

**Population:** EoH maintains a population of N heuristics:
```
P = {h1, ..., hN}
```

Each heuristic `hi` is evaluated on a set of problem instances and assigned a fitness value `f(hi)`.

**Generation structure:**
- Five prompt strategies are designed to generate new heuristics
- At each generation, each strategy is called N times → up to 5N new heuristics generated
- Each newly generated heuristic is evaluated and added to the current population if feasible
- N best individuals are selected to form the next generation

**Algorithm:**

```
Step 0 - Initialization:
  Initialize population P = {h1, ..., hN} by prompting LLMs with Initialization prompt.
  Repeat N times to generate N initial heuristics.

Step 1 - Generation of Heuristics:
  While stopping condition not met:
    Use 5 evolution prompt strategies simultaneously to generate 5N new heuristics.
    For each of the five prompt strategies, repeat N times:
      Step 1.1: Select parent heuristic(s) from current population.
      Step 1.2: Request LLM to generate a new heuristic + code implementation.
      Step 1.3: Evaluate new heuristic on evaluation instances → fitness value.
      Step 1.4: Add new heuristic to current population if feasible.

Step 2 - Population Management:
  Select N best heuristics from current population → next generation population.
  Go to Step 1.
```

### 3.3. Heuristic Representation

Each heuristic consists of three parts:
1. **Description in natural language** — a few sentences created by LLMs presenting a high-level thought
2. **Code block** — an executable Python implementation in pre-defined format
3. **Fitness value** — performance on the evaluation instance set

**Code block format requirements:**
- Name of the function
- Input variables
- Output variables

**Fitness evaluation:**
- Running the resulting algorithms on an instance set of the problem in question
- Differs from traditional EAs which evaluate on a single instance
- Similar to some AHD approaches (Lopez-Ibanez et al., 2016; Hutter et al., 2011)
- Often costly, but applied consistently across all compared methods

### 3.4. Prompt Strategies

All prompts consist of five components:
1. **Task description** — informs LLMs of the problem description (shared across strategies)
2. **Strategy-specific prompt** — instructs LLMs on the reasoning/generation approach
3. **Expected output** — asks for heuristic description + Python code implementation
4. **Note** — additional instructions for efficiency and robustness (e.g., specific I/O types, discourage extra explanations)
5. **Parent heuristic(s)** — enables in-context learning (absent in Initialization prompt)

#### Initialization Prompt

Used to create all initial heuristics from scratch, eliminating the need for expert knowledge. LLMs are informed of the heuristic design task and instructed to:
1. First present a description of the heuristic
2. Then implement it as a Python code block

**Example (bin packing):**
```
I need help designing a new heuristic that scores a set of bins to assign an item.
In each step, the item will be assigned to the bin with the maximum score.
If the rest capacity of a bin equals the maximum capacity, it will not be used.
The final goal is to minimize the number of used bins.

Please design a new heuristic.
Firstly, describe your new heuristic and main steps in one sentence.
Next, implement it in Python as a function named 'score'.
This function should accept two inputs: 'item' and 'bins'.
The function should return one output: 'scores'.
'item' and 'bins' are the size of the current item and the rest capacities
of feasible bins, which are larger than the item size.
The output named 'scores' is the scores for the bins for assignment.

Note that 'item' is of type int, 'bins' is a Numpy array that includes
integer values, and 'scores' should be a Numpy array.
Avoid utilizing the random component, and it is crucial to maintain
self-consistency. Do not give additional explanations.
```

#### Evolution Prompt Strategies

Five strategies are divided into two groups:

**Exploration Strategies** (crossover-like operators, focus on exploring the heuristic space):

**E1 — Generate maximally different heuristics:**
- Select p heuristics from the current population
- Prompt LLM to design a new heuristic that is **as different as possible** from the selected heuristics
- Goal: explore new ideas beyond existing ones

**E2 — Explore common-idea variants:**
- Select p heuristics from the current population
- LLM first identifies common ideas behind these heuristics
- Then designs a new heuristic based on the common idea but **as different as possible** from the selected parents by introducing new parts
- Goal: exploit shared patterns while introducing novelty

**Modification Strategies** (refine a parent heuristic):

**M1 — Modify for better performance:**
- Select one heuristic from the population
- LLM is prompted to modify it to produce a new, improved heuristic

**M2 — Parameter modification:**
- Select one heuristic from the current population
- LLM is prompted to try **different parameter values** in the current heuristic (rather than designing a new one)

**M3 — Simplify by removing redundancy:**
- Select one heuristic from the current population
- LLM analyzes and identifies main components
- LLM determines whether there are redundant components
- LLM simplifies the code implementation based on its analysis

> In all prompts, LLM is asked to first describe the heuristic and then provide a code implementation in a pre-defined format.

#### Selection Mechanism

Any selection method can be used. In the experimental studies:
- All heuristics in the current population are ranked according to fitness
- Heuristic i is randomly selected with probability:

```
p_i ∝ 1 / (r_i + N)
```

where `r_i` is its rank and `N` is the population size. This gives higher selection probability to better-ranked heuristics while still allowing selection of weaker ones.

---

## 4. Experiments

### 4.1. Experimental Settings

#### Benchmark Problems

**1. Online Bin Packing Problem**
- **Objective:** Allocate items of different sizes into the fewest possible bins with fixed capacity C
- **Scenario:** Online (items packed as they arrive, no lookahead)
- **Training instances:** Five Weibull instances of size 5k with capacity 100
- **Fitness:** Average `lb/n` on five instances, where:
  - `lb` = lower bound of optimal number of bins (Martello & Toth, 1990)
  - `n` = number of bins used by the evaluated heuristic
- **Task for EoH:** Design the **scoring function** for assigning items to bins
  - Input: size of item, rest capacities of bins
  - Output: scores for the bins (item assigned to bin with maximum score)

**2. Traveling Salesman Problem (TSP)**
- **Objective:** Find the shortest route to visit all locations once and return to start
- **Training instances:** 64 TSP100 instances with locations randomly sampled from [0,1]^2
- **Fitness:** Average gap from optimal solution (generated by Concorde solver)
- **Task for EoH:** Design **Guided Local Search (GLS) heuristics** — specifically, a method for updating the distance matrix
  - Inputs: distance matrix, current route, number of edges used
  - Output: updated distance matrix
  - Local search operators: Relocate and 2-opt

**3. Flow Shop Scheduling Problem (FSSP)**
- **Objective:** Schedule n jobs on m machines to minimize makespan (total schedule length)
- **Setup:** Permutation flow-shop (processing order consistent, no machine executes multiple operations simultaneously)
- **Training instances:** 64 randomly generated instances; 50 jobs, 2–20 machines; processing times from Uniform[0,1]
- **Fitness:** Average makespan
- **Task for EoH:** Design a GLS heuristic for updating the objective landscape
  - Inputs: time matrix, current scheduling, number of machines and jobs
  - Outputs: updated time matrix and calculated job perturbation priority
  - Local search operators: Relocate and Swap

#### Implementation Details

| Parameter | Bin Packing | TSP | FSSP |
|---|---|---|---|
| Generations | 20 | 20 | 20 |
| Population size (N) | 20 | 10 | 10 |
| Parent heuristics (E1/E2, p) | 5 | 5 | 5 |
| LLM | GPT-3.5-turbo | GPT-3.5-turbo | GPT-3.5-turbo |
| Max LS iterations | — | 1,000 | 1,000 |
| Max time per instance | — | 60s | 60s |

- Framework and implementations in Python
- Executed on a single CPU i7-9700
- Total LLM queries: approximately **2,000** (20 generations × 5 strategies × 20 population = 2,000 for bin packing)

#### Comparison Methods

**Online Bin Packing baselines:**
- **First Fit (human):** Assigns incoming item to first bin with sufficient space
- **Best Fit (human):** Selects bin with least available space that can still accommodate the item
- **FunSearch (automatic):** Best heuristic from Romera-Paredes et al. (2024), using ~1 million LLM queries

**TSP baselines:**
- **NI — Nearest Insertion (human):** Classic constructive heuristic
- **FI — Farthest Insertion (human):** Classic constructive heuristic
- **Or-Tools (human):** Popular solver with local search, 60s per instance
- **AM (automatic):** Attention Model (Kool et al., 2018) — seminal neural network heuristic
- **POMO (automatic):** Policy Optimization with Multiple Optima (Kwon et al., 2020)
- **LEHD (automatic):** Heavy decoder variant of AM, trained with supervised learning (Luo et al., 2023)

**FSSP baselines:**
- **GUPTA (human):** Classic method (Gupta, 1971)
- **CDS (human):** Classic method (Campbell et al., 1970)
- **NEH (human):** Widely recognized efficient heuristic (Nawaz et al., 1983)
- **NEHFF (human):** Revision of NEH (Fernandez-Viagas & Framinan, 2014)
- **PFSPNet and PFSPNet NEH (automatic):** End-to-end deep learning solvers (Pan et al., 2021)

### 4.2. Results

#### Online Bin Packing

The fitness value (objective) improves from **0.962 to 0.993** in 20 generations (2,000 LLM queries).

**Evolution trace of best heuristic (key milestones):**

| Generation | Fitness | Strategy | Key idea |
|---|---|---|---|
| Init | 0.9621 | Initialization | Baseline |
| ~2 | 0.9620 | M1 | Penalty for large bins: `(bins - item) < 0.2*bins.max()` |
| ~4 | 0.9689 | E1 | Deviation from average: `abs(bins - np.mean(bins))` |
| ~6 | 0.9825 | E2 | Utilization of cubic root: `cbrt(item) / (bins - item)` |
| ~8 | 0.9927 | E2 | Combination of utilization and penalty |
| ~10 | 0.9928 | E1 | Exponent term: `exp(-(bins - item)**2)` |
| ~12 | 0.9929 | M2 | Hybrid adjustment |
| ~14 | 0.9932 | M3 | New parameter settings |
| 20 (final) | 0.9932 | E1 | Hybrid term: `1 - (bins - item) / bins * sqrt(bins - item + 1)` |

**Table 1: Online bin packing results — gap to lower bound (lower is better)**

| Method | 1k C100 | 5k C100 | 10k C100 | 1k C500 | 5k C500 | 10k C500 |
|---|---|---|---|---|---|---|
| First Fit | 5.32% | 4.40% | 4.44% | 4.97% | 4.27% | 4.28% |
| Best Fit | 4.87% | 4.08% | 4.09% | 4.50% | 3.91% | 3.95% |
| FunSearch | 3.78% | 0.80% | 0.33% | 6.75% | 1.47% | 0.74% |
| **EoH (ours)** | **2.24%** | **0.80%** | 0.61% | **2.13%** | **0.78%** | **0.61%** |

Key observations:
- EoH is best on all test sets except 10k C100 (tied/near-tied with FunSearch at 0.61% vs 0.33%)
- FunSearch performs **worse than hand-crafted heuristics** on 1k C500 (6.75%), whereas EoH achieves 2.13%
- EoH uses only ~2,000 LLM queries vs. ~1,000,000 for FunSearch (500x fewer)
- Excellent generalization to out-of-distribution instances (different sizes and capacities)

**Extended results (Table 9) — average gap across all capacities: EoH 1.18% vs FunSearch 2.23%**

#### Traveling Salesman Problem

EoH converges after about **20 generations**. Population size is 10.

**Table 2: TSP results on TSPLib instances — relative distance (%) to best-known solutions (lower is better)**

| Method | rd100 | pr124 | bier127 | kroA150 | u159 | kroB200 |
|---|---|---|---|---|---|---|
| NI | 19.91 | 15.50 | 23.21 | 18.17 | 23.59 | 24.10 |
| FI | 9.38 | 4.43 | 8.04 | 8.54 | 11.15 | 7.54 |
| Or-Tools | 0.01 | 0.55 | 0.66 | 0.02 | 1.75 | 2.57 |
| AM | 3.41 | 3.68 | 5.91 | 3.78 | 7.55 | 7.11 |
| POMO | 0.01 | 0.60 | 13.72 | 0.70 | 0.95 | 1.58 |
| LEHD | 0.01 | 1.11 | 4.76 | 1.40 | 1.13 | 0.64 |
| **EoH (ours)** | **0.01** | **0.00** | **0.42** | **0.00** | **0.00** | **0.20** |

Key observations:
- EoH consistently outperforms all other heuristics on all test instances
- For pr124, kroA150, and u159: EoH finds the **best-known solutions** (gap = 0%)
- Neural solvers (AM, POMO, LEHD) trained on uniform distributions deteriorate on TSPLib (out-of-distribution); EoH generalizes well
- Or-Tools performance degrades on larger instances with limited time; EoH remains competitive

**Table 10: Results on TSP20, TSP50, TSP100 (average gap and time over 1,000 instances)**

| Method | TSP20 Gap | TSP20 Time | TSP50 Gap | TSP50 Time | TSP100 Gap | TSP100 Time |
|---|---|---|---|---|---|---|
| Concorde | 0.000% | 0.010s | 0.000% | 0.051s | 0.000% | 0.224s |
| LKH3 | 0.000% | 0.020s | 0.000% | 0.069s | 0.011% | 0.118s |
| NN | 17.448% | 0.000s | 23.230% | 0.002s | 25.104% | 0.010s |
| FI | 2.242% | 0.005s | 7.263% | 0.065s | 12.456% | 0.444s |
| AM | 0.069% | 0.038s | 0.494% | 0.124s | 2.368% | 0.356s |
| GCN | 0.035% | 0.974s | 0.884% | 3.080s | 1.880% | 6.127s |
| POMO | 0.120% | — | 0.640% | — | 1.070% | — |
| POMO aug8 | 0.000% | — | 0.030% | — | 0.140% | — |
| BQ | 0.379% | — | 0.245% | — | 0.579% | — |
| LEHD | 0.950% | — | 0.485% | — | 0.577% | — |
| LS | 1.814% | 0.006s | 3.461% | 0.006s | 4.004% | 0.008s |
| GLS | 0.004% | 0.088s | 0.045% | 0.248s | 0.659% | 0.683s |
| EBGLS | 0.002% | 0.091s | 0.003% | 0.276s | 0.155% | 0.779s |
| KGLS | 0.000% | 1.112s | 0.000% | 3.215s | 0.035% | 7.468s |
| GNNGLS | 0.000% | 10.010s | 0.009% | 10.037s | 0.698% | 10.108s |
| NeuralGLS | 0.000% | 10.005s | 0.003% | 10.011s | 0.470% | 10.024s |
| **EoH** | **0.000%** | **0.498s** | **0.000%** | **1.494s** | **0.025%** | **4.510s** |

Note: POMO, BQ, LEHD run in parallel on GPU; single-instance running time not provided.

**Table 11: Results on 29 TSPLib instances (selected rows) — average gap 0.28% for EoH**

| Instance | AM | POMO | LEHD | GNNGLS | NeuralGLS | LS | GLS | EBGLS | KGLS | EoH |
|---|---|---|---|---|---|---|---|---|---|---|
| eil51 | 1.63 | 0.83 | 1.64 | 0.00 | 0.00 | 2.85 | 0.67 | 0.67 | 0.67 | 0.67 |
| berlin52 | 4.17 | 0.04 | 0.03 | 0.14 | 0.00 | 3.89 | 0.03 | 0.03 | 0.03 | 0.03 |
| pr76 | 0.82 | 0.00 | 0.22 | 0.04 | 0.82 | 6.71 | 0.00 | 0.00 | 0.00 | 0.00 |
| kroA100 | 4.02 | 0.41 | 0.12 | 0.73 | 0.03 | 3.00 | 0.02 | 0.02 | 0.06 | 0.02 |
| rd100 | 3.41 | 0.01 | 0.01 | 0.46 | 0.00 | 1.27 | 0.01 | 0.01 | 0.02 | 0.01 |
| pr124 | 3.68 | 0.60 | 1.11 | 0.76 | 0.08 | 2.44 | 0.60 | 0.60 | 0.08 | 0.00 |
| bier127 | 5.91 | 13.72 | 4.76 | 1.95 | 2.73 | 1.79 | 0.59 | 0.29 | 0.42 | 0.42 |
| kroA150 | 3.78 | 0.70 | 1.40 | 2.98 | 0.77 | 5.05 | 1.75 | 0.26 | 0.17 | 0.00 |
| u159 | 7.55 | 0.95 | 1.13 | 1.02 | 0.90 | 5.63 | 0.74 | 0.78 | 0.96 | 0.00 |
| kroB200 | 8.54 | 1.44 | 0.16 | 2.59 | 3.74 | 4.71 | 1.43 | 1.27 | 0.89 | 0.20 |
| d198 | 373.02 | 17.29 | 9.23 | 4.77 | 1.28 | 7.96 | 2.08 | 1.87 | 0.31 | 0.59 |
| **Average** | **16.77** | **2.02** | **1.92** | **1.53** | **0.96** | **4.01** | **0.78** | **0.42** | **0.36** | **0.28** |

EoH achieves the **best average gap of 0.28%** across all 29 TSPLib instances.

#### Flow Shop Scheduling Problem

EoH converges in about **20 generations**.

**Table 3: FSSP results on Taillard instances — average relative makespan (%) to baseline (lower is better)**

| Method | n20m10 | n20m20 | n50m10 | n50m20 | n100m10 | n100m20 |
|---|---|---|---|---|---|---|
| GUPTA | 23.42 | 21.79 | 20.11 | 22.78 | 15.03 | 21.00 |
| CDS | 12.87 | 10.35 | 12.72 | 15.03 | 9.36 | 13.55 |
| NEH | 4.05 | 3.06 | 3.47 | 5.48 | 2.07 | 3.58 |
| NEHFF | 4.15 | 2.72 | 3.62 | 5.10 | 1.88 | 3.73 |
| PFSPNet | 14.78 | 14.69 | 11.95 | 16.95 | 8.21 | 16.47 |
| PFSPNet NEH | 4.04 | 2.96 | 3.48 | 5.05 | 1.72 | 3.56 |
| **EoH (ours)** | **0.30** | **0.10** | **0.19** | **0.60** | **0.14** | **0.41** |

**Table 12: Extended FSSP results on all Taillard instance sets**

| Test Set | GUPTA | CDS | NEH | NEHFF | PFSPNet | LS | ILS1 | ILS2 | EoH |
|---|---|---|---|---|---|---|---|---|---|
| 20×5 | 12.89 | 9.03 | 3.24 | 2.30 | 2.30 | 1.91 | 0.42 | 0.18 | **0.09** |
| 20×10 | 23.42 | 12.87 | 4.05 | 4.15 | 4.04 | 2.77 | 0.33 | 0.25 | **0.30** |
| 20×20 | 21.79 | 10.35 | 3.06 | 2.72 | 2.96 | 2.60 | 0.29 | 0.25 | **0.10** |
| 50×5 | 12.23 | 6.98 | 0.57 | 0.40 | 0.51 | 0.32 | 0.15 | 0.32 | **0.02** |
| 50×10 | 20.11 | 12.72 | 3.47 | 3.62 | 3.48 | 3.33 | 1.47 | 0.29 | **0.19** |
| 50×20 | 22.78 | 15.03 | 5.48 | 5.10 | 5.05 | 4.67 | 2.13 | 0.34 | **0.60** |
| 100×5 | 5.98 | 5.10 | 0.39 | 0.31 | 0.31 | 0.28 | 0.20 | 0.38 | **-0.04** |
| 100×10 | 15.03 | 9.36 | 2.07 | 1.88 | 1.72 | 1.38 | 0.77 | 0.34 | **0.14** |
| 100×20 | 21.00 | 13.55 | 3.58 | 3.73 | 3.56 | 3.51 | 2.27 | 0.43 | **0.41** |
| 200×10 | 11.59 | 7.22 | 0.98 | 0.70 | 0.82 | 0.87 | 0.74 | 0.54 | **0.12** |
| 200×20 | 18.09 | 11.89 | 2.90 | 2.52 | 2.49 | 2.53 | 2.26 | 0.59 | **0.61** |
| **Average** | **16.81** | **10.37** | **2.71** | **2.49** | **2.48** | **2.20** | **1.00** | **0.36** | **0.23** |

EoH achieves the **best average gap of 0.23%** across all test sets. Notably, EoH outperforms ILS2 which uses the same framework and local search operators but with a human hand-crafted perturbation strategy — demonstrating EoH's ability to design better-than-human strategies.

---

## 5. Comparison with FunSearch

### Computational Efficiency

| Method | LLM Queries | Performance (5k C100) |
|---|---|---|
| FunSearch | ~1,000,000 | 0.80% gap |
| EoH | ~2,000 | 0.80% gap |

EoH achieves the **same performance with ~500x fewer LLM queries** on the training distribution (5k C100).

### Generalization

| Method | 1k C500 (out-of-distribution) |
|---|---|
| First Fit | 4.97% |
| Best Fit | 4.50% |
| FunSearch | 6.75% (worse than hand-crafted!) |
| EoH | 2.13% |

FunSearch's heuristic fails to generalize to different capacities, while EoH's heuristic generalizes strongly.

### Final Heuristic Code Comparison

**Human (First Fit):**
```python
import numpy as np
def heuristic(item, bins):
    scores = -np.arange(len(bins))
    return scores
```

**Human (Best Fit):**
```python
def heuristic(item, bins):
    scores = item - bins
    return scores
```

**FunSearch:**
```python
def heuristic(item, bins):
    max_bin = max(bins)
    comb1 = (bins - max_bin)**2 / item
    comb2 = bins**2 / item**2
    comb3 = bins**2 / item**3
    scores = comb1 + comb2 + comb3
    scores[bins > item] = -score[bins > item]
    scores[1:] -= score[:-1]
    return scores
```

**EoH:**
```python
import numpy as np
def heuristic(item, bins):
    diff = bins - item           # remaining capacity
    exp = np.exp(diff)           # exponent term
    sqrt = np.sqrt(diff)         # square root term
    ulti = 1 - diff/bins         # utilization term
    comb = ulti * sqrt           # combination of utilization and square root
    adjust = np.where(diff > (item * 3), comb + 0.8, comb + 0.3)
    # hybrid adjustment term to penalize large bins
    hybrid_exp = bins / ((exp + 0.7) * exp)
    # hybrid score based on exponent term
    scores = hybrid_exp + adjust
    # sum of hybrid score and adjustment
    return scores
```

*The heuristic incorporates a weighted average of the utilization ratio, dynamic adjustment, and an exponentially decaying factor, with different parameter settings to minimize the number of used bins.*

Human-designed heuristics can be implemented in one line. FunSearch and EoH produce more sophisticated heuristics that would be difficult to achieve for human designers.

---

## 6. Ablation Studies

### 6.1. Component Ablation (Prompt Strategies and Thoughts)

**Table 4: Variants studied in ablation**

| Variant | Thoughts | Codes | Prompt Strategies Used |
|---|---|---|---|
| EoC | No | Yes | E1 only |
| EoH-e1 | Yes | Yes | E1 only |
| EoH-e2 | Yes | Yes | E1, E2 |
| EoH | Yes | Yes | E1, E2, M1, M2, M3 |

Settings: population size 20, GPT-3.5-turbo, p=5 parent heuristics in E1/E2. Same initial population for fairness. Total number of evaluated heuristics kept equal by adjusting generations.

**Table 5: Ablation results — gap to lower bound on Weibull instances**

| Variant | 1k×100 | 5k×100 | 10k×100 | 1k×500 | 5k×500 | 10k×500 |
|---|---|---|---|---|---|---|
| EoC | 148.63% | 3.23% | 24.55% | 150.89% | 12.53% | 32.02% |
| EoH-e1 | 4.13% | 0.99% | 0.60% | 58.17% | 55.48% | 54.79% |
| EoH-e2 | 4.28% | 0.97% | 0.56% | 5.86% | 1.36% | 0.73% |
| **EoH** | **2.24%** | **0.80%** | **0.61%** | **2.13%** | **0.78%** | **0.61%** |

**Observations:**
- EoH performs best overall; EoH-e2 is second best → M1, M2, M3 and E2 make positive contributions
- EoC (code-only, no thoughts) performs worst or second worst → thoughts are very beneficial
- EoH-e1 overfits to the training capacity (C=100) but fails to generalize to C=500 instances (58.17%, 55.48%, 54.79%) → E2 is critical for generalization
- EoC dramatically overfits (148.63% on 1k×100, 150.89% on 1k×500)

### 6.2. Interaction Between Thoughts and Codes

Four representation variants compared on bin packing (5k Weibull instances), run 3 times each:

| Variant | Description |
|---|---|
| C2C | Code only for representation; no natural language thoughts |
| T2T2C | Thought only in evolutionary prompts; separate LLM call to produce code for evaluation |
| T&C2T2C | Both thought and code as input to prompts; prompts output thought only; separate LLM call for code |
| EoH | Both thought and code as input; prompts output both thought and code |

**Table 6: Effect of thought/code co-evolution — average gap (%) to lb on 5k Weibull**

| Setting | Run 1 | Run 2 | Run 3 | Average |
|---|---|---|---|---|
| C2C | 2.92 | 1.25 | 3.53 | 2.57 |
| T2T2C | 3.72 | 1.66 | 1.00 | 2.13 |
| T&C2T2C | 0.79 | 0.76 | 1.00 | 0.85 |
| **EoH** | **0.68** | **0.67** | **0.62** | **0.66** |

**Observations:**
- Using only codes (C2C) or only thoughts (T2T2C) in evolutionary prompts is much worse than EoH
- Evolution of **both codes and thoughts** makes a significant contribution
- EoH also outperforms T&C2T2C → having prompts output both codes and thoughts (not just thoughts) is also helpful

### 6.3. Different LLMs

**Table 7: EoH performance with different LLMs — average gap (%) on 5k Weibull**

| Method | LLM | Run 1 | Run 2 | Run 3 | Average |
|---|---|---|---|---|---|
| Sampling (random) | GPT-3.5 | 2.76 | 1.92 | 2.65 | 2.44 |
| EoH | CodeLlama | 0.93 | 0.62 | 1.66 | 1.07 |
| EoH | Deepseek | 1.01 | 1.47 | 1.75 | 1.41 |
| EoH | Gemini Pro | 0.92 | 0.61 | 0.61 | 0.71 |
| **EoH** | **GPT-3.5** | **0.68** | **0.67** | **0.62** | **0.66** |

**Observations:**
- EoH can generate good-performance heuristics with all tested LLMs
- EoH with **2,000 queries** using any LLM outperforms randomly querying GPT-3.5 **10,000 times** → the evolutionary framework itself is the key
- More powerful LLMs (GPT-3.5, Gemini Pro) outperform less powerful ones (CodeLlama, Deepseek) within EoH

### 6.4. Use of Expert Heuristic (EoH expert)

Experiment: Place the FunSearch heuristic as an "expert" into EoH's initial population, with the rest randomly generated.

**Table 8: Effect of using an existing expert heuristic — average gap (%) on 5k Weibull**

| Method | Run 1 | Run 2 | Run 3 | Average |
|---|---|---|---|---|
| FunSearch | 0.94 | 0.82 | 1.15 | 0.97 |
| EoH | 0.68 | 0.67 | 0.62 | 0.66 |
| **EoH expert** | **0.57** | **0.55** | **0.52** | **0.55** |

**Observation:** The adoption of an elite expert heuristic benefits the final results. The knowledge of expert heuristics can be inherited and evolved during evolution to produce better heuristics.

---

## 7. Designed Heuristics (Examples)

### TSP GLS Heuristic (EoH)

```python
import numpy as np
def heuristic(edge_distance, local_opt_tour, edge_n_used):
    updated_edge_distance = np.copy(edge_distance)
    edge_count = np.zeros_like(edge_distance)
    for i in range(len(local_opt_tour) - 1):
        start = local_opt_tour[i]
        end = local_opt_tour[i + 1]
        edge_count[start][end] += 1
        edge_count[end][start] += 1
    # penalize local optimal route
    edge_n_used_max = np.max(edge_n_used)
    # calculate the average edge used
    decay_factor = 0.1  # decay factor
    mean_distance = np.mean(edge_distance)
    # calculate the average distance
    for i in range(edge_distance.shape[0]):
        for j in range(edge_distance.shape[1]):
            if edge_count[i][j] > 0:
                noise_factor = (np.random.uniform(0.7, 1.3) / edge_count[i][j]) + (
                    edge_distance[i][j] / mean_distance) - (0.3 / edge_n_used_max) * \
                    edge_n_used[i][j]
                # calculate a hybrid noise factor
                updated_edge_distance[i][j] += noise_factor * (1 + edge_count[i][j]) - \
                    decay_factor * updated_edge_distance[i][j]
                # new guiding edge distance matrix based on noise term + decayed original
    return updated_edge_distance
```

*Description: Update edge distances by incorporating a pheromone-like effect, where the update is determined by edge count, distance, and usage, with a decay factor to avoid stagnation and promote exploration.*

### FSSP GLS Heuristic (EoH)

```python
import numpy as np
def heuristic(current_sequence, time_matrix, m, n):
    machine_subset = np.random.choice(m, max(1, int(0.3*m)), replace=False)
    # randomly select a subset of machines
    weighted_avg_execution_time = np.average(
        time_matrix[:, machine_subset], axis=1,
        weights=np.random.rand(len(machine_subset)))
    # compute the weighted average execution time
    perturb_jobs = np.argsort(weighted_avg_execution_time)[-int(0.3*n):]
    # sort the last jobs based on weighted average execution time
    new_matrix = time_matrix.copy()
    perturbation_factors = np.random.uniform(0.8, 1.2,
        size=(len(perturb_jobs), len(machine_subset)))
    # calculate perturbation factors, introduce randomness
    new_matrix[perturb_jobs[:, np.newaxis], machine_subset] *= perturbation_factors
    # calculate the final guiding matrix
    return new_matrix, perturb_jobs
```

*Description: Randomly selects a subset of machines, computes the weighted average execution time for each job on the selected machines, and perturbs the top jobs in the current sequence to update the execution time matrix by scaling the original execution time with a random perturbation factor between 0.8 and 1.2.*

---

## 8. Discussion and Future Works

### 8.1. Discussion

#### Key Findings

1. **Thought-code co-evolution is essential.** Using only codes or only thoughts in evolutionary prompts is significantly worse than evolving both together. The combination enables richer in-context learning.

2. **All prompt strategies contribute.** Both exploration (E1, E2) and modification (M1, M2, M3) strategies play a positive role. E2 is particularly critical for generalization.

3. **EoH is LLM-agnostic.** Works well with GPT-3.5, Gemini Pro, CodeLlama, and Deepseek. The evolutionary framework adds value beyond what any single LLM can do with random sampling.

4. **Expert heuristics can bootstrap evolution.** Seeding the initial population with known good heuristics leads to better final results.

5. **Extreme computational efficiency.** EoH achieves competitive or superior performance to FunSearch with ~500x fewer LLM queries.

#### Connection to Chain-of-Thought Prompting

The prompt strategies in EoH can be regarded as **variants of Chain-of-Thought (CoT)** for heuristic design. Parent heuristics and instructions serve as in-context information, similar to how CoT uses step-by-step reasoning to enhance LLM reasoning ability.

### 8.2. Future Works

**1. Pre-trained domain LLM**
Instead of using a general pre-trained LLM with linguistic and code generation capability, it is worthwhile studying how to train an LLM specifically for automatic algorithm design, incorporating domain knowledge.

**2. Understanding the search space of heuristics**
EoH directly searches on the space of heuristics — different from classic optimization algorithms which search in well-defined mathematical spaces such as R^n. Studying and understanding the search space of heuristics is important for establishing theory and basic principles for automatic algorithm design.

**3. Interaction with human experts**
A LLM in EoH can be regarded as an intelligent agent. It should be interesting to study how to implement efficient and effective interaction with human experts in EoH, where human experts can replace LLM for generating, modifying, and evaluating heuristics at specific stages. Ideas and techniques in collective intelligence (Malone & Bernstein, 2022) are relevant.

---

## 9. Conclusion

This paper proposes **Evolution of Heuristics (EoH)**, which combines large language models (LLMs) and evolutionary computation (EC) methods to design heuristics in an automatic manner.

**Core mechanism:**
- Evolution of both thoughts (natural language descriptions) and codes (executable implementations)
- Five prompt strategies: E1, E2 (exploration) + M1, M2, M3 (modification)
- Mimics the process of heuristic design by human experts

**Tested on three problems:**
- Online bin packing problem
- Traveling Salesman Problem
- Flow Shop Scheduling Problem

**Key results:**
- Outperforms human hand-crafted heuristics on all benchmark problems
- Outperforms FunSearch on most test sets while using only ~2,000 LLM queries vs. ~1,000,000 for FunSearch
- Strong generalization to out-of-distribution instances
- Works across multiple LLMs (GPT-3.5, Gemini Pro, CodeLlama, Deepseek)

EoH offers a principled approach to automatic algorithm design and serves as a step towards efficient and automatic algorithm design.

---

## 10. Key Figures and Tables Summary

### Figure Descriptions

**Figure 1** — Three-way comparison of heuristic design approaches:
- (a) Manual design: human expertise over thoughts
- (b) FunSearch: search over code space only
- (c) EoH: evolution of both thoughts and codes using LLMs with 5 prompt strategies (E1, E2, M1, M2, M3)

**Figure 2** — Evolution process for online bin packing over 20 generations:
- Tracks the best heuristic's fitness from 0.962 to 0.993
- Shows the code snippet and thought for key generational improvements
- Labels which prompt strategy produced each improvement
- Compares final EoH heuristic with Best Fit (human) and FunSearch

**Figure 3** — Convergence curves for TSP and FSSP:
- (a) TSP: y-axis = average gap (%) to optimal; x-axis = number of generations; convergence ~20 generations
- (b) FSSP: y-axis = average makespan; convergence ~20 generations
- Both show mean (orange) and best (red) population performance per generation

**Figure 4** — Two prompt examples for bin packing (Initialization and E2):
- Shows all 5 components: task description, strategy-specific prompt, expected output, note, parent heuristics
- E2 prompt includes 5 parent heuristics with descriptions and code; instructs LLM to identify common idea and generate new variant

**Figure 5** — Illustration of E2 generation in one EoH step:
- Shows 5 parent heuristics (with fitness values) fed into E2 prompt
- LLM performs reasoning (identifies common idea), then generates new heuristic description and code
- New heuristic fitness shown

**Figure 6** — Side-by-side comparison of heuristics from First Fit, Best Fit (human), EoC, FunSearch, and EoH for bin packing:
- Shows Python implementations of all approaches
- Hand-crafted heuristics: 1-2 lines; EoC/FunSearch/EoH: significantly more complex

**Figure 7** — Prompt examples for TSP (Initialization and E2):
- Function name: `update_edge_distance`
- Inputs: `edge_distance`, `local_opt_tour`, `edge_n_used`
- Output: `updated_edge_distance`

**Figure 8** — TSP GLS heuristic designed by EoH with full code

**Figure 9** — Prompt examples for FSSP (Initialization and E2):
- Function name: `get_matrix_and_jobs`
- Inputs: `current_sequence`, `time_matrix`, `m`, `n`
- Outputs: `new_matrix`, `perturb_jobs`

**Figure 10** — FSSP GLS heuristic designed by EoH with full code

---

## Appendix Notes

### A. Additional Related Work

**Neural Solvers:** End-to-end neural solvers for combinatorial optimization have been extensively studied. A pointer network was proposed in Vinyals et al. (2015), improved with RL by Bello et al. (2016), and further enhanced with attention models (Kool et al., 2018). POMO (Kwon et al., 2020) achieves state-of-the-art for small/moderate sizes. Recent work uses heavy encoders/light decoders (Drakulic et al., 2023; Luo et al., 2023). Hybridization with classic heuristics includes heat map methods, MCTS, dynamic programming, and GLS variants.

**Prompt Engineering:** Chain-of-Thought (CoT) prompting (Wei et al., 2022) enables in-context learning with step-by-step reasoning. Extensions include tree-of-thoughts, graph-of-thoughts, algorithm-of-thoughts, and automatic CoT construction. EoH's prompt strategies are variants of CoT for heuristic design.

### B. Online Bin Packing Problem — Prompt Details

The E2 prompt for bin packing instructs the LLM to:
1. Identify the common idea in 5 provided heuristics
2. Design a new heuristic based on the common idea but different from the parents
3. Implement as `def score(item, bins)` returning `scores` (Numpy array)

Example parent heuristics use combinations of: logarithms of remaining capacity, sqrt of bin indices, penalties, and weighted factors.

### C. TSP — GLS Framework Details

GLS (Guided Local Search) alternates two phases:
1. **Local search phase:** Apply operators (Relocate and 2-opt) to improve solution
2. **Perturbation phase:** When trapped in local optimum, update the objective function (distance matrix) using EoH's heuristic strategy

EoH designs only the perturbation/update strategy; the local search operators are fixed.

### D. FSSP — GLS Framework Details

Same GLS structure with Swap and Relocate operators. EoH designs:
1. How to update the time matrix
2. Which jobs to perturb (perturbation priority)

---

## Acknowledgements

Supported by:
- Research Grants Council of the Hong Kong Special Administrative Region, China (GRF Project No. CityU11215622)
- National Natural Science Foundation of China (Grant No. 62106096)
- Natural Science Foundation of Guangdong Province (Grant No. 2024A1515011759)
- National Natural Science Foundation of Shenzhen (Grant No. JCYJ20220530113013031)

---

## Selected References

- **Burke et al. (2013):** Hyper-heuristics survey — foundational AHD reference
- **Romera-Paredes et al. (2024):** FunSearch — main comparison method (Nature, 625(7995):468–475)
- **Yang et al. (2023):** Large language models as optimizers (OPRO)
- **Kool et al. (2018):** Attention model for routing problems
- **Kwon et al. (2020):** POMO — state-of-the-art neural solver
- **Nawaz et al. (1983):** NEH heuristic for flow-shop scheduling
- **Voudouris & Tsang (1999):** Guided local search and application to TSP
- **Taillard (1993):** Benchmark instances for flow-shop scheduling
- **Reinelt (1991):** TSPLib benchmark library
- **Liu et al. (2023b):** Algorithm evolution using large language model (preliminary version of EoH)
