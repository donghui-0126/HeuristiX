"""Main evolution loop — orchestrates population, operators, evaluation, and knowledge."""
from __future__ import annotations

import random
import time
from typing import TYPE_CHECKING

from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.table import Table

from heuristix.evolution.operators import crossover, init_population, mutate
from heuristix.evolution.population import Individual, Population
from heuristix.llm.provider import create_provider_for_role

if TYPE_CHECKING:
    from heuristix.amure_client import AmureClient
    from heuristix.config import HeuristiXConfig
    from heuristix.evaluation.cascade import EvaluationCascade
    from heuristix.knowledge.distillation import KnowledgeDistiller
    from heuristix.knowledge.selection import KnowledgeSelector
    from heuristix.llm.provider import LLMProvider
    from heuristix.problems.base import Problem


class EvolutionManager:
    """Drives the knowledge-evolutionary loop."""

    def __init__(
        self,
        config: HeuristiXConfig,
        problem: Problem,
        llm: LLMProvider,
        evaluator: EvaluationCascade,
        amure_client: AmureClient | None = None,
        knowledge_selector: KnowledgeSelector | None = None,
        knowledge_distiller: KnowledgeDistiller | None = None,
    ):
        self.config = config
        self.problem = problem
        self.llm = llm
        self.evaluator = evaluator

        # Create role-specific providers (fall back to llm if role config unavailable)
        try:
            self.llm_mutation = create_provider_for_role(config, "mutation")
            self.llm_crossover = create_provider_for_role(config, "crossover")
            self.llm_init = create_provider_for_role(config, "init")
        except (ValueError, Exception):
            self.llm_mutation = llm
            self.llm_crossover = llm
            self.llm_init = llm
        self.amure = amure_client
        self.selector = knowledge_selector
        self.distiller = knowledge_distiller
        self.console = Console()

        evo = config.evolution
        self.population = Population(
            max_size=evo.population_size,
            elitism=evo.elitism,
        )
        self.stagnation_count = 0
        self.best_ever: Individual | None = None

    def run(self, generations: int | None = None) -> Individual | None:
        """Main evolution loop. Returns the best individual found."""
        gens = generations or self.config.evolution.generations
        evo = self.config.evolution

        self.console.print("\n[bold cyan]--- Initializing population ---[/]")
        self._init_population()
        self._evaluate_population()
        self._update_best()
        self._log_generation(0)

        # Issue 1: Store initial population in amure-db
        if self.distiller:
            for ind in self.population.individuals:
                try:
                    node_id = self.distiller.store_heuristic(ind, generation=0)
                    ind.node_id = node_id
                except Exception:
                    pass

        # Issue 2: Progress bar wrapping the generation loop
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(bar_width=30),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=self.console,
        ) as progress:
            gen_task = progress.add_task("Evolution", total=gens)

            for gen in range(1, gens + 1):
                progress.update(gen_task, description=f"Gen {gen}/{gens}")
                start = time.time()

                offspring: list[Individual] = []
                target_offspring = evo.population_size - evo.elitism

                # Sub-progress for offspring generation
                offspring_task = progress.add_task(
                    "  Offspring", total=target_offspring, visible=True
                )

                for _ in range(target_offspring):
                    # Get knowledge context if amure-do is available
                    knowledge_ctx = ""
                    failure_warnings = ""
                    if self.selector:
                        parent_for_ctx = self.population.tournament_select(evo.tournament_size)
                        ctx = self.selector.get_context(parent_for_ctx)
                        knowledge_ctx = ctx.get("knowledge", "")
                        failure_warnings = ctx.get("failures", "")

                    if random.random() < evo.crossover_rate:
                        # Crossover
                        parent_a = self.population.tournament_select(evo.tournament_size)
                        parent_b = self.population.tournament_select(evo.tournament_size)
                        child = crossover(parent_a, parent_b, self.llm_crossover, knowledge_ctx)
                    else:
                        # Mutation
                        parent = self.population.tournament_select(evo.tournament_size)
                        child = mutate(parent, self.llm_mutation, knowledge_ctx, failure_warnings)

                    offspring.append(child)
                    progress.advance(offspring_task)

                progress.remove_task(offspring_task)

                # Evaluate offspring
                for ind in offspring:
                    self._evaluate_individual(ind)

                # Issue 1: Store offspring in amure-db and record lineage
                if self.distiller:
                    for ind in offspring:
                        try:
                            node_id = self.distiller.store_heuristic(ind, generation=gen)
                            ind.node_id = node_id
                            # Store lineage from parents
                            for pid in ind.parent_ids:
                                parent = next(
                                    (p for p in self.population.individuals if p.id == pid),
                                    None,
                                )
                                if parent and parent.node_id:
                                    self.distiller.store_evolution_lineage(
                                        parent.node_id, node_id, gen
                                    )
                        except Exception:
                            pass

                # Update population
                self.population.next_generation(offspring)
                prev_best = self.best_ever.primary_score if self.best_ever else float("inf")
                self._update_best()

                # Stagnation detection
                curr_best = self.best_ever.primary_score if self.best_ever else float("inf")
                if curr_best >= prev_best:
                    self.stagnation_count += 1
                else:
                    self.stagnation_count = 0

                # Suggest combinations if stuck
                if self.stagnation_count >= 5 and self.amure:
                    self.console.print("[yellow]Stagnation detected — querying amure-do for suggestions...[/]")
                    try:
                        suggestions = self.amure.suggest_combinations()
                        self.console.print(f"[yellow]Suggestions: {suggestions}[/]")
                    except Exception:
                        pass
                    self.stagnation_count = 0

                # Knowledge distillation
                kn = self.config.knowledge
                if self.distiller and gen % kn.distill_every == 0:
                    top_k = self.population.get_top(kn.top_k_compare)
                    bottom_k = self.population.get_bottom(kn.bottom_k_compare)
                    try:
                        self.distiller.distill_generation(top_k, bottom_k, gen)
                        self.distiller.promote_validated_claims(top_k, gen)
                    except Exception as e:
                        self.console.print(f"[red]Distillation error: {e}[/]")

                elapsed = time.time() - start
                self._log_generation(gen, elapsed)

                progress.advance(gen_task)

        # Issue 1: Mark best-ever as Accepted in amure-db
        if self.distiller and self.best_ever and self.best_ever.node_id:
            try:
                self.amure.update_node(self.best_ever.node_id, status="Accepted")
            except Exception:
                pass

        # Save graph at the end
        if self.amure:
            try:
                self.amure.save_graph()
            except Exception:
                pass

        self.console.print("\n[bold green]Evolution complete![/]")
        if self.best_ever:
            self.console.print(f"[bold green]Best: {self.best_ever.summary()}[/]")
            self.console.print(f"[dim]Thought: {self.best_ever.thought}[/]")

        # Knowledge summary
        if self.amure:
            try:
                summary = self.amure.graph_summary()
                self.console.print("\n[bold]Knowledge Summary:[/]")
                self.console.print(f"  Nodes: {summary.get('n_nodes', 0)}")
                self.console.print(f"  Edges: {summary.get('n_edges', 0)}")
                # Show maturity distribution if available
                by_status = summary.get("by_status", {})
                if by_status:
                    parts = [f"{s}: {c}" for s, c in sorted(by_status.items())]
                    self.console.print(f"  Maturity: {', '.join(parts)}")
                by_kind = summary.get("by_kind", {})
                if by_kind:
                    parts = [f"{k}: {c}" for k, c in sorted(by_kind.items())]
                    self.console.print(f"  Kinds: {', '.join(parts)}")
            except Exception:
                pass
        else:
            self.console.print("\n[dim]Knowledge: disabled (--no-amure)[/]")

        # Print benchmark comparison if per-instance data available
        self._print_benchmark_comparison()

        return self.best_ever

    def _init_population(self) -> None:
        """Generate the initial population via LLM."""
        description = self.problem.describe()
        individuals = init_population(
            self.config.evolution.population_size,
            self.llm_init,
            description,
        )
        for ind in individuals:
            self.population.add(ind)

    def _evaluate_population(self) -> None:
        """Evaluate all individuals in the current population."""
        for ind in self.population.individuals:
            self._evaluate_individual(ind)

    def _evaluate_individual(self, individual: Individual) -> None:
        """Evaluate a single individual using the cascade evaluator."""
        try:
            scores = self.evaluator.evaluate(
                individual.code,
                self.config.evaluation.quick_instances,
                self.config.evaluation.full_instances,
            )
            individual.scores = scores
        except Exception as e:
            self.console.print(f"[red]Evaluation failed for {individual.id}: {e}[/]")
            individual.scores = {"makespan": float("inf")}

    def _update_best(self) -> None:
        """Track the all-time best individual."""
        current_best = self.population.best
        if current_best is None:
            return
        if self.best_ever is None or current_best.primary_score < self.best_ever.primary_score:
            self.best_ever = current_best

    def _log_generation(self, gen: int, elapsed: float = 0.0) -> None:
        """Log generation statistics with rich table."""
        stats = self.population.stats()

        table = Table(title=f"Generation {gen}", show_lines=False)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Best makespan", f"{stats['best']:.1f}")
        table.add_row("Avg makespan", f"{stats['avg']:.1f}")
        table.add_row("Worst makespan", f"{stats['worst']:.1f}")
        table.add_row("Diversity", f"{stats['diversity']:.2f}")
        table.add_row("Population", str(self.population.size))
        if elapsed > 0:
            table.add_row("Time (s)", f"{elapsed:.1f}")
        if self.best_ever:
            table.add_row("Best ever", f"{self.best_ever.primary_score:.1f}")

        # Show per-instance gap-to-optimal for the best individual
        best = self.population.best
        if best:
            per_instance = best.scores.get("per_instance")
            if isinstance(per_instance, dict) and per_instance:
                from heuristix.problems.jssp.benchmarks_known import gap_to_optimal

                gaps = []
                for inst, inst_scores in sorted(per_instance.items()):
                    ms = inst_scores.get("makespan", float("inf"))
                    gap = gap_to_optimal(inst, ms)
                    if gap is not None:
                        gaps.append(f"{inst}: {gap:+.1f}%")
                if gaps:
                    table.add_row("Gap to optimal", ", ".join(gaps))

        self.console.print(table)

    def _print_benchmark_comparison(self) -> None:
        """Print a final benchmark comparison table for the best individual."""
        if not self.best_ever:
            return

        per_instance = self.best_ever.scores.get("per_instance")
        if not isinstance(per_instance, dict) or not per_instance:
            return

        from heuristix.problems.jssp.benchmarks_known import format_benchmark_comparison

        # Extract per-instance makespans
        instance_makespans: dict[str, float] = {}
        for inst, inst_scores in per_instance.items():
            ms = inst_scores.get("makespan", float("inf"))
            if ms < float("inf"):
                instance_makespans[inst] = ms

        if not instance_makespans:
            return

        self.console.print("\n[bold cyan]--- Benchmark Comparison ---[/]")
        comparison = format_benchmark_comparison(instance_makespans)
        self.console.print(f"[white]{comparison}[/]")
