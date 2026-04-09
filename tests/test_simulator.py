"""Tests for the JSSP simulator — parsing, schedule building, metrics."""
from __future__ import annotations

from heuristix.problems.jssp.benchmarks import FT06, FT10
from heuristix.problems.jssp.simulator import (
    build_schedule,
    compute_metrics,
    parse_instance,
    simulate,
)


# ── Parsing Tests ───────────────────────────────────────────────


def test_parse_ft06():
    """ft06 should parse as 6 jobs x 6 machines."""
    inst = parse_instance(FT06)
    assert inst.n_jobs == 6
    assert inst.n_machines == 6
    assert len(inst.jobs) == 6
    for job in inst.jobs:
        assert len(job) == 6


def test_parse_ft10():
    """ft10 should parse as 10 jobs x 10 machines."""
    inst = parse_instance(FT10)
    assert inst.n_jobs == 10
    assert inst.n_machines == 10
    assert len(inst.jobs) == 10
    for job in inst.jobs:
        assert len(job) == 10


def test_ft06_first_job_operations():
    """Verify the first job of ft06 has correct machine/duration pairs."""
    inst = parse_instance(FT06)
    job0 = inst.jobs[0]
    expected = [(2, 1), (0, 3), (1, 6), (3, 7), (5, 3), (4, 6)]
    for op, (m, d) in zip(job0, expected):
        assert op.machine == m
        assert op.duration == d


# ── Schedule Building Tests ─────────────────────────────────────


def spt_heuristic(available_ops, machine_loads, current_time):
    """Shortest Processing Time dispatching rule."""
    return min(range(len(available_ops)), key=lambda i: available_ops[i]["duration"])


def fifo_heuristic(available_ops, machine_loads, current_time):
    """First-come first-served (by job index)."""
    return min(range(len(available_ops)), key=lambda i: available_ops[i]["job"])


def test_schedule_ft06_spt():
    """SPT on ft06 should produce a valid complete schedule."""
    inst = parse_instance(FT06)
    schedule = build_schedule(inst, spt_heuristic)

    # Should have exactly 36 operations (6 jobs x 6 machines)
    assert len(schedule) == 36

    # Every operation should have start < end
    for op in schedule:
        assert op.start < op.end
        assert op.end - op.start > 0


def test_schedule_ft06_fifo():
    """FIFO on ft06 should produce a valid schedule."""
    inst = parse_instance(FT06)
    schedule = build_schedule(inst, fifo_heuristic)
    assert len(schedule) == 36


def test_schedule_respects_precedence():
    """Operations within a job must be scheduled in order."""
    inst = parse_instance(FT06)
    schedule = build_schedule(inst, spt_heuristic)

    # Group by job and verify ordering
    job_ops: dict[int, list] = {}
    for op in schedule:
        job_ops.setdefault(op.job, []).append(op)

    for job_idx, ops in job_ops.items():
        ops_sorted = sorted(ops, key=lambda o: o.op_idx)
        for i in range(1, len(ops_sorted)):
            # Each op must start after the previous one ends
            assert ops_sorted[i].start >= ops_sorted[i - 1].end


def test_schedule_respects_machine_capacity():
    """No two operations on the same machine should overlap."""
    inst = parse_instance(FT06)
    schedule = build_schedule(inst, spt_heuristic)

    machine_ops: dict[int, list] = {}
    for op in schedule:
        machine_ops.setdefault(op.machine, []).append(op)

    for machine, ops in machine_ops.items():
        ops_sorted = sorted(ops, key=lambda o: o.start)
        for i in range(1, len(ops_sorted)):
            assert ops_sorted[i].start >= ops_sorted[i - 1].end, (
                f"Machine {machine}: overlap between op ending at {ops_sorted[i-1].end} "
                f"and op starting at {ops_sorted[i].start}"
            )


# ── Metric Tests ────────────────────────────────────────────────


def test_metrics_ft06_spt():
    """Metrics on ft06 with SPT should return reasonable values."""
    inst = parse_instance(FT06)
    metrics = simulate(inst, spt_heuristic)

    assert metrics["makespan"] > 0
    assert metrics["makespan"] < 1000  # ft06 optimal is 55, worst shouldn't exceed ~200
    assert metrics["flowtime"] > 0
    assert 0.0 < metrics["utilization"] <= 1.0
    assert metrics["tardiness"] == 0.0


def test_metrics_ft06_known_range():
    """ft06 makespan should be in a reasonable range (optimal = 55)."""
    inst = parse_instance(FT06)
    metrics = simulate(inst, spt_heuristic)

    # SPT is a simple rule, should be between 55 and ~100
    assert 55 <= metrics["makespan"] <= 150, f"Unexpected makespan: {metrics['makespan']}"
