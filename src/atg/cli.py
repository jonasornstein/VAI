"""CLI entry for random-mode proposal generation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from atg.io.pools import load_operator_pools, pools_from_race_card
from atg.io.proposal import format_proposal_markdown
from atg.io.race_card import load_race_card
from atg.models.proposal import RandomError, RandomResult
from atg.strategies.random import generate_random_v1

DEFAULT_BUDGET_SEK = 500.0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ATG V85 proposal toolkit")
    subparsers = parser.add_subparsers(dest="command", required=True)

    random_parser = subparsers.add_parser("random", help="Generate random-mode V85 proposal")
    random_parser.add_argument("--race-card", required=True, type=Path, help="Path to race card YAML")
    random_parser.add_argument(
        "--pools",
        type=Path,
        default=None,
        help="Operator pools YAML (default: all race-card horses)",
    )
    random_parser.add_argument(
        "--budget",
        type=float,
        default=DEFAULT_BUDGET_SEK,
        help=f"SYSTEMKOSTNAD in SEK (default: {DEFAULT_BUDGET_SEK:g})",
    )
    random_parser.add_argument("--seed", type=int, default=None, help="RNG seed for reproducibility")
    random_parser.add_argument("--out", type=Path, required=True, help="Output proposal markdown path")

    args = parser.parse_args(argv)

    if args.command == "random":
        return _run_random(args)

    return 1


def _run_random(args: argparse.Namespace) -> int:
    race_card = load_race_card(args.race_card)
    if args.pools is not None:
        operator_pools = load_operator_pools(args.pools)
    else:
        operator_pools = pools_from_race_card(race_card)

    outcome = generate_random_v1(
        race_card,
        operator_pools,
        args.budget,
        seed=args.seed,
    )

    if isinstance(outcome, RandomError):
        _print_error(outcome)
        return 1

    assert isinstance(outcome, RandomResult)
    markdown = format_proposal_markdown(race_card, outcome, stake_budget_sek=args.budget)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(markdown, encoding="utf-8")

    print(f"Proposal written to {args.out}")
    print(f"Cost: {outcome.cost_sek:.2f} SEK ({outcome.combinations} combinations)")
    return 0


def _print_error(error: RandomError) -> None:
    print(f"Error [{error.code}]: {error.message}", file=sys.stderr)
    if error.hint:
        print(f"Hint: {error.hint}", file=sys.stderr)
    if error.cost_sek is not None and error.stake_budget_sek is not None:
        print(
            f"Cost after shrink: {error.cost_sek:.2f} SEK "
            f"(budget {error.stake_budget_sek:.2f} SEK, {error.combinations} combinations)",
            file=sys.stderr,
        )


if __name__ == "__main__":
    raise SystemExit(main())