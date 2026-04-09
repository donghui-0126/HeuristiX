"""Known optimal and best-known results for JSSP Taillard benchmarks."""
from __future__ import annotations


# Source: OR-Library, various papers
KNOWN_RESULTS: dict[str, dict] = {
    # instance: {"optimal": value, "best_known": value, "size": "JxM"}
    "ft06": {"optimal": 55, "best_known": 55, "size": "6x6"},
    "ft10": {"optimal": 930, "best_known": 930, "size": "10x10"},
    "ft20": {"optimal": 1165, "best_known": 1165, "size": "20x5"},
    "la01": {"optimal": 666, "best_known": 666, "size": "10x5"},
    "la02": {"optimal": 655, "best_known": 655, "size": "10x5"},
    "la03": {"optimal": 597, "best_known": 597, "size": "10x5"},
    "la04": {"optimal": 590, "best_known": 590, "size": "10x5"},
    "la05": {"optimal": 593, "best_known": 593, "size": "10x5"},
    "la06": {"optimal": 926, "best_known": 926, "size": "15x5"},
    "la07": {"optimal": 890, "best_known": 890, "size": "15x5"},
    "la08": {"optimal": 863, "best_known": 863, "size": "15x5"},
    "la09": {"optimal": 951, "best_known": 951, "size": "15x5"},
    "la10": {"optimal": 958, "best_known": 958, "size": "15x5"},
    "la11": {"optimal": 1222, "best_known": 1222, "size": "20x5"},
    "la16": {"optimal": 945, "best_known": 945, "size": "10x10"},
    "la17": {"optimal": 784, "best_known": 784, "size": "10x10"},
    "la18": {"optimal": 848, "best_known": 848, "size": "10x10"},
    "la19": {"optimal": 842, "best_known": 842, "size": "10x10"},
    "la20": {"optimal": 902, "best_known": 902, "size": "10x10"},
    "la21": {"optimal": 1046, "best_known": 1046, "size": "15x10"},
    "la36": {"optimal": 1268, "best_known": 1268, "size": "15x15"},
    "la37": {"optimal": 1397, "best_known": 1397, "size": "15x15"},
    "la38": {"optimal": 1196, "best_known": 1196, "size": "15x15"},
    "la39": {"optimal": 1233, "best_known": 1233, "size": "15x15"},
    "la40": {"optimal": 1222, "best_known": 1222, "size": "15x15"},
}


def gap_to_optimal(instance: str, makespan: float) -> float | None:
    """Calculate gap to optimal in percent. Returns None if optimal unknown."""
    if instance not in KNOWN_RESULTS:
        return None
    opt = KNOWN_RESULTS[instance]["optimal"]
    return ((makespan - opt) / opt) * 100


def format_benchmark_comparison(results: dict[str, float]) -> str:
    """Format results with gap-to-optimal comparison.

    Args:
        results: mapping of instance name to makespan value.

    Returns:
        Formatted comparison table as a string.
    """
    lines = []
    lines.append(f"{'Instance':<10} {'Size':<8} {'Ours':<10} {'Optimal':<10} {'Gap%':<8}")
    lines.append("-" * 46)
    for inst, makespan in sorted(results.items()):
        if inst in KNOWN_RESULTS:
            opt = KNOWN_RESULTS[inst]["optimal"]
            size = KNOWN_RESULTS[inst]["size"]
            gap = ((makespan - opt) / opt) * 100
            lines.append(f"{inst:<10} {size:<8} {makespan:<10.1f} {opt:<10} {gap:<8.1f}%")
        else:
            lines.append(f"{inst:<10} {'?':<8} {makespan:<10.1f} {'?':<10} {'?':<8}")
    return "\n".join(lines)
