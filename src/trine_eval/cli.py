from __future__ import annotations

import argparse
import sys


def main() -> None:
    """Entry point for the trine-eval CLI."""
    parser = argparse.ArgumentParser(
        prog="trine-eval",
        description="trine-eval: LLM evaluation library CLI",
    )
    subparsers = parser.add_subparsers(dest="command", metavar="{run,score,report}")

    subparsers.add_parser("run", help="Run an evaluation task")
    subparsers.add_parser("score", help="Score evaluation results")
    subparsers.add_parser("report", help="Generate an evaluation report")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    print(f"trine-eval {args.command}: not implemented in v0.1 — sprint 2+")
    sys.exit(0)


if __name__ == "__main__":
    main()
