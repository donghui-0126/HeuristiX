# Mathematical Discoveries from Program Search with Large Language Models

**FunSearch: Searching in the Function Space**

**Journal:** Nature, Vol. 625, pp. 468–476, 18 January 2024
**DOI:** https://doi.org/10.1038/s41586-023-06924-6
**Received:** 12 August 2023 | **Accepted:** 30 November 2023 | **Published online:** 14 December 2023
**Open Access** (CC BY 4.0)

---

## Authors and Affiliations

**Authors:**
Bernardino Romera-Paredes¹·⁴ ✉, Mohammadamin Barekatain¹·⁴, Alexander Novikov¹·⁴, Matej Balog¹·⁴, M. Pawan Kumar¹·⁴, Emilien Dupont¹·⁴, Francisco J. R. Ruiz¹·⁴, Jordan S. Ellenberg², Pengming Wang¹, Omar Fawzi³, Pushmeet Kohli¹ ✉, Alhussein Fawzi¹·⁴ ✉

**Affiliations:**
1. Google DeepMind, London, UK
2. Department of Mathematics, University of Wisconsin-Madison, Madison, WI, USA
3. Laboratoire de l'Informatique du Parallélisme, University of Lyon (Inria, ENS Lyon, UCBL, LIP), Lyon, France
4. These authors contributed equally: Bernardino Romera-Paredes, Mohammadamin Barekatain, Alexander Novikov, Matej Balog, M. Pawan Kumar, Emilien Dupont, Francisco J. R. Ruiz, Alhussein Fawzi

**Correspondence:** brp@google.com; pushmeet@google.com; afawzi@google.com

---

## Abstract

Large language models (LLMs) have demonstrated tremendous capabilities in solving complex tasks, from quantitative reasoning to understanding natural language. However, LLMs sometimes suffer from confabulations (or hallucinations), which can result in them making plausible but incorrect statements. This hinders the use of current large models in scientific discovery.

Here we introduce **FunSearch** (short for *searching in the function space*), an evolutionary procedure based on pairing a pretrained LLM with a systematic evaluator. We demonstrate the effectiveness of this approach to surpass the best-known results in important problems, pushing the boundary of existing LLM-based approaches.

Applying FunSearch to a central problem in extremal combinatorics — **the cap set problem** — we discover new constructions of large cap sets going beyond the best-known ones, both in finite dimensional and asymptotic cases. This shows that it is possible to make discoveries for established open problems using LLMs.

We showcase the generality of FunSearch by applying it to an algorithmic problem, **online bin packing**, finding new heuristics that improve on widely used baselines.

In contrast to most computer search approaches, FunSearch searches for *programs that describe how to solve a problem*, rather than what the solution is. Beyond being an effective and scalable strategy, discovered programs tend to be more interpretable than raw solutions, enabling feedback loops between domain experts and FunSearch, and the deployment of such programs in real-world applications.

---

## 1. Introduction and Motivation

### The Core Problem Setting

Many problems in mathematical sciences are "easy to evaluate" despite being typically "hard to solve." For example, in computer science, NP-complete optimization problems admit a polynomial-time evaluation procedure (measuring the quality of the solution), despite the widespread belief that no polynomial-time algorithms to solve such problems exist.

The paper focuses on problems admitting an efficient **'evaluate' function**, which measures the quality of a candidate solution. Prominent examples include:
- The maximum independent set problem
- Maximum constraint satisfaction problems (such as finding the ground state energy of a Hamiltonian)

The goal is to generate a **'solve' program** such that its outputs receive high scores from the 'evaluate' function (when executed on inputs of interest), and ultimately improve on the best-known solutions.

### Limitations of Current LLMs

While LLMs have recently seen notable improvements in coding capabilities — with applications including debugging, solving code competitions, and improving code performance — synthesizing 'solve' programs for open problems requires finding new ideas that are verifiably correct. This is very hard for LLMs, as they tend to confabulate or ultimately fall short of going beyond existing results.

### FunSearch's Approach

To surpass the "nominal" capabilities of LLMs, FunSearch combines them with evolutionary algorithms, pushing the boundary of LLM-guided evolutionary procedures to a new level:
- Discovery of new scientific results for established open problems
- Discovery of new algorithms

Surpassing state-of-the-art results on established open problems provides a clear indication that the discoveries are truly new, as opposed to being retrieved from the LLM's training data.

### Key Innovations

FunSearch combines a **pretrained (frozen) LLM** (creative core) with an **evaluator** (guards against confabulations and incorrect ideas). It iterates over these two components, evolving initial low-scoring programs into high-scoring ones.

Key ingredients:
1. **Best-shot prompting**: Sample best performing programs and feed them back into prompts for the LLM to improve upon
2. **Program skeleton**: Start with a skeleton containing boilerplate code and known structure; evolve only the critical logic part
3. **Island-based evolutionary method**: Maintain a large pool of diverse programs to encourage exploration and avoid local optima
4. **Distributed asynchronous scaling**: Leverages parallelism, considerably broadening scope while keeping cost low

### Key Results

- **Cap set problem**: Discovered hitherto unknown constructions that go beyond existing ones, including the largest improvement in 20 years to the asymptotic lower bound
- **Online bin packing**: Found new algorithms that improve on traditional ones on well-studied distributions, with potential applications to job scheduling

### Searching in Function Space vs. Solution Space

Most computer search techniques output directly *what the solution is* (e.g., a list of vectors forming a cap set). FunSearch produces **programs generating the solution**. For structured problems, such programs tend to be:
- More interpretable — facilitating interactions with domain experts
- More concise — making it possible to scale to large instances
- Easier to deploy — especially decision procedures described by code in a standard programming language, compared to neural networks which require specialized hardware

---

## 2. The FunSearch Method

### 2.1 Overview (Fig. 1)

The FunSearch loop:
1. **Input**: A specification of the problem as an 'evaluate' function, an initial (possibly trivial) implementation of the function to evolve, and optionally a skeleton
2. **Prompt construction**: At each iteration, FunSearch builds a prompt by combining several programs sampled from the programs database (favouring high-scoring ones)
3. **LLM generation**: The prompt is fed to the pretrained LLM, which creates new programs
4. **Evaluation**: Newly created programs are scored
5. **Storage**: Correct programs are stored back in the programs database, closing the loop
6. **Retrieval**: The user can at any point retrieve the highest-scoring programs discovered so far

### 2.2 Specification

The input to FunSearch is a specification in the form of an 'evaluate' function which scores candidate solutions. An initial program (which can be trivial) to evolve is also provided.

**Key design insight**: Performance improves significantly when the initial 'solve' program is written as a **skeleton** containing:
- Boilerplate code
- Previous knowledge of the problem as a program structure
- Only the critical part governing logic is evolved by FunSearch

**Rationale**: A fixed skeleton may constrain the space of programs that can be discovered, but it improves overall results because it focuses LLM resources on only evolving the critical part, instead of also using the LLM to recreate already known program structures (which has more opportunities for mistakes that would render the entire program incorrect).

**Optional extras**: The user can optionally provide extra known information in the form of docstrings, relevant primitive functions, or import packages.

#### Example Specification for Cap Set Problem (Fig. 2a):

```python
"""Finds large cap sets."""
import numpy as np
import utils_capset

# Function to be executed by FunSearch.
def main(n):
    """Runs `solve` on `n`-dimensional cap set and evaluates the output."""
    solution = solve(n)
    return evaluate(solution, n)

def evaluate(candidate_set, n):
    """Returns size of candidate_set if it is a cap set, None otherwise."""
    if utils_capset.is_capset(candidate_set, n):
        return len(candidate_set)
    else:
        return None

def solve(n):
    """Builds a cap set of dimension `n` using `priority` function."""
    # Precompute all priority scores.
    elements = utils_capset.get_all_elements(n)
    scores = [priority(el, n) for el in elements]
    # Sort elements according to the scores.
    elements = elements[np.argsort(scores, kind='stable')[::-1]]
    # Build `capset` greedily, using scores for prioritization.
    capset = []
    for element in elements:
        if utils_capset.can_be_added(element, capset):
            capset.append(element)
    return capset

# Function to be evolved by FunSearch.
def priority(element, n):
    """Returns the priority with which we want to add `element` to the cap set."""
    return 0.0
```

#### Example Specification for Online Bin Packing (Fig. 2b):

```python
"""Finds good assignment for online 1d bin packing."""
import numpy as np
import utils_packing

# Function to be executed by FunSearch.
def main(problem):
    """Runs `solve` on online 1d bin packing instance, and evaluates the output."""
    bins = problem.bins
    # Packs `problem.items` into `bins` online.
    for item in problem.items:
        # Extract bins that have space to fit item.
        valid_bin_indices = utils_packing.get_valid_bin_indices(item, bins)
        best_index = solve(item, bins[valid_bin_indices])
        # Add item to the selected bin.
        bins[valid_bin_indices[best_index]] -= item
    return evaluate(bins, problem)

def evaluate(bins, problem):
    """Returns the negative of the number of bins required to pack items in `problem`."""
    if utils_packing.is_valid_packing(bins, problem):
        return -utils_packing.count_used_bins(bins, problem)
    else:
        return None

def solve(item, bins):
    """Selects the bin with the highest value according to `heuristic`."""
    scores = heuristic(item, bins)
    return np.argmax(scores)

# Function to be evolved by FunSearch.
def heuristic(item, bins):
    """Returns priority with which we want to add `item` to each bin."""
    return -(bins - item)
```

### 2.3 Pretrained LLM

The LLM is the **creative core** of FunSearch, in charge of coming up with improvements to the functions presented in the prompt.

Key characteristics:
- Uses a **pretrained model** — no fine-tuning on the specific problems
- Uses **Codey**, an LLM built on top of the PaLM 2 model family, fine-tuned on a large corpus of code and publicly accessible through its API (Vertex AI, Google Cloud)
- Important performance-defining tradeoff: quality of samples vs. inference speed — chose to work with a **fast-inference model** (rather than slower-inference, higher-quality)
- Total number of samples on the order of **10^6**
- Results are not too sensitive to the exact choice of LLM, as long as it has been trained on a large enough corpus of code
- Comparison to StarCoder (a state-of-the-art open-source LLM for code) is provided in Supplementary Information Appendix A

### 2.4 Evaluation

Programs generated by the LLM are evaluated and scored on a set of inputs:
- **Cap set problem**: inputs are the values of dimensionality *n* of interest
- **Combinatorial optimization**: inputs correspond to different bin packing instances

Scores across different inputs are combined into an overall score using an **aggregation function** (such as the mean).

**Filtering**: Programs that were incorrect — that did not execute within imposed time and memory limits, or produced invalid outputs — are discarded. Only correct programs are sent to the programs database.

### 2.5 Programs Database (Island Model)

The programs database keeps a population of correct programs, which are then sampled to create prompts. Preserving and encouraging **diversity** is crucial to enable exploration and avoid local optima.

**Island-based evolutionary method** (also known as multiple population / multiple-deme model):
- Several **islands** (subpopulations) are created and evolved independently
- To sample from the database: first sample an island, then sample a program within that island, favouring higher-scoring and shorter programs
- **Information flow between islands**: every 4 hours, programs in the worst half of the islands (those whose best individuals have the lowest scores) are discarded
- The discarded islands are replaced with a new population, initialized by cloning one of the best individuals from the surviving islands

**Advantages of the island model**:
1. Effectively runs several smaller experiments in parallel instead of a single large experiment
2. Single experiments can get stuck in local minima — the multiple island approach allows killing off such experiments
3. Promising experiments run longer, as islands that survive a reset are the ones with higher scores

#### Clustering within Islands

Within each island, programs are further clustered according to their **signature** — the tuple containing the program's scores on each of the inputs (e.g., the cap set size for each input *n*). Programs with the same signature are clustered together.

When sampling:
1. Sample a cluster within the island (favouring higher-scoring clusters)
2. Sample a program within that cluster (favouring shorter programs)

**Cluster sampling probability** (Boltzmann selection):

$$P_i = \frac{\exp(s_i / T_{\text{cluster}})}{\sum_{i'} \exp(s_{i'} / T_{\text{cluster}})}, \quad T_{\text{cluster}} = T_0 \cdot \left(1 - \frac{N \bmod n}{N}\right)$$

where $T_{\text{cluster}}$ is a temperature parameter, $n$ is the current number of programs in the island, and $T_0$ and $N$ are hyperparameters.

**Program sampling within a cluster** (favours shorter programs):
- Let $\ell_i$ denote the negative length of the $i$th program (measured in characters)
- Let $\tilde{\ell}_i = \ell_i - \min_{i'} \ell_{i'} + 10$ (shifted negative lengths)
- Probability proportional to $\exp(\tilde{\ell}_i / T_{\text{program}})$

This approach is related to Lexicase selection (both consider a set of test cases for scoring) and fitness uniform optimization (both cluster individuals by fitness value).

### 2.6 Prompt Construction (Best-Shot Prompting)

New prompts are created by **best-shot prompting** from the programs database:

1. Sample $k$ programs from a single island (using the selection mechanism above). In practice, $k = 2$ — two functions lead to better results compared to just one, with diminishing returns beyond that.
2. Sort sampled programs according to their score (ascending)
3. Assign version numbers: 'v0' for lowest scoring, 'v1' for second lowest, etc.
4. Combine into a single prompt with version appended as suffix to function name (e.g., `priority_v0`, `priority_v1`)
5. Append the header of the function to be generated (e.g., `priority_v2`) at the end

**Rationale**: Constructing a prompt by combining several programs (as opposed to only one) enables the LLM to spot patterns across the different programs and generalize those.

The overall structure of the prompt mimics the structure of the program skeleton, with the following differences:
1. The 'priority' function is stripped out and replaced with the $k = 2$ programs sampled
2. After that, a 'priority_v2' function with no body is appended — the LLM completes the body
3. All other functions that appear before 'priority_v0' are removed

### 2.7 Distributed Approach

FunSearch is implemented as a **distributed system** with three types of workers communicating asynchronously:

| Worker Type | Role |
|---|---|
| Programs database | Stores and serves programs |
| Samplers | Generate new functions using the pretrained LLM |
| Evaluators | Assess programs by executing and scoring them |

**Typical scale**: 15 samplers and 150 CPU evaluators (can be served on five CPU servers each running 32 evaluators in parallel).

**Advantages**:
1. Naturally leverages parallelism — LLM sampling and evaluation performed concurrently
2. Enables scaling to more than one sampler and evaluator (evaluation can take minutes for many problems)
3. Evaluators run on inexpensive CPU hardware; few samplers run on machines with accelerators — keeps cost and energy usage low
4. Running evaluators in parallel considerably broadens the scope of the approach

---

## 3. Application 1: Extremal Combinatorics

Extremal combinatorics is a branch of mathematics that studies the maximal (or minimal) possible sizes of sets satisfying certain properties.

FunSearch was applied to two related problems, with additional results on the **corners problem** and **Shannon capacity of cycle graphs** in Supplementary Information Appendix B.

### 3.1 Cap Sets

#### Problem Definition

The **cap set problem** — once described by Terence Tao as "perhaps my favourite open question" — refers to the task of finding the largest possible set of vectors in $\mathbb{Z}_3^n$ (known as a cap set) such that no three vectors sum to zero. Geometrically, no three points of a cap set are in a line (see Fig. 3 for $n = 2$).

**Fig. 3 (described)**: Diagram of a cap set of size four in $\mathbb{Z}_3^2$. The circles are the elements of $\mathbb{Z}_3^2$ with the ones belonging to the cap set shown in blue. The possible lines in $\mathbb{Z}_3^2$ are also shown (with colours indicating lines that wrap around in arithmetic modulo 3). No three elements of the cap set are in a line.

**Why the problem is important**:
- Analogue of the classical number theory problem of finding large subsets of integers in which no three are in arithmetic progression
- Unlike many combinatorics problems, there is no consensus among mathematicians about the right answer
- Serves as a model for many other problems involving 'three-way interactions'
- Progress towards improved upper bounds immediately led to other combinatorial results (e.g., on the Erdős–Rado sunflower problem)

**Known facts**:
- The exact size of the largest possible cap set in $n$ dimensions is known only for $n \le 6$
- A brute force approach is not practical — search space is enormous (around 31,600 for $n = 8$)
- Previous methods imposed potentially suboptimal restrictions on the search space

#### FunSearch Approach

FunSearch searches the full space by means of an **algorithm skeleton** using a function `priority` : $\mathbb{Z}_3^n \to \mathbb{R}$. This function provides a priority with which each $x \in \mathbb{Z}_3^n$ should be included in the cap set.

The algorithm:
1. Start with an empty set
2. Iteratively add the vector $x \in \mathbb{Z}_3^n$ with the highest priority that does not violate the cap set constraint
3. Start from a trivial constant function, evolve the crucial 'priority' component

#### Results (Fig. 4a)

| Dimension $n$ | Best Known (prior) | FunSearch |
|---|---|---|
| 3 | 9 | 9 |
| 4 | 20 | 20 |
| 5 | 45 | 45 |
| 6 | 112 | 112 |
| 7 | 236 | 236 |
| **8** | **496** | **512** |

**Key result**: In dimension $n = 8$, FunSearch found a cap set of **size 512**, larger than the previously known best of 496. This is the first improvement in that dimension using a direct construction approach.

**Scalability**: FunSearch discovered a larger cap set from scratch, without being explicitly taught any way of combining cap sets. In contrast, the previously best-known construction relied on a complex combination of cap sets in lower dimensions.

#### Discovered Program and Interpretation (Fig. 4b, 4c)

FunSearch does not just discover the set of 512 eight-dimensional vectors, but a **program that generates it**. Through inspecting the code, researchers obtained a degree of understanding of what this set is.

**The discovered `priority` function** (Fig. 4b):

```python
def priority(el: tuple[int, ...], n: int) -> float:
    score = n
    in_el = 0
    el_count = el.count(0)
    if el_count == 0:
        score += n**2
        if el[1] == el[-1]:
            score *= 1.5
        if el[2] == el[-2]:
            score *= 1.5
        if el[3] == el[-3]:
            score *= 1.5
    else:
        if el[1] == el[-1]:
            score *= 0.5
        if el[2] == el[-2]:
            score *= 0.5
        for e in el:
            if e == 0:
                if in_el == 0:
                    score *= n * 0.5
                elif in_el == el_count - 1:
                    score *= 0.5
                else:
                    score *= n * 0.5 ** in_el
                in_el += 1
            else:
                score += 1
                if el[1] == el[-1]:
                    score *= 1.5
                if el[2] == el[-2]:
                    score *= 1.5
    return score
```

**Key insight**: The priority is affected by whether the same entry appears in positions $i$ and $-i$ (where $-i$ denotes the $i$th position counting from the end). This motivates the notion of **reflections**.

**Explicit construction** (Fig. 4c) — manually derived from the discovered program:

```python
def build_512_cap() -> list[tuple[int, ...]]:
    """Returns a cap set of size 512 in n=8 dimensions."""
    n = 8
    V = np.array(list(itertools.product(range(3), repeat=n)), dtype=np.int32)
    support = lambda v: tuple(i for i in range(n) if v[i] != 0)
    reflections = lambda v: sum(1 for i in range(1, n//2) if v[i] == v[-i])

    # Add all weight-8 vectors that have >= 2 reflections
    weight8_vectors = [v for v in V
        if np.count_nonzero(v) == 8  # Weight is 8
        and reflections(v) >= 2]     # At least 2 reflections

    # Add all weight-4 vectors that have specific support
    supports_16 = [(0, 1, 2, 3), (0, 1, 2, 5), (0, 3, 6, 7), (0, 5, 6, 7),
                   (1, 3, 4, 6), (1, 4, 5, 6), (2, 3, 4, 7), (2, 4, 5, 7)]
    weight4_vectors = [v for v in V
        if support(v) in supports_16]

    # Add all weight-4 vectors with specific support and 1 reflection
    supports_8 = [(0, 1, 2, 7), (0, 1, 2, 6), (0, 1, 3, 7), (0, 1, 6, 7),
                  (0, 1, 5, 7), (0, 2, 3, 6), (0, 2, 6, 7), (0, 2, 5, 6),
                  (1, 2, 4, 7), (1, 2, 4, 6), (1, 3, 4, 7), (1, 4, 6, 7),
                  (1, 4, 5, 7), (2, 3, 4, 6), (2, 4, 6, 7), (2, 4, 5, 6)]
    weight4_vectors_2 = [v for v in V
        if support(v) in supports_8
        and reflections(v) == 1]     # Exactly 1 reflection

    # Add weight-5 vectors with <= 1 reflections and one more condition
    allowed_zeros = [(0, 4, 7), (0, 2, 4), (0, 1, 4), (0, 4, 6),
                     (1, 2, 6), (2, 6, 7), (1, 2, 7), (1, 6, 7)]
    weight5_vectors = [
        v for v in V
        if tuple(i for i in range(n) if v[i] == 0) in allowed_zeros
        and reflections(v) <= 1      # At most 1 reflection
        and (v[1] * v[7]) % 3 != 1
        and (v[2] * v[6]) % 3 != 1]

    return weight8_vectors + weight4_vectors + weight4_vectors_2 + weight5_vectors
```

**Note**: Some properties of this construction are similar to the construction of the **Hill cap**, which results in the optimal 112-cap in $\mathbb{Z}_3^6$.

### 3.2 Admissible Sets and Asymptotic Bounds

#### Problem Definition

Beyond finding the size of the largest cap set $c_n$ in dimension $n$, a fundamental problem in additive combinatorics is determining the **cap set capacity**:

$$C = \sup_n c_n^{1/n}$$

The breakthrough result from Ellenberg & Gijswijt (2017) established an upper bound of $C \le 2.756$.

The framework of **constant weight admissible sets** (or simply admissible sets) establishes the current state-of-the-art for lower bounds.

**Definition**: Admissible sets $A(n, w)$ are collections of vectors in $\{0, 1, 2\}^n$ satisfying:
1. Each vector has the same number $w$ of non-zero elements but a unique support (therefore $|A(n, w)| \le \binom{n}{w}$)
2. For any three distinct vectors there is a coordinate in which their three respective values are $\{0, 1, 2\}$, $\{0, 0, 1\}$ or $\{0, 0, 2\}$

Informally, an admissible set describes how to combine cap sets in smaller dimensions into large cap sets in higher dimensions. Full-size admissible sets (with $|A(n, w)| = \binom{n}{w}$) are denoted $\mathcal{I}(n, w)$.

The previous state-of-the-art relied on SAT solvers to construct large admissible sets.

#### FunSearch Results on Admissible Sets (Fig. 5a)

FunSearch evolves a `priority` function used to iteratively grow admissible sets, starting from a trivial constant function.

| Lower bound on $C$ | Admissible set ingredient | Source |
|---|---|---|
| 2.2101 | $\mathcal{I}(90, 89)$ | Calderbank & Fishburn (1994) [Ref. 37] |
| 2.2173 | $\mathcal{I}(10, 5)$ | Edel (2004) [Ref. 34] |
| 2.2180 | $\mathcal{I}(11, 7)$ | Tyrrell (2023) [Ref. 38] |
| **2.2184** | **$\mathcal{I}(12, 7)$** | **FunSearch** |
| **2.2194** | **$\mathcal{I}(15, 10)$** | **FunSearch** |
| **2.2202** | **$A(24, 17)$ partial** | **FunSearch** |

**Key results**:
- FunSearch discovered an $\mathcal{I}(12, 7)$ admissible set, improving the lower bound from 2.2180 to **2.2184**
- By interpreting the code and exploiting a new symmetry, discovered $\mathcal{I}(15, 10)$ (bound: **2.2194**)
- Discovered a partial admissible set in $A(24, 17)$ of size 237,984, implying a lower bound of **2.2202**
- Although still far from the upper bound of 2.756, this represents the **largest improvement in 20 years**

**Note**: The partial set $A(24, 17)$ in trivial representation consists of more than 200,000 vectors, but the program generating it consists of only a few lines of code — illustrating FunSearch's ability to find compact representations.

#### The Discovered Priority Function for Admissible Sets (Fig. 5b)

```python
def priority(el: tuple[int, ...], n: int, w: int) -> float:
    score = 0.0
    for i in range(n):
        if el[i] == 1:
            score -= 0.9 ** (i % 4)
        if el[i] == 2:
            score -= 0.98 ** (30 - (i % 4))
        if el[i] == 1 and el[i - 4] == 1:
            score -= 0.98 ** (30 - (i % 4))
        if el[i] == 2 and el[i - 4] != 0:
            score -= 0.98 ** (30 - (i % 4))
        if el[i] == 2 and el[i - 4] == 1 and el[i - 8] == 2:
            score -= 0.98 ** (30 - (i % 4))
            score -= 6.3
        if el[i] == 2 and el[i - 4] == 2 and el[i - 8] == 1:
            score -= 0.98 ** (30 - (i % 4))
        if el[i] == 2 and el[i - 4] == 1 and el[i - 8] == 1:
            score -= 6.3
        if el[i] == 2 and el[i - 4] == 0 and el[i - 8] == 2:
            score -= 6.3
        if el[i] == 1 and el[i - 4] == 1 and el[i - 8] == 0:
            score -= 2.2
    return score
```

**Key insight from this code**: When $n = 12$, the function treats the four triples of coordinates $\{0, 4, 8\}$, $\{1, 5, 9\}$, $\{2, 6, 10\}$ and $\{3, 7, 11\}$ together (note the `i % 4` pattern). Researchers verified that the admissible set is in fact **symmetric under independent cyclic permutations of coordinates within each of these four triples**.

#### The Human-AI Feedback Loop

The procedure followed here is a concrete example of how LLM-based approaches can be used in mathematical sciences:
1. FunSearch suggests a solution
2. Researchers examine it and note features of interest (e.g., the symmetry)
3. These features are used to refine the search (searching directly for symmetric admissible sets)
4. Better solutions are found
5. Process can be iterated with both human and search consistently in the loop

**Symmetry exploitation**: By restricting to symmetric admissible sets (a more restricted but much smaller search space), FunSearch could search significantly higher dimensions and weights than were previously possible — leading to $\mathcal{I}(15, 10)$ and the $A(24, 17)$ construction.

---

## 4. Application 2: Online Bin Packing

### 4.1 Problem Definition

**Bin packing**: Pack a set of items of various sizes into the smallest number of fixed-sized bins. Applications: cutting materials, scheduling jobs on compute clusters.

**Online setting**: Pack each item as soon as it is received (as opposed to the offline setting which has access to all items in advance). Requires designing a heuristic for deciding which bin to assign an incoming item to.

### 4.2 Baseline Heuristics

**Classical heuristics**:
- **First Fit**: Places the incoming item in the first bin with enough available space
- **Best Fit**: Places the item in the bin with the least available space where the item still fits

While several variants exist with strong worst-case performance, they often show poor performance in practice.

### 4.3 FunSearch Approach

FunSearch defines a heuristic as a program that takes as input an item and an array of bins (containing the remaining capacity of each bin) and returns a priority score for each bin. The `solve` function picks the bin with the highest score according to the heuristic.

FunSearch is used to evolve this heuristic, **starting from best fit** as the initial program.

### 4.4 Datasets

**OR-Library benchmarks**: Four datasets OR1 to OR4, containing bin packing instances with an increasing number of items.

**Training**: Heuristic evolved on a training set of generated bin packing instances with the same number of items as those in OR1. After the evolutionary process, tested on OR1 to OR4.

**Weibull distribution**: Bin packing instances sampled from a Weibull distribution (closely follows many real-world scheduling problems).

**Performance metric**: Fraction of excess bins used over the L2 lower bound of the optimal offline packing solution (lower is better; this lower bound is generally not achievable in the online setting).

### 4.5 Results (Table 1)

| Dataset | First Fit | Best Fit | FunSearch |
|---|---|---|---|
| OR1 | 6.42% | 5.81% | **5.30%** |
| OR2 | 6.45% | 6.06% | **4.19%** |
| OR3 | 5.74% | 5.37% | **3.11%** |
| OR4 | 5.23% | 4.94% | **2.47%** |
| Weibull 5k | 4.23% | 3.98% | **0.68%** |
| Weibull 10k | 4.20% | 3.90% | **0.32%** |
| Weibull 100k | 4.00% | 3.79% | **0.03%** |

**Key observations**:
- FunSearch outperforms both First Fit and Best Fit across all datasets
- The learned heuristic **generalizes**: even though it only saw instances of the same size as OR1 during training, it generalizes across problem sizes
- The gap to Best Fit widens for larger instances
- On Weibull 100k (100,000 items), FunSearch is only **0.03% off the lower bound** on the optimum
- FunSearch is robust and consistently outperforms these baselines (confirmed by statistical analysis in Supplementary Information Appendix A.3)

### 4.6 Discovered Heuristic Strategy (Fig. 6)

Several heuristics discovered by FunSearch use the same general strategy. An example of a short discovered heuristic:

```python
def heuristic(item: float, bins: np.ndarray) -> np.ndarray:
    """Online bin packing heuristic discovered with FunSearch."""
    score = 1000 * np.ones(bins.shape)
    # Penalize bins with large capacities.
    score -= bins * (bins - item)
    # Extract index of bin with best fit.
    index = np.argmin(bins)
    # Scale score of best fit bin by item size.
    score[index] *= item
    # Penalize best fit bin if fit is not tight.
    score[index] -= (bins[index] - item)**4
    return score
```

**Comments were manually added** for clarity; they were not part of the original discovered code.

**Strategy**: Instead of always packing items into the bin with the least capacity (like best fit), the FunSearch heuristics assign items to the least capacity bin **only if the fit is very tight** after placing the item. Otherwise, the item is typically placed in another bin, which would leave more space after the item is placed. This **avoids leaving small gaps in bins** that are unlikely to ever be filled.

---

## 5. Methods

### 5.1 Implementation Details

#### Distributed System

Three types of workers communicate asynchronously:
1. **Programs database**: Stores the initial user-provided program, as well as all programs received from evaluators
2. **Samplers**: Perform LLM inference; repeatedly query the programs database for prompts; generate several samples from each prompt (for higher throughput)
3. **Evaluators**: Score programs by executing them on inputs of interest and assessing outputs using 'evaluate'; send correct programs to the programs database

Each of the three components is provided as both Python code and pseudocode (Supplementary Information Appendix F).

#### Prompt Building

- Samples $k$ programs (typically $k = 2$; see Supplementary Information Appendix E.1)
- Programs sorted by score in increasing order, starting from version 0 ('v0')
- See Extended Data Fig. 1 for an example of the prompt structure

#### Evolutionary Method and Program Selection

The island-based parallel genetic algorithm:
- Population split into $m$ separate islands
- Each island initialized with a copy of the user-provided initial program
- Evolved separately: when a prompt is required, first uniformly sample an island, then sample $k = 2$ programs from that island
- Programs generated from that prompt are stored in the same island
- **Every 4 hours**: discard all programs from the $m/2$ islands with the lowest best-instance scores
- Each discarded island is reseeded with a single program: choose one of the surviving $m/2$ islands uniformly at random and retrieve the highest-scoring program (breaking ties in favour of older programs)
- Evolutionary process restarts from this state (see Extended Data Fig. 2)

### 5.2 Robustness Analysis

Due to randomness in LLM sampling and evolutionary procedure, repeating an experiment can lead to different results:

- **Admissible sets**: Every single run of FunSearch surpasses the baseline, with only some variation in the magnitude. 60% of experiments on $\mathcal{I}(12, 7)$ find a full-size admissible set.
- **Cap set direct construction** ($n = 8$): Particularly challenging — only **4 out of 140 experiments** discovered a cap set of size 512.
- **Online bin packing**: Every run consistently outperforms both first fit and best fit.

Full statistical analysis in Supplementary Information Appendix A.3.

---

## 6. Analysis of Discovered Programs (Interpretability)

A unique feature of FunSearch — searching in function space — is the ability to inspect discovered code and infer new insights:

### Cap Set Problem
- The discovered `priority` function for $n = 8$ revealed that the priority is affected by whether the same entry appears in positions $i$ and $-i$ (reflections)
- This inspired manual simplification and derivation of an explicit, human-readable construction of the 512-cap

### Admissible Sets
- The discovered `priority` function for $\mathcal{I}(12, 7)$ revealed that coordinates are treated in groups using `i % 4`
- Researchers identified a new **symmetry**: the admissible set is preserved under independent cyclic permutations of coordinates within four disjoint groups of coordinate triples
- This symmetry was then exploited to search in a much smaller space, enabling discovery of larger admissible sets

### Bin Packing
- Multiple discovered heuristics share the same general strategy: assign to best-fit bin only if the fit is tight; otherwise use a bin that leaves more space
- This is a qualitatively different strategy from best fit, and provides insight into why it outperforms best fit

### Why Programs Are Interpretable

FunSearch implicitly encourages **concise programs** (by preferring shorter programs during sampling). This creates a Kolmogorov-compressed inductive bias:
- FunSearch attempts to find solutions that have low Kolmogorov complexity — the length of the shortest computer program that produces a given object as output
- Traditional search procedures have a very different inductive bias (directly searching for solutions)

Additional interpretability factors:
- LLMs (trained on human-produced code) tend to output code with similar traits to human code — including symmetry and parsimony
- This is in contrast to traditional genetic programming, which does not have this bias

---

## 7. Ablation Studies

Ablation studies are presented in Supplementary Information Appendix A, demonstrating the importance of each component.

Key components validated:
1. **Best-shot prompting vs. single program**: Two programs in prompt lead to better results than one, with diminishing returns beyond $k = 2$
2. **Skeleton vs. no skeleton**: Using a skeleton with isolated critical part significantly improves performance
3. **Island model vs. single population**: Island model improves exploration and avoids local optima
4. **LLM choice**: Results with StarCoder (open-source) compared to Codey — results not too sensitive to exact LLM choice as long as trained on sufficient code
5. **Distributed scaling**: Asynchronous parallel execution vs. sequential — substantial gains from parallelism
6. **FunSearch vs. SAT solvers**: FunSearch scales to much larger instances than traditional combinatorial solvers (Supplementary Information Appendix A.4)

---

## 8. Discussion

### Why FunSearch Works

The LLM used within FunSearch does not use much context about the problem. The LLM should instead be seen as a **source of diverse, syntactically correct programs with occasionally interesting ideas**. When constrained to operate on the crucial part of the algorithm with a program skeleton, the LLM provides suggestions that marginally improve over existing ones in the population.

Combined with the evolutionary algorithm, this ultimately results in discovering new knowledge on open problems.

### The Role of Searching in Function Space

Rather than directly searching for constructions (which is typically an enormous list of numbers), FunSearch searches for programs generating those constructions. Because most problems of interest are structured (highly non-random), solutions are described more concisely with a computer program.

- The trivial representation of $A(24, 17)$ consists of more than 200,000 vectors
- The program generating this set consists of only a few lines of code

This conciseness is key to FunSearch scaling up to large instances compared to traditional search approaches.

### Comparison to Genetic Programming

FunSearch vs. traditional genetic programming:
- Traditional GP requires defining the set of allowed mutation operations (primitives) — non-trivial, problem-specific, requires domain knowledge
- LLMs have been trained on vast amounts of code and have learned common patterns and routines
- The LLM can leverage context in the prompt to generate more effective suggestions than random ones in genetic programming
- FunSearch achieves cross-domain applicability (mathematics and algorithm design) without problem-specific tuning

### Comparison to Hyper-Heuristics

Hyper-heuristics seek to design learning methods for generating heuristics for combinatorial optimization problems, often using genetic programming. Like FunSearch, they have been applied to online bin packing:
- Previous hyper-heuristic approaches could match the performance of first fit and best fit
- Adding memory of previously seen items could even lead to heuristics outperforming best fit

**FunSearch advantage**: In GP and hyper-heuristics, components of the evolved heuristic must be manually defined by the user and tailored to a specific problem. The LLM in FunSearch bypasses this limitation.

### Limitations

FunSearch, at present, works best for problems having the following characteristics:
1. **Availability of an efficient evaluator**
2. **Rich scoring feedback** quantifying improvements (as opposed to a binary signal)
3. **Ability to provide a skeleton** with an isolated part to be evolved

**Examples of out-of-scope problems**:
- Generating proofs for theorems — unclear how to provide a rich enough scoring signal
- (Suitable example for FunSearch: MAX-SAT — the number of satisfied clauses can be used as a scoring signal)

### Future Outlook

- The rapid development of LLMs is likely to result in samples of far superior quality at a fraction of the cost, making FunSearch more effective at tackling a broad range of problems
- Automatically tailored algorithms will soon become common practice and deployed in real-world applications
- FunSearch explicitly strives for simplicity and can be further extended

---

## 9. Related Work

### LLMs in Program Synthesis

- LLMs have been used for debugging, solving code competitions, generating code from natural language descriptions, and improving code performance
- Related approaches to prompt building (combining several programs) were shown to perform well on different domains (Meyerson et al., 2023 — "language model crossover")
- LLMs combined with evaluators: refs. 20, 67 fine-tuned LLMs on data generated by the LLM itself, using an evaluator to ensure correctness

**Key distinction**: Unlike approaches that increase software engineer productivity, FunSearch combines the creativity of LLMs with evolutionary procedures to push the boundaries of human knowledge.

### LLM + Evolution

- Lehman et al. (2023): First showed that coupling LLM with a programmatic way of scoring a solution can lead to self-improvement loop; applied to code generating 2D virtual robots
- EvoPrompting (Chen et al., 2023), GPT-4 NAS, LLMatic: LLM as crossover operator for neural architecture search
- Voyager: Open-ended embodied agent with LLMs in Minecraft

**FunSearch distinction**: Tackles open problems in mathematics and algorithm design, surpassing human-designed constructions, using a distributed system with many asynchronous samplers/evaluators, user-provided skeleton, and island-based evolutionary mechanism — all with an off-the-shelf LLM without fine-tuning.

### Automatic Theorem Proving

LLMs have been used to guide the search for formal proofs (Polu & Sutskever, 2020; THOR, 2022). Although this has potential to find new knowledge, achievements still lag behind the frontier of human knowledge.

### Related Algorithms (AlphaTensor, AlphaDev)

Related work by the same group:
- AlphaTensor (Fawzi et al., 2022): Discovering faster matrix multiplication algorithms with reinforcement learning (Nature, 610, 47–53)
- AlphaDev (Mankowitz et al., 2023): Faster sorting algorithms discovered using deep reinforcement learning (Nature, 618, 257–263)

---

## 10. Key Figures Description

### Fig. 1 — Overview of FunSearch
A diagram showing the four main components of FunSearch: (1) Specification (problem definition and initial program), (2) Programs database (storing all correct programs found), (3) Pretrained LLM (generating new programs), and (4) Evaluation (scoring programs). Arrows show the cyclic flow: database feeds into prompt construction, prompt goes to LLM, LLM generates new program, program is evaluated, and correct ones go back to database.

### Fig. 2 — Examples of FunSearch Specifications
Two side-by-side code blocks:
- **(a) Cap set**: Shows `main`, `evaluate`, and `solve` functions, with `priority` as the function to evolve (initialized as `return 0.0`)
- **(b) Online bin packing**: Shows `main`, `evaluate`, and `solve` functions, with `heuristic` as the function to evolve (initialized as `return -(bins - item)`)

The `main` function connects the pieces: uses `solve` to produce a solution, then `evaluate` to score it.

### Fig. 3 — Cap Set in Z_3^2
A diagram of a cap set of size four in $\mathbb{Z}_3^2$. Elements of the cap set are shown in blue. Lines (including those that wrap around modulo 3) are shown in different colours. Illustrates the no-three-in-a-line property.

### Fig. 4 — FunSearch Results on Cap Set Problem
- **(a)** Table comparing best-known cap set sizes vs. FunSearch (showing the new 512 in dimension 8)
- **(b)** The discovered `priority` function code
- **(c)** The explicit construction of the 512-cap, derived by manual simplification of the discovered program, using the concept of reflections

### Fig. 5 — Results on Cap Set via Admissible Sets
- **(a)** Table of lower bounds on cap set capacity $C$, showing progression from 2.2101 to FunSearch's 2.2202
- **(b)** The discovered `priority` function for admissible sets, showing the `i % 4` pattern that revealed the symmetry

### Fig. 6 — Discovered Bin Packing Heuristic
A short Python heuristic function with manually added comments explaining the strategy: penalize bins with large capacities, penalize best-fit bin if fit is not tight, effectively avoiding leaving small gaps.

### Extended Data Fig. 1 — Best-Shot Prompting Example
An example showing how the prompt is constructed from $k = 2$ programs sampled from the database. Higher-scoring implementations are more likely to be included. Shows two `priority_v0` and `priority_v1` implementations followed by the header for `priority_v2` to be completed by the LLM.

### Extended Data Fig. 2 — Evolutionary Method (Island Model)
A diagram showing the island evolution process: initial programs separated into islands, each evolved separately. After a number of iterations, islands with the worst score are wiped and the best program from the best-score islands are placed in the empty islands. Process repeats until termination.

### Extended Data Fig. 3 — Program Clusters within Islands
Within each island, programs are grouped into clusters based on their signature (scores on several inputs). First, clusters are sampled favouring higher scores. Within the chosen cluster, a program is sampled favouring shorter programs. Sampled programs prompt the LLM to generate a new program, which — if correct — is added to the island in an existing or new cluster.

---

## 11. Additional Results (from Supplementary Information)

The paper mentions additional discoveries beyond the main results:

- **Corners problem**: Results in Supplementary Information Appendix B
- **Shannon capacity of cycle graphs**: Results in Supplementary Information Appendix B

Full discovered programs are available in Supplementary Information Appendix C.

---

## 12. Data and Code Availability

- **Data**: No external data corpus required other than the publicly available OR-Library bin packing benchmarks
- **Code**: Available at https://github.com/google-deepmind/funsearch
  - Discovered functions
  - Evolutionary algorithm
  - Code manipulation routines
  - Single-threaded implementation of FunSearch pipeline (Python)
- **Software library**: `launchpad` (distributed machine learning research framework) used for the distributed system
- **LLMs used**: Codey (available through Vertex AI API) and StarCoder (open source); no training or fine-tuning required — API access for inference is sufficient

---

## 13. References (Selected Key Citations)

1. Bang, Y. et al. A multitask, multilingual, multimodal evaluation of ChatGPT on reasoning, hallucination, and interactivity. arXiv:2302.04023 (2023).
2. Borji, A. A categorical archive of ChatGPT failures. arXiv:2302.03494 (2023).
3. Lehman, J. et al. in *Handbook of Evolutionary Machine Learning* 331–366 (Springer, 2023).
4. Chen, M. et al. Evaluating large language models trained on code (Codex). arXiv:2107.03374 (2021).
6. Li, R. et al. StarCoder: may the source be with you! arXiv:2305.06161 (2023).
16. Meyerson, E. et al. Language model crossover: variation through few-shot prompting. arXiv:2302.12170 (2023).
21. Grochow, J. New applications of the polynomial method: the cap set conjecture and beyond. *Bull. Am. Math. Soc.* 56, 29–64 (2019).
23. Beasley, J. E. OR-library: distributing test problems by electronic mail. *J. Oper. Res. Soc.* 41, 1069–1072 (1990).
24. Castiñeiras, I. et al. Weibull-based benchmarks for bin packing. *Proc. CP* 207–222 (Springer, 2012).
25. Anil, R. et al. PaLM 2 technical report. arXiv:2305.10403 (2023).
27. Tanese, R. Distributed Genetic Algorithms for Function Optimization. PhD thesis, Univ. Michigan (1989).
31. Ellenberg, J. S., Gijswijt, D. On large subsets of $\mathbb{F}_q^n$ with no three-term arithmetic progression. *Ann. Math.* 185, 339–343 (2017). [Upper bound $C \le 2.756$]
34. Edel, Y. Extensions of generalized product caps. *Des. Codes Cryptogr.* 31, 5–14 (2004).
35. Hill, R. On the largest size of cap in $S_{5,3}$. *Rend Lincei. Sci. Fis. Mat. Nat.* 54, 378–384 (1973).
37. Calderbank, A. R. & Fishburn, P. C. Maximal three-independent subsets of $\{0, 1, 2\}^n$. *Des. Codes Cryptogr.* 4, 203–211 (1994).
38. Tyrrell, F. New lower bounds for cap sets. *Discrete Analysis* (2023). [Previous best: $C \ge 2.2180$]
46. Martello, S. & Toth, P. Lower bounds and reduction procedures for the bin packing problem. *Discrete Appl. Math.* 28, 59–70 (1990). [L2 lower bound used for evaluation]
48. Chaitin, G. J. On the length of programs for computing finite binary sequences. *J. ACM* 13, 547–569 (1966). [Kolmogorov complexity]
55. Mouret, J.-B. & Doncieux, S. Overcoming the bootstrap problem in evolutionary robotics using behavioral diversity. *Proc. IEEE CEC* 1161–1168 (2009). [Quality diversity]
57. Helmuth, T., Spector, L. & Matheson, J. Solving uncompromising problems with lexicase selection. *IEEE Trans. Evol. Comput.* 19, 630–643 (2015).
89. Fawzi, A. et al. Discovering faster matrix multiplication algorithms with reinforcement learning. *Nature* 610, 47–53 (2022).
90. Mankowitz, D. J. et al. Faster sorting algorithms discovered using deep reinforcement learning. *Nature* 618, 257–263 (2023).
91. Yang, F. et al. Launchpad: a programming model for distributed machine learning research. arXiv:2106.04516 (2021).

---

## Summary of Key Contributions

| Contribution | Details |
|---|---|
| New method: FunSearch | Evolutionary LLM-based program search with evaluator verification |
| Cap set: $n=8$ | First cap set of size 512 (previous best: 496) |
| Admissible sets | New lower bound $C \ge 2.2202$ (previous: 2.2180 — best in 20 years) |
| New symmetry discovered | Admissible sets symmetric under cyclic permutations within groups of 4 triples |
| Bin packing: OR1–OR4 | FunSearch outperforms both First Fit and Best Fit across all instances |
| Bin packing: Weibull 100k | Only 0.03% excess over optimal lower bound with 100,000 items |
| Interpretability | Programs are readable and enabled human insight into new mathematical structures |
| Scalability | Searches for programs (compact) vs. explicit solutions (exponentially large) |
