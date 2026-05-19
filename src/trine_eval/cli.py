from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> None:
    """Entry point for the trine-eval CLI."""
    parser = argparse.ArgumentParser(
        prog="trine-eval",
        description="trine-eval: LLM evaluation library CLI",
    )
    subparsers = parser.add_subparsers(dest="command", metavar="{run,score,report}")

    # run subcommand (stub)
    subparsers.add_parser("run", help="Run an evaluation task")

    # score subcommand — rescores a saved EvalLog without re-running the model
    score_parser = subparsers.add_parser(
        "score",
        help="Re-score a saved EvalLog without re-running the model",
    )
    score_parser.add_argument(
        "--log",
        required=True,
        metavar="PATH",
        help="Path to a saved EvalLog (.json or .msgpack)",
    )
    score_parser.add_argument(
        "--scorer",
        required=True,
        metavar="NAME",
        help="Name of the scorer to apply (e.g. exact_match)",
    )

    # report subcommand — prints token-efficiency metrics
    report_parser = subparsers.add_parser(
        "report",
        help="Print token-efficiency and cost metrics for a saved EvalLog",
    )
    report_parser.add_argument(
        "log",
        metavar="LOG",
        help="Path to a saved EvalLog (.json or .msgpack)",
    )

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)
    elif args.command == "run":
        print("trine-eval run: not implemented in v0.1 — sprint 3+")
        sys.exit(0)
    elif args.command == "score":
        _cmd_score(args)
    elif args.command == "report":
        _cmd_report(args)
    else:
        parser.print_help()
        sys.exit(1)


def _cmd_score(args: argparse.Namespace) -> None:
    """Re-score a saved EvalLog using the named scorer from the registry."""
    from trine_eval.runner.logformat import load
    from trine_eval.core import registry as _registry

    log_path = Path(args.log)
    if not log_path.exists():
        print(f"Error: log file not found: {log_path}", file=sys.stderr)
        sys.exit(1)

    log = load(log_path)

    # Look up the scorer in the registry
    scorer_fn = _registry.scorers.get(args.scorer)

    if scorer_fn is None:
        # Fall back to built-in exact_match if requested
        if args.scorer == "exact_match":
            scorer_fn = _exact_match_scorer
        else:
            print(f"Error: scorer not found: {args.scorer!r}", file=sys.stderr)
            sys.exit(1)

    # Re-score each sample using cached model responses from the log
    scores = []
    for sample, existing_score in zip(log.samples, log.scores):
        answer = existing_score.answer or ""
        new_score = scorer_fn(sample, answer)
        scores.append(new_score)

    total = len(scores)
    if total > 0:
        accuracy = sum(s.value for s in scores) / total
    else:
        accuracy = 0.0

    print(f"scorer: {args.scorer}")
    print(f"samples: {total}")
    print(f"score: {accuracy:.4f}")
    print(f"accuracy: {accuracy:.4f}")
    sys.exit(0)


def _exact_match_scorer(sample: object, answer: str) -> object:
    """Built-in exact match scorer (fallback when registry is empty)."""
    from trine_eval.core.score import Score
    from trine_eval.core.sample import Sample as S

    target = getattr(sample, "target", None) or ""
    value = 1.0 if answer.strip() == target.strip() else 0.0
    return Score(value=value, answer=answer)


def _cmd_report(args: argparse.Namespace) -> None:
    """Print token-efficiency and cost metrics for a saved EvalLog."""
    from trine_eval.runner.logformat import load
    from trine_eval.runner.metrics import accuracy_per_dollar, success_per_1k_tokens

    log_path = Path(args.log)
    if not log_path.exists():
        print(f"Error: log file not found: {log_path}", file=sys.stderr)
        sys.exit(1)

    log = load(log_path)

    # Compute aggregate if not present
    if "accuracy" not in log.aggregate and log.scores:
        accuracy = sum(s.value for s in log.scores) / len(log.scores)
    else:
        accuracy = log.aggregate.get("accuracy", 0.0)

    apd = accuracy_per_dollar(log)
    sp1k = success_per_1k_tokens(log)

    print(f"task: {log.task_name}")
    print(f"model: {log.model}")
    print(f"samples: {len(log.scores)}")
    print(f"accuracy: {accuracy:.4f}")
    print(f"accuracy_per_dollar: {apd:.6f}")
    print(f"success_per_1k_tokens: {sp1k:.6f}")
    sys.exit(0)


if __name__ == "__main__":
    main()
