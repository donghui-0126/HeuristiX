"""Execute heuristic code and compute metrics on JSSP instances."""
from __future__ import annotations

import json
import subprocess
import tempfile
import textwrap
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from heuristix.problems.base import Problem


class EvaluationRunner:
    """Run heuristic code on problem instances via subprocess."""

    def __init__(self, problem: Problem, timeout: int = 30):
        self.problem = problem
        self.timeout = timeout

    def evaluate(self, code: str, instances: list[str]) -> dict[str, float]:
        """Run heuristic on instances and return aggregated metrics.

        Args:
            code: Python source code defining `def heuristic(...)`.
            instances: list of instance names (e.g. ["ft06", "ft10"]).

        Returns:
            Aggregated metric dict or {"makespan": inf} on failure.
        """
        from heuristix.evaluation.metrics import aggregate_metrics

        all_scores: list[dict[str, float]] = []

        for instance_name in instances:
            scores = self._run_single(code, instance_name)
            if scores is not None:
                all_scores.append(scores)

        if not all_scores:
            return {"makespan": float("inf")}

        return aggregate_metrics(all_scores)

    def _run_single(self, code: str, instance_name: str) -> dict[str, float] | None:
        """Run the heuristic on a single instance in a subprocess."""
        runner_script = self._build_runner_script(code, instance_name)

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as f:
            f.write(runner_script)
            script_path = f.name

        try:
            result = subprocess.run(
                ["python3", script_path],
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )

            if result.returncode != 0:
                return None

            # Parse JSON output from the runner script
            output = result.stdout.strip()
            if not output:
                return None

            # Take the last line (in case of debug prints)
            last_line = output.strip().split("\n")[-1]
            return json.loads(last_line)

        except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception):
            return None
        finally:
            Path(script_path).unlink(missing_ok=True)

    def _build_runner_script(self, heuristic_code: str, instance_name: str) -> str:
        """Build a self-contained Python script that evaluates the heuristic."""
        # Get the problem's evaluation skeleton
        skeleton = self.problem.get_skeleton()

        return textwrap.dedent(f"""\
            import json
            import sys

            # --- Heuristic code ---
            {textwrap.indent(heuristic_code, "            ").strip()}

            # --- Problem skeleton (simulator + instance data) ---
            {textwrap.indent(skeleton, "            ").strip()}

            # --- Run evaluation ---
            if __name__ == "__main__":
                try:
                    metrics = run_evaluation(heuristic, "{instance_name}")
                    print(json.dumps(metrics))
                except Exception as e:
                    print(json.dumps({{"makespan": 1e18, "error": str(e)}}))
                    sys.exit(1)
        """)
