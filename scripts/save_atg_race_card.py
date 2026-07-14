"""Save an ATG V85 game as inbox YAML (AIRUP Inbox step)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

from vai.atg_race_card import fetch_race_card_from_atg


def _slug_track(track: str) -> str:
    replacements = {"å": "a", "ä": "a", "ö": "o", "Å": "a", "Ä": "a", "Ö": "o", " ": "-"}
    slug = track.lower()
    for src, dst in replacements.items():
        slug = slug.replace(src, dst)
    return slug


def race_card_to_yaml_dict(card) -> dict:
    return {
        "game": card.game,
        "date": card.date,
        "track": card.track,
        "source": card.source,
        "fetched_at": card.fetched_at,
        "settled": card.settled,
        "legs": [
            {
                "leg": leg.leg,
                "race_label": leg.race_label,
                "horses": list(leg.horses),
                **({"start_time": leg.start_time} if leg.start_time else {}),
                **({"scratches": list(leg.scratches)} if leg.scratches else {}),
                **({"reserves": list(leg.reserves)} if leg.reserves else {}),
            }
            for leg in card.legs
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Save ATG V85 race card to inbox/race-cards/")
    parser.add_argument("game_id", help="ATG game id, e.g. V85_2026-07-11_31_5")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("inbox/race-cards"),
        help="Output directory (default: inbox/race-cards)",
    )
    args = parser.parse_args(argv)

    card = fetch_race_card_from_atg(args.game_id)
    filename = f"{card.date}-{_slug_track(card.track)}.yaml"
    out_path = args.out_dir / filename
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        yaml.safe_dump(race_card_to_yaml_dict(card), sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    print(f"Saved {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())