# AlphaEvolve: A Coding Agent for Scientific and Algorithmic Discovery

**White Paper — Google DeepMind, 2025**

---

## Authors and Affiliation

**Authors (equal contributions marked with \*):**
Alexander Novikov\*, Ngân Vũ\*, Marvin Eisenberger\*, Emilien Dupont\*, Po-Sen Huang\*, Adam Zsolt Wagner\*, Sergey Shirobokov\*, Borislav Kozlovskii\*, Francisco J. R. Ruiz, Abbas Mehrabian, M. Pawan Kumar, Abigail See, Swarat Chaudhuri, George Holland, Alex Davies, Sebastian Nowozin, Pushmeet Kohli, and Matej Balog\*

**Affiliation:** Google DeepMind

**Corresponding authors:** Matej Balog, Alexander Novikov, and Pushmeet Kohli

**Results repository:** https://colab.research.google.com/github/google-deepmind/alphaevolve_results/blob/master/mathematical_results.ipynb

---

## Abstract / Summary

AlphaEvolve is an evolutionary coding agent that substantially enhances the capabilities of state-of-the-art LLMs on highly challenging tasks such as tackling open scientific problems or optimizing critical pieces of computational infrastructure. AlphaEvolve orchestrates an autonomous pipeline of LLMs whose task is to improve an algorithm by making direct changes to code. Using an evolutionary approach, continuously receiving feedback from one or more evaluators, AlphaEvolve iteratively improves the algorithm, potentially leading to new scientific and practical discoveries.

Key results include:

- **Matrix multiplication:** Developed a search algorithm that found a procedure to multiply two 4×4 complex-valued matrices using **48 scalar multiplications** — the first improvement after 56 years over Strassen's algorithm in this setting. Improved the state of the art for **14 matrix multiplication algorithms** overall.
- **Mathematics:** Applied to over 50 open mathematical problems, matching best known constructions in ~75% of cases and **surpassing the state of the art in ~20%** of cases, including improvements on the Minimum Overlap Problem (Erdős) and the Kissing Numbers problem in 11 dimensions.
- **Google infrastructure:** Recovered **0.7% of fleet-wide compute resources** via improved data center scheduling heuristics (deployed to production); achieved **23% kernel speedup** and **1% reduction in Gemini LLM training time**; optimized TPU arithmetic circuits; achieved **32% speedup of FlashAttention kernel** and **15% speedup in pre/post-processing**.

---

## 1. Introduction

### Motivation

Discovering new high-value knowledge — making a novel scientific discovery or developing a commercially valuable algorithm — generally requires a prolonged process of ideation, exploration, backtracking on unpromising hypotheses, experimentation, and validation.

There has been much recent interest in using large language models (LLMs) to automate significant parts of this process. Key drivers include:
- The power of recent LLMs, which can enhance their capabilities using test-time compute.
- The rise of agents that combine language generation and action.
- Improved performance across established benchmarks and discovery-oriented tasks like hypothesis generation and experiment design.

However, getting LLM pipelines all the way to making entirely new scientific or practical discoveries remains challenging.

### AlphaEvolve's Approach

AlphaEvolve is an **LLM code superoptimization agent** that combines evolutionary computation and LLM-based code generation. It focuses on the broad spectrum of scientific and engineering discovery problems in which candidates can be automatically evaluated.

Key characteristics:
- **Represents candidates as algorithms**: mathematical objects or practical heuristics are represented as code.
- **Uses LLMs to generate, critique, and evolve** a pool of algorithms.
- **Grounded by code execution and automatic evaluation**: avoids incorrect LLM suggestions (hallucinations).
- Leverages modern LLMs' ability to respond to feedback.
- Applicable to problems where discovering new algorithms is the intrinsic goal, **and** to problems where an algorithm serves as a means to construct or find a solution.

### Key Contributions

1. A general-purpose evolutionary coding agent applicable to a wide range of scientific and engineering domains.
2. State-of-the-art results on matrix multiplication tensor decomposition (14 improvements, including the historic 4×4 rank-48 result).
3. New constructions for ~20% of 50+ open mathematical problems across analysis, combinatorics, number theory, and geometry.
4. Deployed optimizations across Google's compute stack (data center scheduling, LLM kernel engineering, TPU circuit design, FlashAttention compiler optimization).
5. A substantial enhancement of FunSearch [Romera-Paredes et al., 2023] in scale and generality.

---

## 2. Method / Architecture

### 2.0 High-Level Overview

AlphaEvolve is a coding agent that orchestrates an autonomous pipeline of computations including queries to LLMs, and produces algorithms that address a user-specified task. The orchestrating procedure is an **evolutionary algorithm** that gradually develops programs that improve the score on automated evaluation metrics.

**The human defines "What?" (evaluation criteria, initial solution, optional background knowledge). AlphaEvolve figures out "How?" (improved solution).**

The core distributed controller loop is:

```python
parent_program, inspirations = database.sample()
prompt = prompt_sampler.build(parent_program, inspirations)
diff = llm.generate(prompt)
child_program = apply_diff(parent_program, diff)
results = evaluator.execute(child_program)
database.add(child_program, results)
```

The system consists of four main components: **Prompt Sampler**, **LLMs Ensemble**, **Evaluators Pool**, and **Program Database**.

---

### 2.1 Task Specification

#### Evaluation Function

Since AlphaEvolve tackles problems with machine-gradeable solutions, the user must provide a mechanism for automatically assessing generated solutions. This takes the form of a function **h** mapping a solution to a set of scalar evaluation metrics. By convention, these metrics are **maximized**.

In the current setup, `h` is typically implemented as a Python function called `evaluate`, with a fixed input/output signature, returning a dictionary of scalars:

```python
def evaluate(eval_inputs) -> dict[str, float]:
    ...
    return metrics
```

Executing this function may take only seconds on a single device, or spawn extensive computations (training a machine learning model, running a search algorithm from many random initializations, etc.).

#### API: Marking Code for Evolution

AlphaEvolve exposes an input API where blocks of code are annotated as to-be-evolved using special markers:

```python
# EVOLVE-BLOCK-START
def some_function():
    # This code will be evolved by AlphaEvolve
    ...
# EVOLVE-BLOCK-END
```

This design facilitates integrating with existing codebases with minimal changes. Any user-provided code inside such evolution blocks serves as the **initial solution**. The rest of the code forms a **skeleton** that ties evolved pieces together so they can be invoked from `evaluate`. The initial implementation must be complete, but can be rudimentary (e.g., single-line functions returning constants).

#### Flexibility in Abstraction

AlphaEvolve can be applied to the same problem in very different ways:
- **Direct string representation**: evolve the solution in raw string form (as in classical evolutionary algorithms).
- **Constructor function**: evolve a function specifying how to construct the solution from scratch (approach in FunSearch).
- **Bespoke search algorithm**: evolve a search algorithm to find the solution within a fixed compute budget.
- **Co-evolution**: co-evolve intermediate solutions and search algorithms together, such that each search algorithm is tailored to further improve upon a particular intermediate solution.

Different levels of abstraction suit different problems. For problems with **highly symmetric solutions**, evolving constructor functions tends to be advantageous (more concise). For **non-symmetric solutions**, evolving customized search algorithms works better.

---

### 2.2 Prompt Sampling

AlphaEvolve leverages SOTA LLMs and supports various types of customization with long contexts as part of the primary evolution prompt. The prompt comprises:

1. **Multiple previously discovered solutions** sampled from the program database.
2. **System instructions** on how to propose changes to a particular solution.

Beyond these key ingredients, users can further tailor prompts in different ways:

- **Explicit context**: details about the problem being solved — fixed human-written instructions, equations, code snippets, or relevant literature (e.g., PDF files).
- **Stochastic formatting**: template placeholders with human-provided alternatives for increased diversity, instantiated using probability distributions provided in a separate config file.
- **Rendered evaluation results**: usually includes a program, the result of executing that program, and the scores assigned by the `evaluate` function.
- **Meta prompt evolution**: instructions and context suggested by the LLM itself in an additional prompt-generation step, co-evolved in a separate database analogous to the solution programs.

**Example prompt structure (abbreviated):**

```
Act as an expert software developer. Your task is to iteratively
improve the provided codebase. [...]

- Prior programs
Previously we found that the following programs performed well
on the task at hand:
  top_1_acc: 0.796; neg_eval_log_loss: 0.230; average_score: 0.513
  [program code...]

- Current program
Here is the current program we are trying to improve (you will
need to propose a modification to it below).
  top_1_acc: 0.862; neg_eval_log_loss: 0.387; average_score: 0.624
  [program code...]

SEARCH/REPLACE block rules:
[...]

Task
Suggest a new idea to improve the code that is inspired by your
expert knowledge of optimization and machine learning.
Describe each change with a SEARCH/REPLACE block.
```

---

### 2.3 Creative Generation

AlphaEvolve leverages SOTA LLMs whose principal role is to digest information about previously developed solutions and **propose new, diverse ways to improve the solutions**. AlphaEvolve is model-agnostic but benefits from more capable LLMs.

#### Output Format: Diff Blocks

When AlphaEvolve asks an LLM to modify existing code, especially within larger codebases, it requests changes as a sequence of **diff blocks** in a specific format:

```
<<<<<<< SEARCH
# Original code block to be found and replaced
=======
# New code block to replace the original
>>>>>>> REPLACE
```

The code between `<<<<<<< SEARCH` and `=======` is the exact segment to match in the current program version. The code between `=======` and `>>>>>>> REPLACE` is the new segment. This allows targeted updates to specific parts of code.

For very short code or when complete rewrites are more appropriate, AlphaEvolve can be configured to instruct the LLM to output the entire code block directly.

**Example LLM output (abbreviated):**

```
The current model uses a simple ResNet architecture with only
three ResNet blocks. We can improve its performance by
increasing the model capacity and adding regularization...

<<<<<<< SEARCH
self._block1 = ResNetBlock(num_channels)
self._block2 = ResNetBlock(num_channels * 2, stride=2)
self._block3 = ResNetBlock(num_channels * 4, stride=2)
=======
self._block1 = ResNetBlock(num_channels)
self._block2 = ResNetBlock(num_channels, stride=1)
self._block3 = ResNetBlock(num_channels * 2, stride=2)
self._block4 = ResNetBlock(num_channels * 2, stride=1)
self._block5 = ResNetBlock(num_channels * 4, stride=2)
self._block6 = ResNetBlock(num_channels * 4, stride=1)
>>>>>>> REPLACE

<<<<<<< SEARCH
def optimizer(self, learning_rate):
    return optax.adam(learning_rate)
=======
def optimizer(self, learning_rate):
    return optax.adamw(learning_rate, weight_decay=1e-4)
>>>>>>> REPLACE
```

#### Models Used

AlphaEvolve employs an **ensemble of large language models**:

- **Gemini 2.0 Flash**: Lower latency — enables a higher rate of candidate generation, increasing the number of ideas explored per unit of time.
- **Gemini 2.0 Pro**: Greater capabilities — provides occasional, higher-quality suggestions that can significantly advance the evolutionary search and potentially lead to breakthroughs.

This strategic mix optimizes the overall discovery process by maximizing the volume of evaluated ideas while retaining the potential for substantial improvements from the more powerful model.

---

### 2.4 Evaluation

Each new solution proposed by the LLMs is automatically evaluated. In practice, AlphaEvolve supports optional mechanisms to make evaluation more flexible and efficient:

- **Evaluation cascade (hypothesis testing)**: The user can specify ensembles of test cases of increasing difficulty, such that new solutions are evaluated on the next stage only if they achieve sufficiently promising results in all earlier stages. This prunes less promising solutions more quickly. New solutions are initially evaluated on a small scale before being subjected to the main test cases, to filter out faulty programs early.

- **LLM-generated feedback**: For solutions with desirable characteristics that are difficult to capture precisely in the evaluation function (e.g., simplicity of the discovered program), these properties can be graded using separate LLM calls and added to the dictionary of scores to steer evolution, or used to discard solutions when a criterion is not fulfilled.

- **Parallelized evaluation**: AlphaEvolve's sample efficiency makes it feasible to spend on the order of **100 compute-hours** to evaluate any new solution. In many applications, evaluation is embarrassingly parallel (e.g., running a search algorithm from multiple randomized initializations), allowing AlphaEvolve to distribute this work through asynchronous calls to an evaluation cluster.

#### Multiple Scores

AlphaEvolve allows for optimizing **multiple user-provided scores** simultaneously. This has both intrinsic and instrumental value:
- **Intrinsic**: Multiple applications genuinely care about solutions for multiple evaluation metrics.
- **Instrumental**: Even if one metric is of particular interest, optimizing for multiple metrics often improves results for the single target metric — programs excelling under different criteria often possess distinct structures, and incorporating examples of these diverse, high-performing programs into prompts stimulates generation of more varied candidate solutions.

---

### 2.5 Evolution (Program Database)

During evolution, AlphaEvolve continually generates a growing number of solutions with evaluation results (scores and program outputs) attached. These are stored in an **evolutionary database** whose primary goal is to optimally resurface previously explored ideas in future generations.

The key challenge is balancing **exploration and exploitation**:
- Continuously improve the best programs (exploitation).
- Maintain diversity to encourage exploration of the entire search space.

The evolutionary database implements an algorithm inspired by a combination of:
- **MAP-Elites algorithm** [Mouret and Clune, 2015]: quality-diversity algorithm that illuminates search spaces by mapping elites.
- **Island-based population models** [Tanese, 1989; similar to FunSearch]: distributed genetic algorithm with separate populations.

---

### 2.6 Distributed Pipeline

AlphaEvolve is implemented as an **asynchronous computational pipeline** (using the `asyncio` Python library) in which many computations run concurrently, with each computation blocking whenever its next step relies on the result of another, yet unfinished computation.

The asynchronous pipeline comprises:
- A **controller**
- **LLM samplers**
- **Evaluation nodes**

The entire pipeline is optimized for **throughput** (rather than speed of any one computation), to maximize the number of ideas that can be proposed and evaluated within a specific overall computation budget.

---

## 3. Comparison Table: AlphaEvolve vs. FunSearch

| Feature | FunSearch [Romera-Paredes et al., 2023] | AlphaEvolve |
|---|---|---|
| Code scope | Evolves single function | Evolves entire code file |
| Code size | Evolves up to 10–20 lines of code | Evolves up to hundreds of lines of code |
| Programming language | Evolves code in Python only | Evolves any language |
| Evaluation time limit | Needs fast evaluation (≤20 min on 1 CPU) | Can evaluate for hours, in parallel, on accelerators |
| LLM calls required | Millions of LLM samples used | Thousands of LLM samples suffice |
| Model size | Small LLMs used; no benefit from larger | Benefits from SOTA LLMs |
| Context richness | Minimal context (only previous solutions) | Rich context and feedback in prompts |
| Optimization objectives | Optimizes single metric | Can simultaneously optimize multiple metrics |

---

## 4. Applications and Results

### 4.1 Faster Matrix Multiplication via Novel Tensor Decomposition Algorithms

#### Background

Matrix multiplication serves as a fundamental operation underpinning numerous critical algorithms and applications in computer science — from accelerating machine learning to realistic computer graphics. Since the pioneering work of Strassen [1969], it has been known that algorithms for multiplying two matrices can be represented as **decompositions of a 3D tensor into rank-one tensors**. The rank (number of terms) of the decomposition exactly specifies the **number of scalar multiplications** needed to compute the matrix product.

Finding low-rank decompositions of the matrix multiplication tensor is the key challenge. Despite decades of effort using specialized alternating least squares solvers, deep reinforcement learning (AlphaTensor), and custom search algorithms, even for 3×3 matrices, the minimum achievable rank is not known.

#### AlphaEvolve's Approach

Starting from the problem description and a standard gradient-based algorithm (including an initializer, a reconstruction loss function, and an Adam optimizer), AlphaEvolve develops sophisticated tensor decomposition algorithms that outperform existing approaches.

**Evaluation procedure:**
- Choose a set of matrix multiplication targets.
- Run the evolved algorithm, initialized with multiple random seeds, using an evaluation cascade.
- Measure performance as the best (lowest) rank achieved on each target and the fraction of seeds achieving this rank.
- Round each element to the nearest integer or nearest half-integer to ensure exactness; include this request in natural language in the LLM's prompt.

#### Key Changes Introduced by AlphaEvolve (Figure 4)

AlphaEvolve makes significant changes to the initial program across several components, requiring **15 mutations during the evolutionary process**:

1. **Optimizer**: Adam → AdamW with weight decay
   ```python
   return optax.adamw(self.hypers.learning_rate, weight_decay=self.hypers.weight_decay)
   ```

2. **Weight initialization**: Smaller scale with complex initialization
   ```python
   return initializers.normal(0 + 1j * 0, scale * 0.2, jnp.complex64)
   ```

3. **Training loop innovations**:
   - Gradient noise injection for exploration
   - Decomposition parameter noise with linear decay schedule
   - Cyclical annealing for soft clipping threshold (cycle length = 2000 steps)
   - Soft clipping of real and imaginary parts separately

4. **Loss function innovations**:
   - Target tensor noise for robustness
   - Hallucination loss (randomly replacing decomposition values, probability and scale hyperparameters)
   - Discretization loss (encouraging entries to be multiples of 1/2 or integers):
     ```python
     def dist_to_half_ints(x):
         x_re = jnp.real(x)
         x_im = jnp.imag(x)
         return jnp.minimum(
             jnp.abs(x_re - jnp.round(x_re * 2) / 2),
             jnp.abs(x_im - jnp.round(x_im * 2) / 2),
         )
     ```
   - Cosine annealing for half-integer loss
   - Large value penalty for stability

5. **Hyperparameter sweep expansion**: From 2 parameters (`init_scale`, `learning_rate`) to 12 parameters including `discretization_weight`, `hallucination_prob`, `hallucination_scale`, `noise_std`, `target_noise_std`, `weight_decay`, `clip_min`, `clip_max`, `large_value_penalty_weight`, `grad_noise_std`, `half_int_start`.

#### Results: Table of Improvements

The following table shows AlphaEvolve's improvements (selected from Table 2 in the paper; full results in Table 3):

| Tensor ⟨m, n, p⟩ | Best Known [ref] | AlphaEvolve | Improvement |
|---|---|---|---|
| ⟨2, 4, 5⟩ | 33 [42] | **32** | -1 |
| ⟨2, 4, 7⟩ | 46 [93] | **45** | -1 |
| ⟨2, 4, 8⟩ | 52 [93] | **51** | -1 |
| ⟨2, 5, 6⟩ | 48 [93] | **47** | -1 |
| ⟨3, 3, 3⟩ | 23 [52] | 23 | matched |
| ⟨3, 4, 6⟩ | 56 [48] | **54** | -2 |
| ⟨3, 4, 7⟩ | 66 [91] | **63** | -3 |
| ⟨3, 4, 8⟩ | 75 [91] | **74** | -1 |
| ⟨3, 5, 6⟩ | 70 [48] | **68** | -2 |
| ⟨3, 5, 7⟩ | 82 [91] | **80** | -2 |
| ⟨4, 4, 4⟩ | 49 [95] | **48** | -1 |
| ⟨4, 4, 5⟩ | 62 [47] | **61** | -1 |
| ⟨4, 4, 7⟩ | 87 [93] | **85** | -2 |
| ⟨4, 4, 8⟩ | 98 [95] | **96** | -2 |
| ⟨4, 5, 6⟩ | 93 [48] | **90** | -3 |
| ⟨5, 5, 5⟩ | 93 [72] | 93 | matched |

**Full results summary (Table 3):** Of 54 targets, AlphaEvolve matches the state of the art in 38 cases, **surpasses it in 14 cases**, and falls behind in 2 cases. In all cases, AlphaEvolve provides exact algorithms using integer or half-integer entries. For ⟨3, 4, 7⟩, ⟨4, 4, 4⟩, and ⟨4, 4, 8⟩, algorithms use complex-valued multiplications usable for exact multiplication of complex or real-valued matrices.

#### Historic Result: 4×4 Matrix Multiplication

Applying the Strassen [1969] algorithm recursively gives rank **49** for 4×4 matrices (works over any field). For the specific field with 2 elements, AlphaTensor [Fawzi et al., 2022] found rank 47. For **56 years**, designing an algorithm with rank less than 49 over any field with characteristic 0 was an open problem. AlphaEvolve is the **first method to find a rank-48 algorithm** to multiply two 4×4 complex-valued matrices.

> Note: There exist algorithms using fewer than 49 multiplications that do not correspond to decompositions of the matrix multiplication tensor and cannot be applied recursively to multiplying larger matrices.

---

### 4.2 Finding Tailored Search Algorithms for Open Mathematical Problems

#### Scope and Methodology

AlphaEvolve was applied to a curated set of **over 50 mathematical problems** spanning more than five different branches of mathematics: analysis, combinatorics, number theory, and geometry, evaluated across numerous specific parameter settings.

**Key methodological innovation**: AlphaEvolve evolves **heuristic search algorithms** rather than directly evolving the constructions themselves. This iterative refinement strategy works as follows:
- Each generation of AlphaEvolve evolves a program representing a search heuristic.
- This program is given a **fixed time budget** (e.g., 1000 seconds) and is shown the best construction found by the previous best heuristic.
- Its goal is to leverage this starting point and the allotted time to find an even better construction.
- The evolutionary process selects for heuristics that are effective at improving already high-quality solutions.
- The final constructions are often the result of a **sequence of different, specialized heuristics** — early heuristics proficient at making large gains from random or simple initial states, and later heuristics adept at fine-tuning near-optimal configurations.

**Overall results:**
- **~75%** of cases: AlphaEvolve rediscovered the best known constructions.
- **~20%** of cases: AlphaEvolve discovered new objects better than previously known best constructions, thereby improving the SOTA.
- All results started from simple or random initial constructions.

**External collaborators:** Most discoveries are on open problems suggested by external mathematicians **Javier Gomez Serrano** and **Terence Tao**, who also advised on how to best formulate them as inputs to AlphaEvolve.

#### Selected New Mathematical Results

**Analysis:**
- **Autocorrelation inequalities**: AlphaEvolve improved the best known bounds on several autocorrelation inequalities.
- **Uncertainty principles**: AlphaEvolve produced a refined configuration for a problem arising in Fourier analysis, by polishing an uncertainty principle construction [Gonçalves et al., 2017], leading to a slightly better upper bound.

**Combinatorics and Number Theory:**
- **Erdős's minimum overlap problem** [Erdős, 1955]: AlphaEvolve established a new upper bound for the minimum overlap problem, slightly improving upon the previous record [Haugland, 2016].

**Geometry and Packing:**
- **Kissing number problem**: In **11 dimensions**, AlphaEvolve improved the lower bound on the kissing number, finding a configuration of **593 non-overlapping unit spheres** that can simultaneously touch a central unit sphere, surpassing the previous record of **592** [Ganzhinov, 2022].
- **Packing problems**: AlphaEvolve achieved several new results in packing N points in a shape to minimize the ratio of maximum and minimum distance, packing various polygons in other polygons, and variants of the Heilbronn problem concerning point sets avoiding small-area triangles.

---

### 4.3 Optimizing Google's Computing Ecosystem

#### 4.3.1 Improving Data Center Scheduling

**Problem:** Efficiently scheduling compute jobs onto a cluster of machines is a critical optimization problem at the scale of Google's data centers, orchestrated by **Borg** [Verma et al., 2015]. Inefficient assignments cause **stranded resources**: when a machine runs out of one kind of resource (e.g., memory) but still has others free (e.g., CPU). This problem combines typical engineering difficulties (debuggability, scale) on top of the classically difficult **bin-packing problem**.

**Formulation:** Online job scheduling as a **vector bin-packing problem with two variables**:
- Machines = bins with capacities for CPU and memory.
- Incoming jobs = items with specific resource demands.
- A heuristic function takes a pending job's CPU and memory requirements and a potential machine's CPU and memory availability, and outputs a priority score for that machine.
- The Borg scheduler assigns the pending job to the machine with the highest priority score.

**Discovered heuristic function:**
```python
def alpha_evolve_score(required, free):
    cpu_residual = required.cpu / free.cpu
    mem_residual = required.mem / free.mem

    return -1.0 * (cpu_residual + mem_residual +
                   mem_residual / cpu_residual +
                   cpu_residual / mem_residual)
```

**Process:**
- A simulator of Google's data centers provides feedback to AlphaEvolve based on historical snapshots of workloads and capacity across Google's fleet.
- Performance is measured on an unseen test dataset of recent workloads to ensure generalization.

**Results:** Post-deployment measurements across Google's fleet confirmed simulator results, revealing that this heuristic function **continuously recovers on average 0.7% of Google's fleet-wide compute resources** that would otherwise be stranded.

**Why AlphaEvolve over deep RL:** The code solution offers clear advantages in **interpretability, debuggability, predictability, and ease of deployment** — essential qualities for a mission-critical system.

---

#### 4.3.2 Enhancing Gemini Kernel Engineering

**Problem:** Training large models like Gemini requires substantial computational resources. Gemini is built on JAX, and Pallas (an extension to JAX) enables writing custom, highly specialized programs (kernels) for optimal execution on hardware accelerators. A critical aspect of kernel optimization is tuning the **tiling strategy for matrix multiplication operations** — dividing a large matrix multiplication into smaller subproblems to better balance computation with data movement.

Challenges:
- Search-based tuning interrupts the research workflow and requires retuning for every input shape change.
- Manually crafting effective tiling heuristics is a major engineering bottleneck, demanding deep understanding of both kernel functionality and hardware intricacies.

**AlphaEvolve's approach:**
- Optimizes tiling heuristics for an important matrix multiplication kernel used to train Gemini.
- Objective: minimize kernel's actual runtime.
- Proposes candidate code and iteratively refines tiling heuristics on real TPU accelerators.
- Kernel correctness maintained by construction (optimizing tiling strategy only, not the underlying math).
- Training set: half of realistic input shapes collected from kernel users.
- Evaluation set: remaining input shapes for testing general applicability.

**Results:**
- **23% average kernel speedup** across all kernels vs. the existing expert-designed heuristic.
- **1% reduction in Gemini's overall training time**.
- Kernel optimization time reduced from **several months of dedicated engineering effort to just days** of automated experimentation.
- Heuristic deployed in production — a novel instance where Gemini, through AlphaEvolve, **optimizes its own training process**.

---

#### 4.3.3 Assisting in Hardware Circuit Design (TPU)

**Problem:** Designing new computer chips is complex and time-consuming (spanning years). Register-Transfer Level (RTL) optimization involves manually rewriting hardware descriptions to improve power, performance, and area metrics, demanding months of iteration by highly skilled engineers.

**AlphaEvolve's task:** Optimize an already highly optimized Verilog implementation of a key TPU arithmetic circuit within the matrix multiplication unit. Objectives: reduce area and power consumption while preserving core functionality. The final proposal must pass robust verification methods to confirm functional correctness.

**Result:** AlphaEvolve found a simple code rewrite that removed unnecessary bits. While this specific improvement was also independently caught by downstream synthesis tools, AlphaEvolve's contribution at the RTL stage demonstrates its capability to refine source RTL and provide optimizations early in the design flow.

**Significance:** Integrated into an upcoming TPU. This represents **Gemini's first direct contribution to TPU arithmetic circuits**, achieved via AlphaEvolve. AlphaEvolve communicates suggested changes directly in Verilog (the standard language used by hardware engineers), fostering trust and simplifying adoption.

---

#### 4.3.4 Directly Optimizing Compiler-Generated Code (FlashAttention / XLA)

**Problem:** The transformer architecture (Vaswani et al., 2017) is used in the majority of modern neural networks. The core computation is the attention mechanism, most commonly implemented using **FlashAttention** [Dao et al., 2022]. In Google's stack, FlashAttention is implemented as an accelerator kernel in Pallas, wrapped by higher-level JAX code. The machine learning compiler (XLA) then translates this into a sequence of intermediate representations (IRs).

**AlphaEvolve's task:** Directly optimize XLA-generated IRs encapsulating the FlashAttention kernel along with pre- and postprocessing code. Target: a highly impactful transformer model used for inference at scale on GPUs. Minimize the module's overall execution time.

**Challenges:**
1. The IR is designed for debugging purposes rather than for direct editing by developers.
2. It is compiler-generated and already highly optimized.
3. Each modification was checked against reference (unmodified) code on randomized inputs to ensure numerical correctness throughout optimization.

**Results:**
- **32% speedup** of the FlashAttention kernel for the configuration of interest.
- **15% speedup** in pre- and postprocessing of kernel inputs and outputs.
- Final version confirmed by human experts to be correct for all possible inputs.

---

## 5. Ablation Studies

Ablations were carried out on two tasks:
1. Finding tensor decompositions for faster matrix multiplication (Section 3.1)
2. Computing lower bounds on kissing numbers (Section 3.2)

### Ablated Components

| Component | Description | Ablation Name |
|---|---|---|
| Evolutionary approach | AlphaEvolve uses a program database to store and sample previously generated programs for subsequent iterations. | "No evolution" — repeatedly feeds the same initial program to the LLM |
| Context in prompts | AlphaEvolve provides problem-specific context in the prompt. | "No context in the prompt" — no explicit context added |
| Meta prompt evolution | AlphaEvolve uses meta prompts to improve prompts, potentially surpassing human prompter performance. | "No meta prompt evolution" — meta prompting disabled (tensor decomposition only) |
| Full-file evolution | Unlike FunSearch, AlphaEvolve can evolve entire codebases. | "No full-file evolution" — only the loss function is evolved (tensor decomposition only) |
| Powerful language models | AlphaEvolve uses a mixture of small and large LLMs for highly diverse samples. | "Small base LLM only" — only a single small base model used |

### Results (Figure 8)

For **matrix multiplication tensor decomposition**:
- Full method outperforms all ablations.
- Removal of evolution, context, full-file evolution, meta prompts, and use of only a small LLM each result in significant degradation.
- Curves are averaged over all considered targets (higher values on the target metric are better), with shades indicating intra-target standard deviation averaged over three independent runs with different random seeds.

For **kissing number problem**:
- Full method also outperforms "No evolution" and "No context in the prompt" ablations clearly.

**Conclusion:** Each of the components — evolutionary approach, contextual prompting, meta prompt evolution, full-file evolution, and powerful LLMs — is responsible for a significant improvement in results.

---

## 6. Discussion and Limitations

### Key Insights

1. **Surprising power of the combination**: SOTA LLMs + automated evaluation metrics + evolutionary framework can lead to new discoveries on decades-old mathematical problems as well as practical improvements to highly optimized compute stacks.

2. **Multiple problem formulations**: AlphaEvolve can approach the same problem in different ways (direct search, constructor function, bespoke search algorithm), each with different biases. Constructive functions may favor discovering highly symmetric objects; customized search algorithms suit non-symmetric solutions.

3. **Test-time compute scaling**: AlphaEvolve can be seen as a **test-time compute agent** that significantly enhances the capability of the base LLM (compared to, e.g., repeated sampling) through its evolutionary procedure. This is a compelling demonstration of how machine feedback sustains test-time compute scaling into regimes where new scientific discoveries and highly valuable practical optimizations are made.

4. **Distillation opportunity**: A natural next step is to distill AlphaEvolve-augmented performance into the next generation of base models — having both intrinsic value and likely uplifting the next version of AlphaEvolve.

5. **Self-improvement feedback loop**: AlphaEvolve can make practical discoveries that increase the efficiency of its own infrastructure and future versions of its base LLMs. Currently gains are moderate and feedback loops are on the order of months. With improvements, the value of setting up more environments with robust evaluation functions will become more widely recognized.

### Main Limitation

The main limitation of AlphaEvolve is that it handles problems for which it is possible to devise an **automated evaluator**. While this is true of many problems in the mathematical and computational sciences, there are domains (e.g., natural sciences) where only some experiments can be simulated or automated.

While AlphaEvolve does allow for LLM-provided evaluation of ideas, this is not a setting optimized for in the current work. However, concurrent work (AI Co-Scientist) shows this is possible, and a natural step would be to link the two settings — LLMs providing feedback on high-level ideas before transitioning to an implementation stage for which machine feedback is available through code execution.

---

## 7. Key Figures Descriptions

### Figure 1 — AlphaEvolve High-Level Overview
Shows the four-component system: the human defines evaluation criteria and initial solution; AlphaEvolve figures out improved solutions. The Prompt Sampler, LLMs Ensemble, Evaluators Pool, and Program Database form a closed loop.

### Figure 2 — Expanded View of the Discovery Process
Shows the detailed distributed controller loop with pseudocode. The user provides an initial program (with evolution blocks marked), evaluation code, and optional configurations. The evolutionary loop runs: sample from database → build prompt → LLM generates diff → apply diff → evaluate → register back into database.

### Figure 3 — Illustrative Example (Image Classification Pipeline)
(a) User-provided file with `# EVOLVE-BLOCK-START` / `# EVOLVE-BLOCK-END` markers and the `evaluate` function. (b) Example assembled prompt showing prior programs with scores, current program with score, and task instructions. (c) Example LLM output with SEARCH/REPLACE diff blocks.

### Figure 4 — Changes Proposed for Matrix Multiplication
Full diff showing AlphaEvolve's extensive changes across several components to discover the rank-48 4×4 matrix multiplication algorithm, requiring 15 mutations. Magnified excerpts show changes to optimizer, weight initialization, loss function, and hyperparameter sweep.

### Figure 5 — SOTA-Breaking Mathematical Constructions
Examples of new constructions in analysis (autocorrelation and uncertainty inequalities), geometry (packing and minimum/maximum distance problems), and combinatorics (Erdős's minimum overlap problem and sums/differences of finite sets). Shows numerical improvements: e.g., geometry value 4.000 → 3.942, combinatorics 12.890 → 12.889.

### Figure 6 — Data Center Scheduling Heuristic
Left: The discovered Python heuristic function. Right: Visualization of the scoring function — yellow regions represent high scores, purple regions represent low scores, plotted across CPU residual (0–100%) vs. Memory residual (0–100%).

### Figure 7 — Tiling Heuristic Problem Visualization
Illustrates the tile size selection problem (M, N, P) for matrix product A×B=C, showing how the matrix is decomposed into tiles. Creating a heuristic that automatically chooses the right tile size for all input shapes is difficult because of matrix multiplication unit's optimal shapes, memory capacity, surrounding operation memory requirements, extra fused operations, and low-level compiler intricacies.

### Figure 8 — Ablation Study Results
Left (tensor decomposition): curves for Full method vs. No meta prompt evolution, Small base LLM only, No context in the prompt, No full-file evolution, No evolution. Right (kissing number): Full method vs. No context in the prompt, No evolution. X-axis: fraction of compute budget (0–100%); Y-axis: aggregated target metric.

### Figures 9a–9c — Magnified Diff for 4×4 Matrix Multiplication
Three-part magnified view of the full program diff that discovers the rank-48 algorithm for multiplying 4×4 matrices.

---

## 8. Related Work

### Evolutionary Methods
AlphaEvolve extends a long tradition of research on evolutionary or genetic programming [Langdon and Poli, 2013], where mutation and crossover operators evolve a pool of programs. Classical evolutionary techniques have succeeded in symbolic regression, automated scientific/algorithmic discovery, and scheduling problems. AlphaEvolve uses LLMs to automate construction of these operators, leveraging world knowledge to mutate programs without pre-defining allowed mutation operations.

**Key predecessor:** FunSearch [Romera-Paredes et al., 2023]. AlphaEvolve goes beyond FunSearch in three ways:
1. FunSearch evolved a single Python function; AlphaEvolve evolves entire codebases in any language.
2. FunSearch optimized a single objective; AlphaEvolve supports multi-objective optimization.
3. FunSearch used small, code-only LLMs; AlphaEvolve uses frontier LLMs with rich natural-language context and feedback.

**Other related systems:** Lehman et al. [2023] (LLM-guided evolution for robot policies); Hemberg et al. [2024] (code synthesis); LLM-guided evolution for symbolic regression, combinatorial optimization heuristics, and molecular structures; EvoPrompting [Chen et al., 2023] (neural architecture search); Surina et al. [2025] (evolution + RL fine-tuning); Grayeli et al. [2024] (LLM-directed concept learning).

### Superoptimization and Algorithm Discovery
Code superoptimization dates to the 1980s [Massalin, 1987]. Pre-LLM approaches included systematic enumeration, genetic search, Monte Carlo sampling, and deep RL. AlphaTensor [Fawzi et al., 2022] discovered provably correct matrix multiplication algorithms using deep RL. More recent LLM-based approaches: attention operation optimization on GPUs, general user-specified kernel operations, novel evolutionary algorithm discovery, LLM training optimization, warehouse-scale computer optimization.

### AI for Scientific and Mathematical Discovery
AI has been applied broadly to protein structure prediction (AlphaFold), quantum physics, climate sciences, materials science, chemistry, bioinformatics, and more. FunSearch established LLM-guided evolution as a powerful tool for discovering witnesses and counterexamples to mathematical statements, complementing formal proof-finding approaches (AlphaProof, AlphaGeometry).

---

## 9. References (Selected Key References)

| # | Citation | Notes |
|---|---|---|
| [22] | Dao et al. (2022). FlashAttention: Fast and memory-efficient exact attention with io-awareness. NeurIPS 35:16344–16359. | FlashAttention implementation target |
| [23] | Davies et al. (2021). Advancing mathematics by guiding human intuition with AI. Nature 600(7887):70–74. | AI for pure mathematics |
| [25] | Erdős (1955). Some remarks on number theory. Riveon Lematematika 9:45–48. | Minimum overlap problem |
| [26] | Fawzi et al. (2022). Discovering faster matrix multiplication algorithms with reinforcement learning. Nature 610(7930):47–53. | AlphaTensor |
| [31] | Ganzhinov (2022). Highly symmetric lines. arXiv:2207.08266v1. | Kissing number 11D previous record (592) |
| [40] | Haugland (2016). The minimum overlap problem revisited. arXiv:1609.08000. | Previous Erdős record |
| [46] | Jumper et al. (2021). Highly accurate protein structure prediction with AlphaFold. Nature 596(7873):583–589. | AlphaFold |
| [50] | Kingma and Ba (2015). Adam: A method for stochastic optimization. ICLR. | Adam optimizer |
| [52] | Laderman (1976). A noncommutative algorithm for multiplying 3×3 matrices using 23 multiplications. Bull. AMS 82(1):126–128. | 3×3 rank-23 algorithm |
| [54] | Langdon and Poli (2013). Foundations of genetic programming. Springer. | Genetic programming foundations |
| [68] | Mankowitz et al. (2023). Faster sorting algorithms discovered using deep reinforcement learning. Nature 618(7964):257–263. | AlphaSort / deep RL for algorithms |
| [72] | Moosbauer and Poole (2025). Flip graphs with symmetry and new matrix multiplication schemes. arXiv:2502.04514. | Previous 5×5×5 rank-93 result |
| [74] | Mouret and Clune (2015). Illuminating search spaces by mapping elites. arXiv:1504.04909. | MAP-Elites algorithm |
| [77] | OpenXLA. XLA: composable transformations of Python+NumPy programs. | XLA compiler |
| [83] | Romera-Paredes et al. (2023). Mathematical discoveries from program search with large language models. Nature 625(7995):468–475. | FunSearch |
| [88] | Shinn et al. (2023). Reflexion: Language agents with verbal reinforcement learning. NeurIPS 36:8634–8652. | LLM agents |
| [95] | Strassen (1969). Gaussian elimination is not optimal. Numerische Mathematik 13(4):354–356. | Original Strassen algorithm (rank 7 for 2×2, recursive rank 49 for 4×4) |
| [97] | Tanese (1989). Distributed genetic algorithms for function optimization. Univ. of Michigan. | Island-based population models |
| [100] | Vaswani et al. (2017). Attention is all you need. NeurIPS. | Transformer architecture |
| [102] | Verma et al. (2015). Large-scale cluster management at Google with Borg. EuroSys '15. | Google Borg scheduler |

---

## Appendix A: Full Matrix Multiplication Results (Table 3)

Complete table of tensor decomposition ranks for all 54 considered matrix sizes (m ≤ n ≤ p, with 2 ≤ m, n ≤ 5):

| ⟨m, n, p⟩ | Best Known | AlphaEvolve | Status |
|---|---|---|---|
| ⟨2, 2, 2⟩ | 7 [95] | 7 | matched |
| ⟨2, 2, 3⟩ | 11 [93] | 11 | matched |
| ⟨2, 2, 4⟩ | 14 [93] | 14 | matched |
| ⟨2, 2, 5⟩ | 18 [93] | 18 | matched |
| ⟨2, 2, 6⟩ | 21 [93] | 21 | matched |
| ⟨2, 2, 7⟩ | 25 [93] | 25 | matched |
| ⟨2, 2, 8⟩ | 28 [93] | 28 | matched |
| ⟨2, 2, 9⟩ | 32 [93] | 32 | matched |
| ⟨2, 2, 10⟩ | 35 [93] | 35 | matched |
| ⟨2, 2, 11⟩ | 39 [93] | 39 | matched |
| ⟨2, 2, 12⟩ | 42 [93] | 42 | matched |
| ⟨2, 2, 13⟩ | 46 [93] | 46 | matched |
| ⟨2, 2, 14⟩ | 49 [93] | 49 | matched |
| ⟨2, 2, 15⟩ | 53 [93] | 53 | matched |
| ⟨2, 2, 16⟩ | 56 [93] | 56 | matched |
| ⟨2, 3, 3⟩ | 15 [93] | 15 | matched |
| ⟨2, 3, 4⟩ | 20 [93] | 20 | matched |
| ⟨2, 3, 5⟩ | 25 [93] | 25 | matched |
| ⟨2, 3, 6⟩ | 30 [93] | 30 | matched |
| ⟨2, 3, 7⟩ | 35 [93] | 35 | matched |
| ⟨2, 3, 8⟩ | 40 [93] | 40 | matched |
| ⟨2, 3, 9⟩ | 45 [93] | 45 | matched |
| ⟨2, 3, 10⟩ | 50 [93] | 50 | matched |
| ⟨2, 4, 4⟩ | 26 [93] | 26 | matched |
| ⟨2, 4, 5⟩ | 33 [42] | **32** | improved |
| ⟨2, 4, 6⟩ | 39 [93] | 39 | matched |
| ⟨2, 4, 7⟩ | 46 [93] | **45** | improved |
| ⟨2, 4, 8⟩ | 52 [93] | **51** | improved |
| ⟨2, 5, 5⟩ | 40 [93] | 40 | matched |
| ⟨2, 5, 6⟩ | 48 [93] | **47** | improved |
| ⟨3, 3, 3⟩ | 23 [52] | 23 | matched |
| ⟨3, 3, 4⟩ | 29 [93] | 29 | matched |
| ⟨3, 3, 5⟩ | 36 [93] | 36 | matched |
| ⟨3, 3, 6⟩ | 40 [93] | 40 | matched |
| ⟨3, 3, 7⟩ | 49 [93] | 49 | matched |
| ⟨3, 3, 8⟩ | 55 [93] | 55 | matched |
| ⟨3, 4, 4⟩ | 38 [93] | 38 | matched |
| ⟨3, 4, 5⟩ | 47 [26] | 47 | matched |
| ⟨3, 4, 6⟩ | 56 [48] | **54** | improved |
| ⟨3, 4, 7⟩ | 66 [91] | **63** | improved (complex) |
| ⟨3, 4, 8⟩ | 75 [91] | **74** | improved |
| ⟨3, 5, 5⟩ | 58 [91] | 58 | matched |
| ⟨3, 5, 6⟩ | 70 [48] | **68** | improved |
| ⟨3, 5, 7⟩ | 82 [91] | **80** | improved |
| ⟨4, 4, 4⟩ | 49 [95] | **48** | improved (complex) |
| ⟨4, 4, 5⟩ | 62 [47] | **61** | improved |
| ⟨4, 4, 6⟩ | 73 [48] | 73 | matched |
| ⟨4, 4, 7⟩ | 87 [93, 95] | **85** | improved |
| ⟨4, 4, 8⟩ | 98 [95] | **96** | improved (complex) |
| ⟨4, 4, 9⟩ | 104 [92] | 108 | worse |
| ⟨4, 5, 5⟩ | 76 [26] | 76 | matched |
| ⟨4, 5, 6⟩ | 93 [48] | **90** | improved |
| ⟨5, 5, 5⟩ | 93 [72] | 93 | matched |
| ⟨6, 6, 6⟩ | 153 [72] | 156 | worse |

**Summary:** 38 matched, 14 improved, 2 worse (⟨4, 4, 9⟩ and ⟨6, 6, 6⟩).

Note: Concurrent work [Kauers and Wood, 2025] also found a rank-90 algorithm for ⟨4, 5, 6⟩.

---

## Appendix B: Mathematical Problems (Summary)

AlphaEvolve was applied to over 50 problems across 5+ mathematical branches. Key problem areas include:

**Analysis:**
- Autocorrelation inequalities (suprema of autoconvolutions, related to Sidon sets [Cloninger and Steinerberger, 2017])
- Uncertainty principles (Hermite polynomials, linear flows on the torus [Gonçalves et al., 2017]; optimal uncertainty principle in 12 dimensions [Cohn and Gonçalves, 2019])

**Combinatorics and Number Theory:**
- Erdős's minimum overlap problem [Erdős, 1955; Haugland, 2016; White, 2023]
- Sums and differences of finite sets [Gyarmati et al., 2007]
- Generalized Sidon sets [Vinuesa del Rio, 2010]

**Geometry and Packing:**
- Kissing number problem (achieved 593 in 11D, beating previous record of 592 [Ganzhinov, 2022]; survey: Boyvalenkov et al. [2012])
- Packing N points in a shape (min ratio max/min distance)
- Polygon packing in other polygons
- Heilbronn problem (point sets avoiding small-area triangles) [Friedman, 2025]

Problems were suggested by external collaborators Terence Tao, Javier Gomez Serrano, and Jordan Ellenberg. Full new constructions available in the accompanying Google Colab. More details to be provided in an upcoming paper.
