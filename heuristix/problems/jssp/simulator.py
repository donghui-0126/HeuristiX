"""JSSP simulator — parse Taillard format, build schedule, compute metrics.

This is the evaluation backbone. The simulator:
1. Parses a Taillard-format instance into structured data.
2. Accepts a dispatching-rule heuristic function.
3. Greedily builds a schedule by repeatedly asking the heuristic which
   operation to dispatch next.
4. Returns the completed schedule and metrics.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable


# ── Data Structures ─────────────────────────────────────────────


@dataclass
class Operation:
    """A single operation within a job."""

    job: int
    op_idx: int  # position within the job (0-based)
    machine: int
    duration: int


@dataclass
class JSSPInstance:
    """A parsed JSSP instance."""

    n_jobs: int
    n_machines: int
    jobs: list[list[Operation]]  # jobs[job_idx][op_idx] = Operation

    @property
    def total_operations(self) -> int:
        return sum(len(job) for job in self.jobs)


@dataclass
class ScheduledOp:
    """An operation placed on the timeline."""

    job: int
    op_idx: int
    machine: int
    start: float
    end: float


# ── Parsing ─────────────────────────────────────────────────────


def parse_instance(text: str) -> JSSPInstance:
    """Parse Taillard-format text into a JSSPInstance.

    Format:
        n_jobs  n_machines
        machine_0 time_0  machine_1 time_1  ...  (for job 0)
        machine_0 time_0  machine_1 time_1  ...  (for job 1)
        ...
    """
    lines = [line.strip() for line in text.strip().split("\n") if line.strip()]

    header = lines[0].split()
    n_jobs = int(header[0])
    n_machines = int(header[1])

    jobs: list[list[Operation]] = []
    for job_idx in range(n_jobs):
        tokens = lines[1 + job_idx].split()
        ops: list[Operation] = []
        for op_idx in range(n_machines):
            machine = int(tokens[2 * op_idx])
            duration = int(tokens[2 * op_idx + 1])
            ops.append(Operation(job=job_idx, op_idx=op_idx, machine=machine, duration=duration))
        jobs.append(ops)

    return JSSPInstance(n_jobs=n_jobs, n_machines=n_machines, jobs=jobs)


# ── Simulation ──────────────────────────────────────────────────

# Type alias for heuristic functions
HeuristicFn = Callable[[list[dict], list[float], float], int]


def build_schedule(instance: JSSPInstance, heuristic_fn: HeuristicFn) -> list[ScheduledOp]:
    """Build a complete schedule using a dispatching-rule heuristic.

    At each step:
    1. Determine which operations are available (all predecessors in the same
       job are completed, i.e. the next unscheduled op for each job).
    2. Build the available_ops list with metadata for the heuristic.
    3. Call heuristic_fn(available_ops, machine_loads, current_time) to pick one.
    4. Schedule the selected operation at the earliest feasible time.
    5. Repeat until all operations are scheduled.
    """
    n_jobs = instance.n_jobs
    n_machines = instance.n_machines

    # State tracking
    next_op_idx: list[int] = [0] * n_jobs           # next unscheduled op per job
    job_end_time: list[float] = [0.0] * n_jobs       # when each job's last op finished
    machine_end_time: list[float] = [0.0] * n_machines  # when each machine becomes free
    machine_loads: list[float] = [0.0] * n_machines  # total load on each machine

    schedule: list[ScheduledOp] = []
    total_ops = instance.total_operations

    while len(schedule) < total_ops:
        # Find available operations
        available_ops: list[dict] = []
        available_indices: list[tuple[int, int]] = []  # (job_idx, op_idx)

        for job_idx in range(n_jobs):
            op_idx = next_op_idx[job_idx]
            if op_idx >= len(instance.jobs[job_idx]):
                continue  # job complete

            op = instance.jobs[job_idx][op_idx]
            remaining_ops = len(instance.jobs[job_idx]) - op_idx
            remaining_time = sum(
                o.duration for o in instance.jobs[job_idx][op_idx:]
            )

            available_ops.append({
                "job": job_idx,
                "op_idx": op_idx,
                "machine": op.machine,
                "duration": op.duration,
                "remaining_ops": remaining_ops,
                "remaining_time": remaining_time,
            })
            available_indices.append((job_idx, op_idx))

        if not available_ops:
            break  # should not happen if instance is valid

        # Compute current time as the minimum possible start time
        current_time = min(
            max(job_end_time[ji], machine_end_time[instance.jobs[ji][oi].machine])
            for ji, oi in available_indices
        )

        # Call heuristic
        try:
            selected = heuristic_fn(available_ops, list(machine_loads), current_time)
            selected = int(selected)
            if selected < 0 or selected >= len(available_ops):
                selected = 0
        except Exception:
            selected = 0

        # Schedule the selected operation
        job_idx, op_idx = available_indices[selected]
        op = instance.jobs[job_idx][op_idx]

        # Start time = max(job predecessor done, machine free)
        start = max(job_end_time[job_idx], machine_end_time[op.machine])
        end = start + op.duration

        schedule.append(ScheduledOp(
            job=job_idx,
            op_idx=op_idx,
            machine=op.machine,
            start=start,
            end=end,
        ))

        # Update state
        next_op_idx[job_idx] = op_idx + 1
        job_end_time[job_idx] = end
        machine_end_time[op.machine] = end
        machine_loads[op.machine] += op.duration

    return schedule


def compute_metrics(schedule: list[ScheduledOp], instance: JSSPInstance) -> dict[str, float]:
    """Compute all scheduling metrics from a completed schedule."""
    if not schedule:
        return {
            "makespan": float("inf"),
            "flowtime": float("inf"),
            "utilization": 0.0,
            "tardiness": 0.0,
        }

    # Makespan
    makespan = max(op.end for op in schedule)

    # Flowtime: sum of job completion times
    job_completions: dict[int, float] = {}
    for op in schedule:
        if op.job not in job_completions or op.end > job_completions[op.job]:
            job_completions[op.job] = op.end
    flowtime = sum(job_completions.values())

    # Utilization: total processing / (makespan * n_machines)
    total_processing = sum(op.end - op.start for op in schedule)
    utilization = (
        total_processing / (makespan * instance.n_machines)
        if makespan > 0
        else 0.0
    )

    # Tardiness: 0 for standard Taillard (no due dates)
    tardiness = 0.0

    return {
        "makespan": makespan,
        "flowtime": flowtime,
        "utilization": utilization,
        "tardiness": tardiness,
    }


def simulate(instance: JSSPInstance, heuristic_fn: HeuristicFn) -> dict[str, float]:
    """Convenience: build schedule and compute metrics in one call."""
    schedule = build_schedule(instance, heuristic_fn)
    return compute_metrics(schedule, instance)


# ── Gantt Data (optional visualization support) ─────────────────


def schedule_to_gantt_data(schedule: list[ScheduledOp]) -> list[dict]:
    """Convert schedule to Gantt-chart-ready dicts for visualization."""
    return [
        {
            "job": op.job,
            "machine": op.machine,
            "start": op.start,
            "end": op.end,
            "duration": op.end - op.start,
            "op_idx": op.op_idx,
        }
        for op in schedule
    ]
