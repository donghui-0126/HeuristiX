"""Multi-metric computation for JSSP schedules."""
from __future__ import annotations


def compute_metrics(
    schedule: list[dict],
    n_jobs: int,
    n_machines: int,
) -> dict[str, float]:
    """Compute scheduling metrics from a completed schedule.

    Args:
        schedule: list of {"job", "op_idx", "machine", "start", "end"} dicts
        n_jobs: total number of jobs
        n_machines: total number of machines

    Returns:
        {"makespan", "flowtime", "utilization", "tardiness"}
    """
    if not schedule:
        return {
            "makespan": float("inf"),
            "flowtime": float("inf"),
            "utilization": 0.0,
            "tardiness": 0.0,
        }

    # Makespan: latest completion time
    makespan = max(op["end"] for op in schedule)

    # Flowtime: sum of completion times per job (last op end for each job)
    job_completions: dict[int, float] = {}
    for op in schedule:
        job = op["job"]
        if job not in job_completions or op["end"] > job_completions[job]:
            job_completions[job] = op["end"]
    flowtime = sum(job_completions.values())

    # Utilization: total processing time / (makespan * n_machines)
    total_processing = sum(op["end"] - op["start"] for op in schedule)
    utilization = total_processing / (makespan * n_machines) if makespan > 0 else 0.0

    # Tardiness: 0 for now (no due dates in standard Taillard instances)
    tardiness = 0.0

    return {
        "makespan": makespan,
        "flowtime": flowtime,
        "utilization": utilization,
        "tardiness": tardiness,
    }


def aggregate_metrics(
    all_scores: list[dict[str, float]],
    weights: dict[str, float] | None = None,
) -> dict[str, float]:
    """Aggregate scores across multiple instances.

    For makespan/flowtime/tardiness: use weighted average.
    For utilization: use average (higher is better, but we keep it as-is).
    """
    if not all_scores:
        return {"makespan": float("inf"), "flowtime": float("inf"), "utilization": 0.0}

    if weights is None:
        weights = {"makespan": 1.0, "flowtime": 0.3, "utilization": 0.2}

    # Average each metric across instances
    metric_keys = set()
    for s in all_scores:
        metric_keys.update(s.keys())

    averaged: dict[str, float] = {}
    for key in metric_keys:
        values = [s[key] for s in all_scores if key in s]
        if values:
            averaged[key] = sum(values) / len(values)
        else:
            averaged[key] = float("inf")

    # Compute weighted composite score
    composite = 0.0
    for metric, weight in weights.items():
        val = averaged.get(metric, 0.0)
        # For utilization, higher is better — invert for composite
        if metric == "utilization":
            composite += weight * (1.0 - val)
        else:
            composite += weight * val
    averaged["composite"] = composite

    return averaged
