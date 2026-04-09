"""HeuristiX CLI — run evolution from the command line."""
from __future__ import annotations

import argparse
import sys

from rich.console import Console

from heuristix.config import load_config


def main(argv: list[str] | None = None) -> None:
    """Entry point for the heuristix CLI."""
    parser = argparse.ArgumentParser(
        description="HeuristiX: Knowledge-Evolutionary Heuristic Discovery"
    )
    parser.add_argument("--config", default="configs/default.yaml", help="Path to config YAML")
    parser.add_argument("--generations", type=int, default=None, help="Override generation count")
    parser.add_argument("--population", type=int, default=None, help="Override population size")
    parser.add_argument("--problem", default="jssp", help="Problem type (default: jssp)")
    parser.add_argument(
        "--no-amure",
        action="store_true",
        help="Run without amure-do connection (no knowledge storage)",
    )
    parser.add_argument(
        "--rag-mode",
        choices=["full", "failure-only", "adaptive", "none"],
        default="full",
        help="RAG injection mode: full (insights+failures), failure-only, adaptive (late-stage only), none",
    )
    args = parser.parse_args(argv)

    console = Console()
    console.print("[bold purple]HeuristiX[/] — Knowledge-Evolutionary Heuristic Discovery\n")

    # Load configuration
    config = load_config(args.config)

    # Override from CLI args
    if args.generations is not None:
        config.evolution.generations = args.generations
    if args.population is not None:
        config.evolution.population_size = args.population

    # Initialize problem
    if args.problem == "jssp":
        from heuristix.problems.jssp.problem import JSSPProblem

        problem = JSSPProblem(
            quick_instances=config.evaluation.quick_instances,
            full_instances=config.evaluation.full_instances,
        )
    else:
        console.print(f"[red]Unknown problem type: {args.problem}[/]")
        sys.exit(1)

    # Initialize LLM provider (default role)
    from heuristix.llm.provider import create_provider

    llm = create_provider(
        provider=config.llm.default.provider,
        model=config.llm.default.model,
        api_key=config.llm.default.api_key,
        temperature=config.llm.default.temperature,
    )

    # Initialize evaluator
    from heuristix.evaluation.cascade import EvaluationCascade

    evaluator = EvaluationCascade(
        problem=problem,
        timeout=config.evaluation.timeout_per_instance,
    )

    # Initialize amure-do client (optional)
    amure_client = None
    knowledge_selector = None
    knowledge_distiller = None

    if not args.no_amure:
        from heuristix.amure_client import AmureClient
        from heuristix.knowledge.embeddings import EmbeddingStore

        amure_client = AmureClient(
            base_url=config.amure_do.url,
            timeout=config.amure_do.timeout,
        )

        # Initialize embedding store (works independently of amure-do)
        embedding_store = EmbeddingStore()
        console.print(f"[cyan]Embedding store: {embedding_store.size} entries[/]")

        if amure_client.is_connected():
            console.print(f"[green]Connected to amure-do at {config.amure_do.url}[/]")

            from heuristix.knowledge.distillation import KnowledgeDistiller
            from heuristix.knowledge.selection import KnowledgeSelector

            knowledge_selector = KnowledgeSelector(amure_client, embedding_store=embedding_store)
            knowledge_distiller = KnowledgeDistiller(
                amure_client, llm, config=config, embedding_store=embedding_store
            )
        else:
            console.print(
                f"[yellow]amure-do not reachable at {config.amure_do.url} "
                f"— running without knowledge storage[/]"
            )
            amure_client = None

    # Run evolution
    from heuristix.evolution.manager import EvolutionManager

    manager = EvolutionManager(
        config=config,
        problem=problem,
        llm=llm,
        evaluator=evaluator,
        amure_client=amure_client,
        knowledge_selector=knowledge_selector,
        knowledge_distiller=knowledge_distiller,
        rag_mode=args.rag_mode if not args.no_amure else "none",
    )

    best = manager.run()

    if best:
        console.print("\n[bold green]═══ Best Heuristic Found ═══[/]")
        console.print(f"[cyan]ID:[/] {best.id}")
        console.print(f"[cyan]Makespan:[/] {best.primary_score:.1f}")
        console.print(f"[cyan]Thought:[/] {best.thought}")
        console.print(f"[cyan]Code:[/]\n{best.code}")
    else:
        console.print("[red]No valid heuristic found.[/]")


if __name__ == "__main__":
    main()
