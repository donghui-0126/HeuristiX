# ReasoningBank: Scaling Agent Self-Evolving with Reasoning Memory

**arXiv:** 2509.25140v2 [cs.AI] 16 Mar 2026
**Code:** https://github.com/google-research/reasoning-bank

---

## Authors and Affiliations

**Authors:**
Siru Ouyang¹*, Jun Yan²†, I-Hung Hsu², Yanfei Chen², Ke Jiang², Zifeng Wang², Rujun Han², Long T. Le², Samira Daruki², Xiangru Tang³, Vishy Tirumalashetty², George Lee², Mahsan Rofouei⁴, Hangfei Lin⁴, Jiawei Han¹, Chen-Yu Lee²†, and Tomas Pfister²

**Affiliations:**
- ¹ University of Illinois Urbana-Champaign (UIUC)
- ² Google Cloud AI Research
- ³ Yale University
- ⁴ Google Cloud AI

**Contact:** siruo2@illinois.edu, {junyann, chenyulee}@google.com
*Siru Ouyang's work was done during an internship at Google Cloud AI Research.*
†Corresponding authors.

---

## Abstract

With the growing adoption of large language model agents in persistent real-world roles, they naturally encounter continuous streams of tasks. A key limitation, however, is their **failure to learn from the accumulated interaction history**, forcing them to discard valuable insights and repeat past errors.

The paper proposes **ReasoningBank**, a novel memory framework that:
1. Distills **generalizable reasoning strategies** from an agent's self-judged successful and failed experiences.
2. At test time, the agent retrieves relevant memories from ReasoningBank to inform its interaction, then integrates new learnings back — enabling it to become more capable over time.

Building on this, the paper further introduces **Memory-aware Test-Time Scaling (MaTTS)**, which:
- Accelerates and diversifies the learning process by scaling up the agent's interaction experience.
- Allocates more compute to each task, generating abundant diverse experiences that provide rich **contrastive signals** for synthesizing higher-quality memory.
- Creates a synergy: better memory guides more effective scaling, while richer experiences forge even stronger memories.

**Experimental results** across web browsing (WebArena, Mind2Web) and software engineering (SWE-Bench-Verified):
- ReasoningBank outperforms baselines by **up to 20% relative improvement** in effectiveness.
- ReasoningBank reduces interactions by **up to 16% fewer steps** (efficiency).
- MaTTS further amplifies these gains.

The paper establishes **memory-driven experience scaling as a new scaling dimension**, enabling agents to self-evolve with emergent behaviors.

---

## 1. Introduction

### Motivation

The rapid advancement of LLMs has accelerated the development of interactive LLM agents crucial for complex real-world tasks requiring multi-turn interactions. These agents have demonstrated potential across:
- Web browsing (Gur et al., 2024)
- Computer use (Xie et al., 2024; Yang et al., 2024)
- Scientific discovery (Ghafarollahi and Buehler, 2025)

As agents are increasingly deployed in **persistent, long-running roles**, they encounter a continuous stream of tasks. However, a critical limitation persists: **they largely fail to learn from accumulated experience**.

By approaching each new task in isolation, agents are doomed to:
1. **Repeat similar errors** observed in the past (Yin et al., 2025)
2. **Discard valuable insights** gained from related problems
3. **Lack self-evolving capabilities** that would make the agent system more capable over time (Gao et al., 2026)

### Problem with Existing Memory Approaches

Recent efforts on agent memory have primarily focused on **storing past interactions for reuse** (Chen et al., 2025; Sun et al., 2025; Tang et al., 2025b; Zhao et al., 2024). However, these approaches are limited to:

- **Raw trajectories** (Kagaya et al., 2024; Kong et al., 2025; Zheng et al., 2024) — too lengthy and noisy, hard to reuse across tasks
- **Successful routines / workflows / procedures** only (Fang et al., 2025; Wang et al., 2025d) — ignore valuable lessons from failures

**Two fundamental drawbacks** of existing memory designs:
1. They **lack the ability to distill higher-level, transferable reasoning patterns**
2. By **over-emphasizing successful experiences**, they leave the valuable lessons from an agent's own failures largely underexplored

Consequently, existing memory designs often remain limited to **passive record-keeping** rather than providing actionable, generalizable guidance for future decisions.

### Solution: ReasoningBank

ReasoningBank bridges this gap by:
- Distilling and organizing memory items from **both successful and failed experiences**, judged by the agent itself (no ground-truth labels needed)
- Capturing **effective strategies from successes** AND **crucial preventative lessons from failures**
- Abstracting them into a collection of **actionable principles**

**Closed-loop operation:**
```
New task → Retrieve relevant memories from ReasoningBank → Agent acts
                                                             ↓
                          New experience is analyzed, distilled, consolidated back
                                         ↓
                              Agent continuously evolves and improves
```

### Memory-Aware Test-Time Scaling (MaTTS)

With ReasoningBank as a strong experience learner, the paper studies **experience scaling**:
- Instead of scaling through **breadth** (more tasks), focus on scaling through **depth** (more exploration per task)
- MaTTS in both **parallel** and **sequential** settings generates diverse exploration for contrastive signals
- Creates a **positive feedback loop**: high-quality memory → more effective scaling → richer experiences → stronger memories

This positions **memory-driven experience scaling as a new scaling dimension** for agents.

---

## 2. Key Contributions

1. **ReasoningBank** — A novel memory framework that distills generalizable reasoning strategies from both successful and failed experiences. Goes beyond prior work that stores raw trajectories or success-only routines.

2. **MaTTS (Memory-aware Test-Time Scaling)** — Establishes a powerful, bidirectional synergy between memory and test-time scaling, with memory-driven experience as a new scaling dimension.

3. **Extensive experiments** on WebArena, Mind2Web, and SWE-Bench-Verified demonstrating:
   - Up to **20% relative improvement** in effectiveness
   - Up to **16% fewer interactions** (efficiency)
   - Unique ability to **learn from failures** and enable **emergent reasoning strategies** over time

---

## 3. Related Work

### Memory for LLM Agents

Memory has emerged as an essential module in modern agent systems (He et al., 2026; Hu et al., 2025b; Zhang et al., 2025b). Existing memory systems organize and store information in various forms:
- **Plain text** (Packer et al., 2023)
- **Latent embeddings** (Wang et al., 2025b)
- **Structured graphs** (Chhikara et al., 2025; Li et al., 2025b; Xu et al., 2025)

Memory methods usually involve **retrieval mechanisms** (semantic search) with **memory management strategies** (updating) (Hu et al., 2025a; Tan et al., 2025).

Recent work also leverages **RL for memory management** in agent systems (Yu et al., 2025a; Zhou et al., 2025).

Most efforts emphasize:
- **Personalization** (Zhang et al., 2025a; Zhong et al., 2024)
- **Long-context management** (Hu et al., 2025c; Maharana et al., 2024; Wu et al., 2025)

The ReasoningBank paper falls in the research line of **learning from past experiences as memory** (Su et al., 2025; Zhao et al., 2024), critical for self-evolving agent systems (Gao et al., 2026; Liang et al., 2024).

**Key distinction from prior work:**
| Prior Work | Memory Type |
|---|---|
| Synapse (Zheng et al., 2024) | Reuses successful trajectories |
| AWM (Wang et al., 2025d) | Procedural workflows |
| EXPEL (Zhao et al., 2024) | Instance-level concepts |
| **ReasoningBank** | **High-level strategies and reasoning hints from both successes AND failures** |

### Agent Test-Time Scaling

Test-time scaling (TTS) (Snell et al., 2025) has demonstrated strong effectiveness in:
- Coding (Li et al., 2025a; Yu et al., 2025c)
- Math reasoning (Muennighoff et al., 2025)

Common TTS methods:
- **Best-of-N** (Chow et al., 2025)
- **Beam search** (Wu et al., 2024b)
- **Verifiers** (Setlur et al., 2025)

Application to **multi-turn interactive/agentic tasks remains underexplored**. Existing works scale:
- Search space for each action (Yu et al., 2025b)
- Number of agents in multi-agent systems (Jin et al., 2025)
- Number of environment interactions (Shen et al., 2025)

**Gap:** None of these efforts considers the role of **agent memory** in scaling. ReasoningBank extends this by introducing MaTTS, showing memory offers benefits beyond mere computational scaling.

---

## 4. Methodology

### 4.1 Problem Formulation

**Agent Configuration:**
- Agent policy: **π_L(·|M, A)** parameterized by backbone LLM **L**, conditioned on memory module **M** and action space **A**
- Sequential decision-making: transition function **T(s_{t+1}|s_t, a_t)** where s_t is state, a_t is action at time t
- **M = ReasoningBank**, initialized as empty
- For each task, agent generates trajectory of **(o_{0:t}, a_{0:t})** for t steps
- Action generation: **a_{t+1} ∈ A** via **π_L(o_{0:t}, a_{0:t}; M, A) → a_{t+1}**
- Memory contributes relevant memories as **additional system instruction** for π_L

**Observation representations:**
- Web browsing: text-based accessibility tree of web pages (using the thinking process of π_L as approximation due to length)
- SWE: code snippets

**Action spaces:**
- Web browsing: web navigation operations
- SWE: bash commands

**Test-Time Learning paradigm:**
- Task queries **Q = {q_1, q_2, ..., q_N}** arrive in a **streaming fashion** (each query revealed and completed sequentially)
- **No ground truth available** during test-time
- Agent must continually evolve using only its own past trajectories and self-verification without external labels

**Two key challenges:**
1. How to extract and preserve useful memory from past trajectories
2. How to effectively leverage such memory for future queries to avoid redundantly re-discovering successful strategies or repeating mistakes

---

### 4.2 ReasoningBank Framework

Past raw trajectories are often too **lengthy and noisy** to be directly applied. ReasoningBank distills useful strategies and reasoning hints from past experiences into **structured memory items**.

#### Memory Schema

Each memory item contains three components:

| Component | Description |
|---|---|
| **Title** | Concise identifier summarizing the core strategy or reasoning pattern |
| **Description** | Brief one-sentence summary of the memory item |
| **Content** | Distilled reasoning steps, decision rationales, or operational insights extracted from past experiences |

Memory items are both **human-interpretable** and **machine-usable**, facilitating efficient usage and integration with agents.

**Example memory item:**
```markdown
# Memory Item 5
## Title: Prioritize user account sections for personal data
## Description: When a query requests user-specific information, prioritize account sections.
## Content: Systematically look for and click on links like "My Account", navigate to "My Orders"
rather than "Recent Orders" to access complete history. Detect pagination mode and examine
all items in relevant orders. Avoid relying only on visible/recent data without checking completeness.
```

#### Three-Step Integration Process

```
┌─────────────────────────────────────────────────────────────────┐
│  Task q_i arrives                                               │
│        ↓                                                        │
│  (i) Memory Retrieval                                           │
│      - Query ReasoningBank with current query context           │
│      - Embedding-based similarity search (cosine distance)      │
│      - Retrieve top-k relevant memory items                     │
│      - Inject into agent's system instruction                   │
│        ↓                                                        │
│  Agent interacts with environment using retrieved memories      │
│        ↓                                                        │
│  (ii) Memory Extraction                                         │
│      - LLM-as-a-Judge labels trajectory outcome (Success/Fail)  │
│      - Extract memory items based on outcome type:              │
│        * Success → validated strategies                         │
│        * Failure → counterfactual signals, pitfalls, guardrails │
│      - Up to 3 memory items extracted per trajectory            │
│        ↓                                                        │
│  (iii) Memory Consolidation                                     │
│      - Append new items to ReasoningBank (simple addition)      │
│      - Evolving repository of memory items                      │
└─────────────────────────────────────────────────────────────────┘
```

#### Memory Retrieval Details
- Embedding model: **gemini-embedding-001** (Lee et al., 2025), accessed via Vertex AI
- Similarity search using **cosine distance** over the memory pool
- Default **k=1** most similar experience retrieved (ablation study available)
- Retrieved items concatenated into agent's system prompt

**Retrieval system instruction injected into agent:**
```
Below are some memory items that I accumulated from past interaction from the environment
that may be helpful to solve the task. You can use it when you feel it's relevant. In each step,
please first explicitly discuss if you want to use each memory item or not, and then take action.
```

#### Memory Extraction Prompts

**For successful trajectories:**
```
System: You are an expert in web navigation. You will be given a user query, the corresponding
trajectory that represents how an agent successfully accomplished the task.
## Guidelines
You need to extract and summarize useful insights in the format of memory items based on the
agent's successful trajectory.
The goal of summarized memory items is to be helpful and generalizable for future similar tasks.
## Important notes
- You must first think why the trajectory is successful, and then summarize the insights.
- You can extract at most 3 memory items from the trajectory.
- You must not repeat similar or overlapping items.
- Do not mention specific websites, queries, or string contents, but rather focus on
  generalizable insights.
## Output Format
# Memory Item i
## Title <the title of the memory item>
## Description <one sentence summary of the memory item>
## Content <1-3 sentences describing the insights learned>
```

**For failed trajectories:**
```
System: You are an expert in web navigation. You will be given a user query, the corresponding
trajectory that represents how an agent attempted to resolve the task but failed.
## Guidelines
You need to extract and summarize useful insights in the format of memory items based on the
agent's failed trajectory.
## Important notes
- You must first reflect and think why the trajectory failed, and then summarize what lessons
  you have learned or strategies to prevent the failure in the future.
- You can extract at most 3 memory items from the trajectory.
- Do not mention specific websites, queries, or string contents, but rather focus on
  generalizable insights.
```

#### LLM-as-a-Judge for Correctness Signals

The judge receives: user intent, trajectory, final webpage state, and bot response. It outputs a binary **Success** or **Failure** label.

**Judge prompt covers three task types:**
1. **Information seeking** — Bot response must contain requested information or explicitly state it's unavailable
2. **Site navigation** — Examine action history and final state to determine success
3. **Content modification** — Examine action history and final state

**Output format:**
```
Thoughts: <reasoning process>
Status: "success" or "failure"
```

**Backbone LLM**: Same as agent system (e.g., Gemini-2.5-flash → judge uses Gemini-2.5-flash)
**Temperature**: 0.0 (deterministic)

#### ReasoningBank Storage

```json
{
  "entry": {
    "task_query": "...",
    "trajectory": "...",
    "memory_items": [
      {"title": "...", "description": "...", "content": "..."},
      ...
    ]
  }
}
```
- Stored as **JSON format**
- Embeddings pre-computed for each query, stored in separate JSON for efficient similarity search
- Memory pool **persisted** for each independent run, enabling continual accumulation

#### Memory Consolidation

The current implementation uses a **minimal consolidation strategy**: newly generated items are directly appended without additional pruning, merging, or forgetting. This design choice deliberately avoids confounding factors from complex consolidation algorithms, isolating the contribution of ReasoningBank's content quality. More advanced consolidation mechanisms are left as future work.

---

### 4.3 MaTTS: Memory-Aware Test-Time Scaling

**Motivation:** ReasoningBank enables learning from experiences. Test-time scaling (TTS) generates abundant exploration histories. Combining them creates a powerful synergy.

**Problem with vanilla TTS:** Simply combining ReasoningBank with TTS (independently converting more trajectories to more memory items) is **suboptimal** because it does not leverage the **inherent contrastive signal** that arises from redundant exploration on the same problem.

**Three configurations compared:**

```
(a) Vanilla TTS (MaTTS w/o aggregation)
    Task q_i → Traj_1, Traj_2, ..., Traj_n
    Each trajectory → independent memory items (no cross-trajectory learning)

(b) MaTTS - Parallel Scaling
    Task q_i → Traj_1, Traj_2, ..., Traj_n
    ALL trajectories → Self-Contrast → Unified, higher-quality memory items

(c) MaTTS - Sequential Scaling
    Task q_i → Traj → Self-Refine → Traj' → Self-Refine → ...
    Intermediate refinement notes also used as memory signals
```

#### Parallel Scaling

- Generate **multiple trajectories** for the same query under guidance of retrieved memory items
- Apply **self-contrast** (Chen et al., 2020) across different trajectories
- Identify consistent reasoning patterns while filtering out spurious solutions
- Enables more **reliable memory curation** from multiple trials that promotes diverse exploration
- Extract up to **5 memory items** from all trajectories combined

**Parallel scaling prompt:**
```
System: You are an expert in web navigation. You will be given a user query and multiple
trajectories showing how an agent attempted the task. Some trajectories may be successful,
and others may have failed.
## Guidelines
Your goal is to compare and contrast these trajectories to identify the most useful and
generalizable strategies as memory items.
Use self-contrast reasoning:
- Identify patterns and strategies that consistently led to success.
- Identify mistakes or inefficiencies from failed trajectories and formulate preventative strategies.
- Prefer strategies that generalize beyond specific pages or exact wording.
## Important notes
- Think first: Why did some trajectories succeed while others failed?
- You can extract at most 5 memory items from all trajectories combined.
```

#### Sequential Scaling

- Iteratively refines reasoning within a single trajectory after initial completion
- Follows the principle of **self-refinement** (Madaan et al., 2023)
- **Intermediate notes** generated during self-refinement are also used as valuable memory signals
- Captures reasoning attempts, corrections, and insights not in the final solution

**Check instructions:**

*First-time check:*
```
Important: Let's carefully re-examine the previous trajectory, including your reasoning steps
and actions taken. Pay special attention to whether you used the correct elements on the page,
and whether your response addresses the user query. If you find inconsistencies, correct them.
If everything seems correct, confirm your final answer.
Output must stay in the same "<think>...</think><action></action>" format.
```

*Follow-up check:*
```
Let's check again.
Output must stay in the same "<think>...</think><action></action>" format.
```

#### Scaling Factor k

- **k** = number of trajectories (parallel) or refinement steps (sequential)
- **k=1** = no scaling baseline
- Both strategies become **memory-aware** with ReasoningBank

#### Best-of-N (BoN) Calculation

For parallel scaling evaluation, an LLM (same backbone as agent) selects the best trajectory from N candidates using a structured evaluation prompt covering:
1. **Progress toward goal** — how well the trajectory advances the task
2. **Trajectory efficiency** — significant progress in fewer steps rewarded
3. **Loop detection** — penalize real loops; identify real vs. benign repetitions
4. **Error severity and stability** — fatal/blocking errors receive major penalty
5. **Overall trajectory quality** — logical flow, clarity, coherence

**Output:** JSON with `{"index": [best_trajectory_index], "analysis": "...reasoning..."}`

---

## 5. Experiments

### 5.1 Setup

#### Benchmarks

| Benchmark | Description | # Instances | Domains/Settings |
|---|---|---|---|
| **WebArena** | General web navigation across diverse domains | 684 | Shopping (187), Admin (182), Gitlab (180), Reddit (106), Multi (29) |
| **Mind2Web** | Generalization of agents on versatile operations | 1341 | Cross-Task (252), Cross-Website (177), Cross-Domain (912) |
| **SWE-Bench-Verified** | Repository-level issue resolution | 500 | Software engineering |

*Note: Map domain excluded from WebArena due to website issues (following Miyai et al., 2025)*

#### Backbone LLMs

- **Gemini-2.5-Flash** (Comanici et al., 2025) — via Vertex AI
- **Gemini-2.5-Pro** (Comanici et al., 2025) — via Vertex AI
- **Claude-3.7-Sonnet** (Anthropic, 2025) — via Vertex AI

Agents implemented using **ReAct** (Yao et al., 2023) style, default decoding temperature **0.7**.

#### Baselines

| Baseline | Description |
|---|---|
| **No Memory** | Vanilla backbone LLM agent, no memory module |
| **Synapse** (Zheng et al., 2024) | Trajectory-as-exemplar: past trajectories as in-context memory |
| **AWM** (Wang et al., 2025d) | Agent Workflow Memory: abstracts common patterns from trajectories into reusable workflows |

**Fair comparison setup:** All baselines use the same Memory Retrieval and Memory Consolidation mechanisms. Only **Memory Extraction differs** — the only dimension where ReasoningBank differs from baselines.

#### Evaluation Metrics

**WebArena:**
- **SR (Success Rate ↑):** SR = (1/N) Σ isSuccess(q_i)
- **AS (Average Steps ↓):** AS = (1/N) Σ Steps(q_i); one step = one complete ReAct cycle (observe → think → act)
- Max step limit: **30** per query

**Mind2Web:**
- **EA (Element Accuracy ↑):** correct page element selected
- **AF1 (Action F1 ↑):** correct action on selected element
- **SSR (Step Success Rate ↑):** both element and action correct at current step
- **SR (Task-level Success Rate ↑):** all intermediate steps correct

**SWE-Bench-Verified:**
- **Resolution Rate:** percentage of issues fixed (patch passes all test scripts)
- **AS (Average Steps ↓)**

---

### 5.2 Main Results: ReasoningBank

#### Table 1: WebArena Results (SR ↑, Steps ↓)

| Model | Method | Shopping SR | Shopping Step | Admin SR | Admin Step | Gitlab SR | Gitlab Step | Reddit SR | Reddit Step | Multi SR | Multi Step | Overall SR | Overall Step |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Gemini-2.5-flash** | No Memory | 39.0 | 8.2 | 44.5 | 9.5 | 33.9 | 13.3 | 55.7 | 6.7 | 10.3 | 10.0 | 40.5 | 9.7 |
| | Synapse | 40.6 | 7.0 | 45.1 | 9.1 | 35.6 | 13.0 | 59.4 | 6.5 | 10.3 | 10.5 | 42.1 | 9.2 |
| | AWM | 44.4 | 7.0 | 46.7 | 8.8 | 37.2 | 13.2 | 62.3 | 6.1 | 3.4 | 7.7 | 44.1 | 9.0 |
| | **ReasoningBank** | **49.7** | **6.1** | **51.1** | **8.2** | **40.6** | **12.3** | **67.0** | **5.6** | **13.8** | **8.8** | **48.8** | **8.3** |
| | +MaTTS | 53.0 | 6.3 | 53.8 | 7.6 | 42.8 | 11.9 | 70.8 | 5.4 | 17.2 | 8.0 | 51.8 | 7.9 |
| **Gemini-2.5-pro** | No Memory | 45.5 | 7.6 | 51.1 | 8.7 | 35.0 | 11.6 | 71.7 | 6.0 | 6.9 | 8.8 | 46.7 | 8.8 |
| | Synapse | 46.5 | 6.6 | 52.2 | 8.9 | 38.3 | 11.3 | 68.9 | 5.9 | 6.9 | 9.0 | 47.7 | 8.5 |
| | AWM | 48.1 | 6.4 | 49.3 | 9.8 | 40.0 | 11.2 | 68.9 | 6.4 | 3.4 | 9.3 | 47.6 | 8.7 |
| | **ReasoningBank** | **51.9** | **6.0** | **56.6** | **7.7** | **44.4** | **9.8** | **80.2** | **5.1** | **13.8** | **8.2** | **53.9** | **7.4** |
| | +MaTTS | 54.0 | 5.9 | 58.2 | 7.4 | 46.7 | 9.1 | 83.0 | 5.3 | 20.7 | 7.2 | 56.3 | 7.1 |
| **Claude-3.7-sonnet** | No Memory | 38.5 | 6.1 | 49.5 | 8.4 | 36.7 | 10.6 | 53.8 | 5.5 | 0.0 | 11.6 | 41.7 | 8.0 |
| | Synapse | 39.6 | 5.8 | 50.5 | 8.5 | 38.0 | 10.0 | 53.8 | 6.1 | 0.0 | 11.8 | 42.6 | 7.9 |
| | AWM | 39.6 | 7.2 | 47.8 | 9.3 | 34.6 | 10.9 | 52.8 | 7.0 | 0.0 | 12.4 | 40.8 | 8.9 |
| | **ReasoningBank** | **44.9** | **5.6** | **53.3** | **7.6** | **41.1** | **9.5** | **57.5** | **5.2** | **3.4** | **10.5** | **46.3** | **7.3** |
| | +MaTTS | 47.1 | 5.8 | 55.5 | 7.4 | 43.3 | 9.4 | 60.4 | 5.0 | 10.3 | 9.1 | 48.8 | 7.2 |

**Overall SR improvements over No Memory baseline:**
- Gemini-2.5-flash: **+8.3** (40.5 → 48.8)
- Gemini-2.5-pro: **+7.2** (46.7 → 53.9)
- Claude-3.7-sonnet: **+4.6** (41.7 → 46.3)

#### Table 2: SWE-Bench-Verified Results

| Model | Method | Resolve Rate ↑ | Avg Steps ↓ |
|---|---|---|---|
| **Gemini-2.5-flash** | No Memory | 34.2 | 30.3 |
| | Synapse | 35.4 | 30.7 |
| | **ReasoningBank** | **38.8** | **27.5** |
| **Gemini-2.5-pro** | No Memory | 54.0 | 21.1 |
| | Synapse | 53.4 | 21.0 |
| | **ReasoningBank** | **57.4** | **19.8** |

*Note: AWM excluded from SWE-Bench because the open-ended bash action space makes it difficult to extract the fixed workflows AWM requires.*

Step savings over No Memory: **2.8 steps** (flash), **1.3 steps** (pro)

#### Table 3: Mind2Web Results

| Model | Method | Cross-Task EA | Cross-Task AF1 | Cross-Task SSR | Cross-Task SR | Cross-Website EA | Cross-Website AF1 | Cross-Website SSR | Cross-Website SR | Cross-Domain EA | Cross-Domain AF1 | Cross-Domain SSR | Cross-Domain SR |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Gemini-2.5-flash** | No Memory | 46.0 | 59.1 | 40.3 | 3.3 | 39.8 | 45.1 | 31.7 | 1.7 | 35.8 | 37.9 | 31.9 | 1.0 |
| | Synapse | 47.0 | 59.5 | 41.2 | 3.5 | 40.3 | 46.0 | 32.1 | 1.9 | 36.3 | 38.5 | 32.4 | 1.1 |
| | AWM | 46.3 | 56.1 | 41.0 | 3.5 | 39.1 | 42.2 | 31.7 | 2.1 | 33.3 | 36.5 | 30.1 | 0.7 |
| | **ReasoningBank** | **52.1** | **60.4** | **44.9** | **4.8** | **44.3** | **52.6** | **33.9** | **2.3** | **40.6** | **41.3** | **36.6** | **1.6** |
| **Gemini-2.5-pro** | No Memory | 49.3 | 60.2 | 44.4 | 3.5 | 41.2 | 49.8 | 34.8 | 3.4 | 37.9 | 37.7 | 35.0 | 1.4 |
| | Synapse | 50.1 | 61.0 | 44.7 | 3.6 | 41.8 | 51.2 | 35.0 | 3.2 | 38.5 | 39.8 | 35.6 | 1.5 |
| | AWM | 48.6 | 61.2 | 44.4 | 3.7 | 41.9 | 47.9 | 34.8 | 2.3 | 37.3 | 38.1 | 34.4 | 1.2 |
| | **ReasoningBank** | **53.6** | **62.7** | **45.6** | **5.1** | **46.1** | **54.8** | **36.9** | **3.8** | **42.8** | **45.2** | **38.1** | **1.7** |

**Key observation:** Gains are especially pronounced in **cross-domain** setting, which requires the highest level of generalization. AWM actually degrades in cross-domain (0.7 vs baseline 1.0 for flash), while ReasoningBank improves consistently.

---

### 5.3 Key Findings on ReasoningBank

#### Finding 1: Consistent Outperformance Across LLM Backbones

ReasoningBank improves across Gemini-2.5-flash, Gemini-2.5-pro, and Claude-3.7-sonnet on all datasets. This is notable because AWM sometimes **degrades** (e.g., Multi subset: 3.4 vs. 10.3 baseline with flash).

#### Finding 2: Superior Generalization

On WebArena Multi subset (requires transferring memory across multiple websites):
- ReasoningBank: +4.6 SR over strongest baseline (averaged)
- AWM: fails to provide gains, even degrades

On Mind2Web cross-domain (highest generalization demand): consistently better across all metrics.

#### Finding 3: Efficiency Gains

WebArena step reductions vs. "No Memory" (up to 1.4 steps) and vs. other memory baselines (up to 1.6 steps).

SWE-Bench: saves 2.8 steps (flash) and 1.3 steps (pro).

---

### 5.4 MaTTS Results

Detailed study on WebArena-Shopping with Gemini-2.5-flash, scaling factor k = 1 to 5.

#### Parallel Scaling Results

| k | MaTTS w/o memory | MaTTS w/o aggregation (Vanilla TTS) | MaTTS |
|---|---|---|---|
| 1 | 39.0 | 49.7 | 49.7 |
| 2 | 40.6 | 51.3 | 52.9 |
| 3 | 39.4 | 52.4 | 52.4 |
| 4 | 42.2 | 54.0 | 54.0 |
| 5 | 41.7 | 52.4 | **55.1** |

#### Sequential Scaling Results

| k | MaTTS w/o memory | MaTTS w/o aggregation (Vanilla TTS) | MaTTS |
|---|---|---|---|
| 1 | 39.0 | 49.7 | 49.7 |
| 2 | 40.1 | 50.8 | 51.9 |
| 3 | 38.5 | 51.9 | 53.5 |
| 4 | 37.4 | 52.4 | 54.0 |
| 5 | 40.6 | 51.9 | **54.5** |

**Key observations:**

1. **Both parallel and sequential boost performance**: k=5 parallel: 39.0 → 55.1 (MaTTS); k=5 sequential: 39.0 → 54.5 (MaTTS)

2. **MaTTS consistently beats vanilla TTS**: At k=5, MaTTS achieves 55.1 vs. 52.4 (parallel) and 54.5 vs. 51.9 (sequential)

3. **Without memory, scaling gains are smaller and less consistent**: MaTTS w/o memory fluctuates between 37.4–42.2 (parallel) and 37.4–40.6 (sequential)

4. **Sequential vs. Parallel trade-off**:
   - Sequential shows short-term advantage at small k (higher initial gains from self-correction)
   - But saturates quickly — once model succeeds or fails decisively, further refinements add little
   - Parallel scaling continues to provide diverse rollouts at larger k, surpassing sequential at k=5 (55.1 vs. 54.5)
   - Without memory, sequential scaling yields little/no benefit; parallel consistently dominates

---

### 5.5 Synergy Between Memory and Test-Time Scaling

Snapshot at k=5, parallel scaling on WebArena-Shopping:

| Memory Method | No Scaling (Pass@1) | Pass@1 w/ Scaling | Best-of-5 (BoN) |
|---|---|---|---|
| No Memory | 39.0 | 39.0 | 42.2 |
| Synapse | 40.6 | 41.2 | 44.4 |
| AWM | 44.4 | 45.5 | 47.6 |
| **ReasoningBank** | **49.7** | **53.0** | **55.1** |

**Two-directional synergy:**

**Direction 1: Better memory → stronger scaling (BoN)**
- Without memory: BoN 39.0 → 42.2 (small gain)
- Synapse: 40.6 → 44.4
- AWM: 44.4 → 47.6
- ReasoningBank: 49.7 → 55.1 (largest gain)

High-quality memory directs scaling toward more promising rollouts, ensuring additional trajectories convert to higher success rates.

**Direction 2: Scaling → better memory curation (Pass@1)**
- Without good memory: Synapse Pass@1 barely improves (40.6 → 41.2); AWM improves slightly (44.4 → 45.5)
- ReasoningBank: Pass@1 rises from 49.7 to 53.0

Scaling alone is insufficient — only when paired with good memory does it contribute to more effective memory curation, closing the **virtuous cycle**.

---

## 6. Analysis

### 6.1 Failure Trajectory Analysis

Ablation on WebArena-Shopping with Gemini-2.5-flash:

| Method | Success Only | With Failures |
|---|---|---|
| No Memory (baseline) | 39.0 | 39.0 |
| Synapse | 40.6 | 41.7 (+1.1) |
| AWM | 44.4 | 42.2 (−2.2, degrades!) |
| **ReasoningBank** | **46.5** | **49.7 (+3.2)** |

**Key finding:** Baseline methods (Synapse, AWM) build memory solely from successful trajectories and cannot effectively benefit from failures. Adding failures to AWM actually **degrades** performance (-2.2).

ReasoningBank uniquely transforms failures into **constructive signals** rather than noise, achieving +3.2 improvement by incorporating failure trajectories.

This highlights that failure signals are valuable **only when** the memory extraction design can properly distill lessons from them.

### 6.2 Emergent Behaviors

ReasoningBank strategies are **not flat or monolithic** — they evolve over time, exhibiting emergent behaviors resembling RL learning dynamics (Wang et al., 2025a).

**Case study: "User-Specific Information Navigation" strategy evolution:**

| Stage | Strategy Type | Example |
|---|---|---|
| **Early** | Procedural/execution | "actively look for and click on 'Next Page', 'Page X', or 'Load More' links" |
| **Mid-early** | Atomic self-reflection | "it's crucial to first re-check the element's current identifier before acting" |
| **Mid-late** | Generalized complex strategy | "Before scanning, always leverage any available search or filter functionalities, ensure completeness before reporting" |
| **Late** | Evolved adaptive check | "Regularly cross-referencing the current view with the task requirements; if contents are incorrect or irrelevant, reassess available options such as search filters, alternative sections" |

**Evolution path:**
1. Simple action rules (execution-oriented)
2. Adaptive self-reflections (reduce simple mistakes)
3. Systematic completeness checks (leverage search/filters)
4. Compositional strategies (cross-referencing + reassessing options)

This demonstrates ReasoningBank enables refinement from **low-level actions to high-level reasoning** during test-time learning.

### 6.3 Robustness to LLM-as-a-Judge Accuracy

Study on WebArena-Shopping with Gemini-2.5-flash, simulating different judge accuracy levels.

**Baseline judge accuracy:** 72.7% (compared against ground-truth labels)

| Simulated Judge Accuracy | SR |
|---|---|
| 50% (random guess) | ~47.6 |
| 60% | ~47.6 |
| 70% | ~49.7 |
| 80% | ~48.7 |
| 90% | ~49.7 |
| 100% (ground truth) | ~52.4 |

**Finding:** Judge accuracy does not significantly impact ReasoningBank performance within the 70%-90% accuracy range. The 100% setting yields best performance, but all variants with >50% accuracy achieve similar results. ReasoningBank is **robust to noise in the verification step**.

### 6.4 Targeted Efficiency Gains (Successful vs. Failed Cases)

Table 4: Average steps separated by successful vs. failed instances:

| Model | Shopping Succ | Shopping Fail | Admin Succ | Admin Fail | Gitlab Succ | Gitlab Fail | Reddit Succ | Reddit Fail |
|---|---|---|---|---|---|---|---|---|
| No Memory | 6.8 | 8.7 | 8.4 | 10.4 | 8.6 | 15.7 | 6.1 | 7.6 |
| **ReasoningBank** | **4.7 ↓2.1** | **7.3 ↓1.4** | **7.0 ↓1.4** | **9.5 ↓0.9** | **7.6 ↓1.0** | **15.5 ↓0.2** | **5.0 ↓1.1** | **6.8 ↓0.8** |

**Key finding:** Step reductions are **larger on successful cases** than failed ones. For Shopping: successful cases save 2.1 steps (26.9% relative reduction) vs. 1.4 steps for failed cases.

This indicates ReasoningBank primarily helps the agent **reach solutions more efficiently** (following effective reasoning paths) rather than simply truncating failed trajectories.

### 6.5 Number of Retrieved Experiences

Ablation on WebArena-Shopping with Gemini-2.5-flash:

| # Retrieved Experiences | SR |
|---|---|
| 0 (no memory) | 39.0 |
| **1 (default)** | **49.7** |
| 2 | 46.0 |
| 3 | 45.5 |
| 4 | 44.4 |

**Finding:** Incorporating even one relevant memory significantly boosts performance (+10.7 SR). However, more experiences leads to gradual decline, suggesting excessive memories may introduce conflicts or noise. **Relevance and quality** are more crucial than quantity.

### 6.6 Inference Cost Analysis

Token consumption breakdown per trajectory on WebArena-Shopping (Gemini-2.5-flash):

| Method | Action Generation | LLM-as-a-Judge | Memory Extraction | Total |
|---|---|---|---|---|
| No Memory | 50,847 | — | — | 50,847 |
| Synapse | 55,921 | 2,594 | — | 58,515 |
| AWM | 53,820 | 2,479 | 3,074 | 59,373 |
| **ReasoningBank** | **49,306** | **2,186** | **1,562** | **53,055** |

**Cost-effectiveness:** Compared to No Memory, ReasoningBank increases total token consumption by only **~4.3%** while boosting performance by **~20.5%**.

Synapse and AWM greatly increase computation overhead (15.1% and 16.8% more tokens) while achieving less performance gains.

Notably, ReasoningBank's **action generation tokens are lower** (49,306 vs. 50,847 for No Memory), consistent with efficiency gains — fewer steps means fewer tokens for interaction.

### 6.7 Pass@k Analysis

Under parallel scaling on WebArena-Shopping with Gemini-2.5-flash:

| k | MaTTS w/o memory | MaTTS w/o aggregation | **MaTTS** |
|---|---|---|---|
| 1 | 39.0 | 49.7 | 49.7 |
| 2 | 47.6 | 50.8 | 51.3 |
| 3 | 49.7 | 51.9 | 52.9 |
| 4 | 51.3 | 52.4 | 55.1 (sic: 54.5?) |
| 5 | 52.4 | 52.4 | **62.1** |

**Finding:** MaTTS not only preserves efficiency at small k (51.3 at k=2) but sustains strong growth with scaling, reaching **62.1 at k=5** — compared to only 52.4 for MaTTS w/o memory. This demonstrates that MaTTS unlocks more potential and encourages diversified generation.

### 6.8 Results with Smaller Open-Source LLMs

Table 6: WebArena-Shopping with Gemma-3-12B-Instruct:

| Method | Success Rate (%) | Average Steps |
|---|---|---|
| No Memory | 17.1 | 13.7 |
| Synapse | 16.0 | 14.0 |
| AWM | 21.4 | 12.5 |
| **ReasoningBank** | **24.1** | **11.8** |

**Finding:** ReasoningBank continues to provide consistent performance gains even on compact open-source models. Benefits are **not limited to proprietary frontier models**.

---

## 7. Case Studies

### Case Study 1: Effectiveness

**Task:** "What is the date when I made my first purchase on this site?"

**Baseline (No Memory):**
- Start → click 'My Account' → View 'Recent Orders' table
- Incorrectly outputs most recent purchase date: "Your first purchase was made on 3/11/23."
- **WRONG** — only checked "Recent Orders"

**ReasoningBank:**
- Start → click 'My Account' → "I will use memory item 5" → View full 'My Orders' table → Next Page
- Correctly outputs: "Your first purchase was made on March 2, 2022."
- **CORRECT** — memory guided it to explore complete history

### Case Study 2: Efficiency

**Task:** "Buy the best rating product from 'Men's shoe' category with at least 5 reviews and the product is least expensive"

**Baseline (No Memory):**
- Inefficient search navigation consuming 8 steps just to find "Men" category
- Cannot filter by "Men", needs to scroll down
- **29 steps total**

**ReasoningBank:**
- "According to Memory Item 11, to correctly navigate to certain categories, I need to first filter products..."
- Hover (Shoes) → Hover (Men) → Select Price → Identify product with ≥5 reviews → Proceed to checkout
- **10 steps total** (3x more efficient!)

### Case Study 3: Reflection on Failures

**Task:** "Provide me with the complete names of Bluetooth headphones from Sony, and also share the price range for the available models."

**Original (failed) trajectory:**
- Imprecise search query → too many items returned → irrelevant objects
- Agent spends endless steps on 'page next', exhausting interaction limits

**ReasoningBank diagnosis:**
- "The agent spent endless steps on 'page next', which exhausts the interaction limits without providing the requested information"

**Distilled strategies:**
1. "Search query optimization" — be more precise, avoid irrelevance
2. "Adjust number of items displayed per page" — accelerate scanning
3. "Use available filters" — narrow results before browsing

These distilled strategies prevent similar future failures, enabling **emergent improvement**.

---

## 8. Appendix Details

### A.1 Prompt Templates

Full prompts for:
- **Success extraction** (3 memory items max, generalize insights, no specific website mentions)
- **Failure extraction** (3 memory items max, reflect on why failed, derive preventative lessons)
- **LLM-as-a-Judge** (binary success/failure, covers 3 task types)
- **Parallel scaling self-contrast** (5 memory items max across all trajectories)
- **Sequential scaling check** (first-time check and follow-up check instructions)
- **Best-of-N selection** (evaluation criteria: progress, efficiency, loop detection, error severity, quality)

### A.2 Implementation Parameters

| Parameter | Value |
|---|---|
| Memory extractor backbone | Same as agent (e.g., Gemini-2.5-flash) |
| Extractor temperature | 1.0 |
| Judge backbone | Same as agent |
| Judge temperature | 0.0 (deterministic) |
| Max memory items per trajectory | 3 |
| Embedding model | gemini-embedding-001 (Vertex AI) |
| Default retrieved memories (k) | 1 |
| ReAct max steps | 30 |
| Agent generation temperature | 0.7 |
| Storage format | JSON |

### A.3 SWE-Bench Implementation

- Follows **mini-SWE-Agent** setting (Yang et al., 2024)
- **Bash-Only** environment, no special scaffold structure
- Simple ReAct agent loop
- AWM excluded (open-ended bash action space incompatible with workflow extraction)

---

## 9. Discussion and Limitations

### 9.1 Limitations

**1. Focus on memory content**
The paper emphasizes how to curate and utilize memory content (integrating failure trajectories, constructing distilled reasoning cues). It does not extensively compare with other memory architectures (episodic, hierarchical memory) — these address orthogonal concerns about memory form/structure.

**2. Simplicity in retrieval and consolidation**
Intentional design choice to use simple embedding-based retrieval and straightforward consolidation to isolate the effect of content quality. More sophisticated strategies (adaptive retrieval, hierarchical consolidation) would be compatible but were not the focus.

**3. Dependence on LLM-as-a-judge**
Success/failure signals determined by LLM-as-a-judge. May introduce noise when tasks are ambiguous or when the judge model errs. Framework is shown to be robust to this noise (see Section 6.3), but stronger verifiers (human-in-loop, ensemble judgment) could further enhance reliability.

### 9.2 Future Directions

**1. Modular and Compositional Memory**
Current framework distills each experience into multiple items and retrieves all associated items independently. Future work could explore:
- **Composition-aware retrieval** — combine complementary items
- **Modular memory extraction** — extract by category: "planning memory", "tool-use memory", "operational memory", "user-centric memory"
- **Reusable macros** — form higher-level strategy macros from combinations
- This would enable richer strategies and stronger generalization in long-horizon tasks

**2. Advanced Memory Architectures**
Build a layered, product-level memory stack integrating:
- **Episodic traces** (Fountas et al., 2025) — per-task context
- **Short-term "working" memory** (Lumer et al., 2025) — within-session state
- **Long-term consolidated knowledge** (Wang et al., 2025b) — with decay/refresh policies
- Memory retrieval beyond embedding-based similarity to **reasoning-intensive controllers** (Shao et al., 2025) with multi-hop lookups
- Learning-based routers and consolidation policies

This would turn ReasoningBank + MaTTS into a deployable memory service that scales across domains and teams.

---

## 10. Key Figures Summary

| Figure | Description |
|---|---|
| **Figure 1** | ReasoningBank vs. Trajectory/Workflow memory: cumulative success rates on WebArena-Admin, showing continuous evolution vs. flat No Memory baseline |
| **Figure 2** | Overview of ReasoningBank: three-step closed loop (retrieval → agent acts → extraction → consolidation) with LLM-as-a-Judge |
| **Figure 3** | Comparison of (a) Vanilla TTS vs. (b) MaTTS-Parallel (self-contrast) vs. (c) MaTTS-Sequential (self-refinement) |
| **Figure 4** | Scaling factor k effect: parallel vs. sequential scaling, comparing MaTTS / MaTTS w/o aggregation / MaTTS w/o memory |
| **Figure 5** | Memory-scaling synergy snapshot at k=5: Pass@1 vs. Best-of-5 for all memory methods |
| **Figure 6** | Emergent behaviors case study: evolution of "User-Specific Information Navigation" memory item over time |
| **Figure 7** | Ablation: success-only vs. with-failure memory induction for Synapse, AWM, ReasoningBank |
| **Figure 8** | Robustness to LLM-as-a-judge accuracy: SR vs. simulated accuracy (50%–100%) |
| **Figure 9** | Prompt templates for memory extraction (success vs. failure trajectories) |
| **Figure 10** | LLM-as-a-Judge system instructions for binary success/failure classification |
| **Figure 11** | MaTTS system instructions: parallel (self-contrast) and sequential (re-check) prompts |
| **Figure 12** | Best-of-N selection prompt with evaluation criteria |
| **Figure 13** | Ablation: number of retrieved experiences (0–4) vs. SR |
| **Figure 14** | Pass@k analysis under parallel scaling |
| **Figure 15** | Effectiveness case study: first purchase date task (baseline vs. ReasoningBank) |
| **Figure 16** | Efficiency case study: Men's shoe task (29 steps vs. 10 steps) |
| **Figure 17** | Failure reflection case study: Sony Bluetooth headphones task |

---

## 11. Conclusion

ReasoningBank introduces a memory framework that distills **strategy-level reasoning signals from both successes and failures** and integrates them into test-time scaling (MaTTS). Key findings:

1. **Consistent performance improvement** across web browsing and software engineering benchmarks, multiple LLM backbones, and generalization settings
2. **Efficiency gains** — reduces redundant exploration, especially on successful cases (up to 26.9% fewer steps)
3. **Strong synergy** between memory and test-time scaling — bidirectional positive feedback loop
4. **Emergent behaviors** — strategies evolve from simple action rules to complex compositional reasoning over time
5. **Learning from failures** is uniquely effective — unlike baselines that either cannot or are degraded by failure signals
6. **Cost-effective** — only 4.3% token overhead for ~20.5% performance boost

These findings suggest a practical pathway toward **adaptive and lifelong-learning agents**, establishing memory-driven experience scaling as a new scaling dimension.

---

## References (Key)

- **Synapse** (Zheng et al., 2024) — Trajectory-as-exemplar prompting with memory for computer control. ICLR 2024.
- **AWM** (Wang et al., 2025d) — Agent Workflow Memory. ICML 2025.
- **WebArena** (Zhou et al., 2024) — A realistic web environment for building autonomous agents. ICLR 2024.
- **Mind2Web** (Deng et al., 2023) — Towards a generalist agent for the web. NeurIPS 2023.
- **SWE-Bench** (Jimenez et al., 2024) — Can language models resolve real-world GitHub issues? ICLR 2024.
- **EXPEL** (Zhao et al., 2024) — LLM agents are experiential learners. AAAI 2024.
- **Self-Refine** (Madaan et al., 2023) — Iterative refinement with self-feedback. NeurIPS 2023.
- **ReAct** (Yao et al., 2023) — Synergizing reasoning and acting in language models. ICLR 2023.
- **TTS** (Snell et al., 2025) — Scaling LLM test-time compute optimally can be more effective than scaling parameters. ICLR 2025.
- **Gemini-2.5** (Comanici et al., 2025) — arXiv:2507.06261
- **Claude-3.7** (Anthropic, 2025) — https://www.anthropic.com/news/claude-3-7-sonnet
- **BrowserGym** (de Chezelles et al., 2025) — The BrowserGym ecosystem for web agent research. TMLR 2025.
- **Self-evolving agents survey** (Gao et al., 2026) — A survey of self-evolving agents. TMLR 2026.
- **LLM-as-a-Judge survey** (Gu et al., 2024) — A survey on LLM-as-a-judge. arXiv:2411.15594.
