"""CLI entry for V85 proposal generation (Hari + Expert)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from vai.io.expert_tips import default_tips_dir, list_expert_tips
from vai.io.pools import empty_operator_pools, load_operator_pools
from vai.io.proposal import format_expert_proposal_markdown, format_proposal_markdown
from vai.io.race_card import load_race_card
from vai.models.expert_tip import ExpertError, ExpertResult
from vai.models.proposal import RandomError, RandomResult
from vai.strategies.expert import generate_expert_v1
from vai.strategies.random import generate_random_v1

DEFAULT_BUDGET_SEK = 500.0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="VAI V85 proposal toolkit")
    subparsers = parser.add_subparsers(dest="command", required=True)

    random_parser = subparsers.add_parser("random", help="Generate random-mode V85 proposal")
    random_parser.add_argument("--race-card", required=True, type=Path, help="Path to race card YAML")
    random_parser.add_argument(
        "--pools",
        type=Path,
        default=None,
        help="Operator horse picks YAML (default: none marked — random fills all legs)",
    )
    random_parser.add_argument(
        "--budget",
        type=float,
        default=DEFAULT_BUDGET_SEK,
        help=f"SYSTEMKOSTNAD in SEK (default: {DEFAULT_BUDGET_SEK:g})",
    )
    random_parser.add_argument("--seed", type=int, default=None, help="RNG seed for reproducibility")
    random_parser.add_argument("--out", type=Path, required=True, help="Output proposal markdown path")

    expert = subparsers.add_parser("expert", help="Expert tip list / apply (UC-12)")
    expert_sub = expert.add_subparsers(dest="expert_command", required=True)

    expert_list = expert_sub.add_parser("list", help="List expert tips")
    expert_list.add_argument("--date", type=str, default=None, help="Filter by ISO date")
    expert_list.add_argument("--track", type=str, default=None, help="Filter by track name")
    expert_list.add_argument(
        "--tips-dir",
        type=Path,
        default=None,
        help="Tips directory (default: inbox/expert-tips)",
    )

    expert_apply = expert_sub.add_parser("apply", help="Apply tip and write proposal markdown")
    expert_apply.add_argument("--tip", required=True, help="tip_id or path to tip YAML")
    expert_apply.add_argument("--race-card", required=True, type=Path, help="Race card YAML")
    expert_apply.add_argument("--out", type=Path, required=True, help="Output proposal path")
    expert_apply.add_argument(
        "--tips-dir",
        type=Path,
        default=None,
        help="Tips directory when --tip is a tip_id",
    )

    serve_parser = subparsers.add_parser("serve", help="Run local UI server (mockup + API)")
    serve_parser.add_argument("--host", default="127.0.0.1", help="Bind host")
    serve_parser.add_argument(
        "--port",
        type=int,
        default=8766,
        help="Bind port (default 8766 for dev; production vai.service uses 8765)",
    )

    args = parser.parse_args(argv)

    if args.command == "random":
        return _run_random(args)
    if args.command == "expert":
        if args.expert_command == "list":
            return _run_expert_list(args)
        if args.expert_command == "apply":
            return _run_expert_apply(args)
    if args.command == "serve":
        return _run_serve(args)

    return 1


def _run_serve(args: argparse.Namespace) -> int:
    from vai.server import serve

    serve(host=args.host, port=args.port)
    return 0


def _run_random(args: argparse.Namespace) -> int:
    race_card = load_race_card(args.race_card)
    if args.pools is not None:
        operator_pools = load_operator_pools(args.pools)
    else:
        operator_pools = empty_operator_pools()

    outcome = generate_random_v1(
        race_card,
        operator_pools,
        args.budget,
        seed=args.seed,
    )

    if isinstance(outcome, RandomError):
        _print_random_error(outcome)
        return 1

    assert isinstance(outcome, RandomResult)
    markdown = format_proposal_markdown(race_card, outcome, stake_budget_sek=args.budget)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(markdown, encoding="utf-8")

    print(f"Proposal written to {args.out}")
    print(f"Cost: {outcome.cost_sek:.2f} SEK ({outcome.combinations} combinations)")
    return 0


def _run_expert_list(args: argparse.Namespace) -> int:
    tips_dir = args.tips_dir or default_tips_dir()
    tips = list_expert_tips(tips_dir, date=args.date, track=args.track)
    if not tips:
        print("No expert tips found.")
        return 0
    for tip in tips:
        product = f" · {tip.product_name}" if tip.product_name else ""
        print(
            f"{tip.tip_id}\t{tip.expert_name}{product}\t"
            f"{tip.date} {tip.track}\t{tip.cost_sek:.2f} SEK\t{tip.combinations} rader"
        )
    return 0


def _run_expert_apply(args: argparse.Namespace) -> int:
    race_card = load_race_card(args.race_card)
    tips_dir = args.tips_dir or default_tips_dir()
    outcome = generate_expert_v1(args.tip, race_card=race_card, tips_dir=tips_dir)
    if isinstance(outcome, ExpertError):
        print(f"Error [{outcome.code}]: {outcome.message}", file=sys.stderr)
        if outcome.hint:
            print(f"Hint: {outcome.hint}", file=sys.stderr)
        return 1
    assert isinstance(outcome, ExpertResult)
    markdown = format_expert_proposal_markdown(race_card, outcome)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(markdown, encoding="utf-8")
    print(f"Proposal written to {args.out}")
    print(
        f"Expert: {outcome.manifest.expert_name} · "
        f"{outcome.cost_sek:.2f} SEK ({outcome.combinations} combinations)"
    )
    return 0


def _print_random_error(error: RandomError) -> None:
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
