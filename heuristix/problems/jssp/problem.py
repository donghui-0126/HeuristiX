"""JSSP Problem implementation — connects benchmarks, simulator, and evaluation."""
from __future__ import annotations

import textwrap

from heuristix.problems.base import Problem
from heuristix.problems.jssp.benchmarks import FT06, FT10, get_instance
from heuristix.problems.jssp.simulator import (
    compute_metrics,
    build_schedule,
    parse_instance,
)


class JSSPProblem(Problem):
    """Job-Shop Scheduling Problem using Taillard benchmarks."""

    def __init__(
        self,
        quick_instances: list[str] | None = None,
        full_instances: list[str] | None = None,
        data_dir: str | None = None,
    ):
        self.quick_instances = quick_instances or ["ft06"]
        self.full_instances = full_instances or ["ft06", "ft10"]
        self.data_dir = data_dir

    def get_skeleton(self) -> str:
        """Return a self-contained Python evaluation skeleton.

        This code is embedded into the subprocess runner script.
        It includes the simulator logic and all instance data needed.
        """
        return textwrap.dedent('''\
            # ── JSSP Simulator (embedded) ──

            def parse_instance(text):
                lines = [l.strip() for l in text.strip().split("\\n") if l.strip()]
                header = lines[0].split()
                n_jobs, n_machines = int(header[0]), int(header[1])
                jobs = []
                for ji in range(n_jobs):
                    tokens = lines[1 + ji].split()
                    ops = []
                    for oi in range(n_machines):
                        machine = int(tokens[2 * oi])
                        duration = int(tokens[2 * oi + 1])
                        ops.append({"job": ji, "op_idx": oi, "machine": machine, "duration": duration})
                    jobs.append(ops)
                return {"n_jobs": n_jobs, "n_machines": n_machines, "jobs": jobs}

            def build_schedule(instance, heuristic_fn):
                n_jobs = instance["n_jobs"]
                n_machines = instance["n_machines"]
                jobs = instance["jobs"]
                next_op = [0] * n_jobs
                job_end = [0.0] * n_jobs
                machine_end = [0.0] * n_machines
                machine_loads = [0.0] * n_machines
                schedule = []
                total_ops = sum(len(j) for j in jobs)

                while len(schedule) < total_ops:
                    available = []
                    indices = []
                    for ji in range(n_jobs):
                        oi = next_op[ji]
                        if oi >= len(jobs[ji]):
                            continue
                        op = jobs[ji][oi]
                        rem_ops = len(jobs[ji]) - oi
                        rem_time = sum(o["duration"] for o in jobs[ji][oi:])
                        available.append({
                            "job": ji, "op_idx": oi, "machine": op["machine"],
                            "duration": op["duration"], "remaining_ops": rem_ops,
                            "remaining_time": rem_time,
                        })
                        indices.append((ji, oi))
                    if not available:
                        break
                    current_time = min(
                        max(job_end[ji], machine_end[jobs[ji][oi]["machine"]])
                        for ji, oi in indices
                    )
                    try:
                        sel = heuristic_fn(available, list(machine_loads), current_time)
                        sel = int(sel)
                        if sel < 0 or sel >= len(available):
                            sel = 0
                    except Exception:
                        sel = 0
                    ji, oi = indices[sel]
                    op = jobs[ji][oi]
                    start = max(job_end[ji], machine_end[op["machine"]])
                    end = start + op["duration"]
                    schedule.append({"job": ji, "op_idx": oi, "machine": op["machine"], "start": start, "end": end})
                    next_op[ji] = oi + 1
                    job_end[ji] = end
                    machine_end[op["machine"]] = end
                    machine_loads[op["machine"]] += op["duration"]
                return schedule

            def compute_schedule_metrics(schedule, n_jobs, n_machines):
                if not schedule:
                    return {"makespan": 1e18, "flowtime": 1e18, "utilization": 0.0, "tardiness": 0.0}
                makespan = max(op["end"] for op in schedule)
                job_comp = {}
                for op in schedule:
                    j = op["job"]
                    if j not in job_comp or op["end"] > job_comp[j]:
                        job_comp[j] = op["end"]
                flowtime = sum(job_comp.values())
                total_proc = sum(op["end"] - op["start"] for op in schedule)
                util = total_proc / (makespan * n_machines) if makespan > 0 else 0.0
                return {"makespan": makespan, "flowtime": flowtime, "utilization": util, "tardiness": 0.0}

            # ── Instance data ──

            INSTANCES = {
                "ft06": """''' + FT06.strip() + '''""",
                "ft10": """''' + FT10.strip() + '''""",
            }

            def run_evaluation(heuristic_fn, instance_name):
                text = INSTANCES.get(instance_name)
                if text is None:
                    return {"makespan": 1e18, "error": f"Unknown instance: {instance_name}"}
                inst = parse_instance(text)
                schedule = build_schedule(inst, heuristic_fn)
                return compute_schedule_metrics(schedule, inst["n_jobs"], inst["n_machines"])
        ''')

    def get_heuristic_template(self) -> str:
        """Return the function signature the LLM should implement."""
        return textwrap.dedent("""\
            def heuristic(available_ops, machine_loads, current_time):
                \"\"\"Select which operation to dispatch next.

                Args:
                    available_ops: list of dicts with keys:
                        - "job": job index
                        - "op_idx": operation index within the job
                        - "machine": machine this operation runs on
                        - "duration": processing time
                        - "remaining_ops": remaining operations for this job
                        - "remaining_time": total remaining time for this job
                    machine_loads: list of floats, current total load per machine
                    current_time: current simulation time

                Returns:
                    int: index into available_ops
                \"\"\"
                # Your dispatching rule here
                return 0
        """)

    def evaluate(self, heuristic_code: str, instance_name: str) -> dict:
        """Evaluate a heuristic on a specific instance using the in-process simulator."""
        text = get_instance(instance_name, self.data_dir)
        instance = parse_instance(text)

        # Compile and extract the heuristic function
        namespace: dict = {}
        exec(heuristic_code, namespace)  # noqa: S102
        heuristic_fn = namespace.get("heuristic")
        if heuristic_fn is None:
            return {"makespan": float("inf"), "error": "No 'heuristic' function found"}

        schedule = build_schedule(instance, heuristic_fn)
        return compute_metrics(schedule, instance)

    def get_instances(self, subset: str = "quick") -> list[str]:
        """Return instance names for a given subset."""
        if subset == "quick":
            return list(self.quick_instances)
        elif subset == "full":
            return list(self.full_instances)
        else:
            return list(self.quick_instances)

    def describe(self) -> str:
        """Natural-language problem description for LLM prompts."""
        return textwrap.dedent("""\
            Job-Shop Scheduling Problem (JSSP):

            Given N jobs and M machines, each job consists of a sequence of operations.
            Each operation must be processed on a specific machine for a specific duration.
            Operations within a job must be executed in order (precedence constraints).
            Each machine can process only one operation at a time (capacity constraints).

            Goal: Minimize the makespan (total completion time of all jobs).

            The heuristic is a dispatching rule that selects which available operation
            to schedule next. At each decision point, multiple operations may be ready
            (their job predecessors are complete). The heuristic chooses one based on
            properties like processing time, remaining work, machine load, etc.

            Benchmark: Taillard instances (ft06: 6x6, ft10: 10x10, ft20: 20x5).
        """)
