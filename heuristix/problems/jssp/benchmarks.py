"""Taillard benchmark instances — embedded small instances + file loader."""
from __future__ import annotations

from pathlib import Path

# ── Embedded Instances ──────────────────────────────────────────
# Format: first line = n_jobs n_machines
# Each subsequent line: machine_0 time_0  machine_1 time_1  ... (for one job)

# ft06: Fisher & Thompson, 6 jobs x 6 machines (optimal makespan = 55)
FT06 = """\
6 6
2 1  0 3  1 6  3 7  5 3  4 6
1 8  2 5  4 10  5 10  0 10  3 4
2 5  3 4  5 8  0 9  1 1  4 7
1 5  0 5  2 5  3 3  4 8  5 9
2 9  1 3  4 5  5 4  0 3  3 1
1 3  3 3  5 9  0 10  4 4  2 1
"""

# ft10: Fisher & Thompson, 10 jobs x 10 machines (optimal makespan = 930)
FT10 = """\
10 10
0 29  1 78  2 9  3 36  4 49  5 11  6 62  7 56  8 44  9 21
0 43  2 90  4 75  9 11  3 69  1 28  6 46  5 46  7 72  8 30
1 91  0 85  3 39  2 74  8 90  5 10  7 12  6 89  9 45  4 33
1 81  2 95  0 71  4 99  6 9  8 52  7 85  3 98  9 22  5 43
2 14  0 6  1 22  5 61  3 26  4 69  8 21  7 49  9 72  6 53
2 84  1 2  5 52  3 95  8 48  9 72  0 47  6 65  4 6  7 25
1 46  0 37  3 61  2 13  6 32  5 21  9 32  8 89  7 30  4 55
2 31  0 86  1 46  5 74  3 32  4 88  8 19  9 48  6 36  7 79
0 76  1 69  3 76  5 51  2 85  9 11  6 40  7 89  4 26  8 74
1 85  0 13  2 61  6 7  8 64  9 76  5 47  3 52  4 90  7 45
"""

# Registry of embedded instances
_EMBEDDED: dict[str, str] = {
    "ft06": FT06,
    "ft10": FT10,
}


def get_instance(name: str, data_dir: str | Path | None = None) -> str:
    """Load a benchmark instance by name.

    Checks embedded instances first, then falls back to file on disk.

    Args:
        name: Instance name (e.g. "ft06", "ft10", "ta01").
        data_dir: Optional directory to search for instance files.

    Returns:
        Raw instance text in Taillard format.

    Raises:
        FileNotFoundError: If the instance is not found anywhere.
    """
    # Check embedded
    if name in _EMBEDDED:
        return _EMBEDDED[name]

    # Check file system
    if data_dir is not None:
        data_path = Path(data_dir)
        for suffix in ["", ".txt", ".dat"]:
            candidate = data_path / f"{name}{suffix}"
            if candidate.exists():
                return candidate.read_text()

    raise FileNotFoundError(
        f"Benchmark instance {name!r} not found (embedded or on disk). "
        f"Available embedded: {list(_EMBEDDED.keys())}"
    )


def list_instances(include_disk: bool = False, data_dir: str | Path | None = None) -> list[str]:
    """List available benchmark instance names."""
    names = list(_EMBEDDED.keys())

    if include_disk and data_dir is not None:
        data_path = Path(data_dir)
        if data_path.is_dir():
            for f in data_path.iterdir():
                stem = f.stem
                if stem not in names and f.suffix in ("", ".txt", ".dat"):
                    names.append(stem)

    return sorted(names)
