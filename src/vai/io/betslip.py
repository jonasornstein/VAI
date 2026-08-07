"""Portable betslip YAML — save/load for local UI (SPARA / LADDA UPP)."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from vai.io.expert_tips import track_slug

SUPPORTED_VERSIONS = frozenset({1})
NUM_LEGS = 8
MODES = frozenset({"random", "expert"})


class BetslipValidationError(ValueError):
    def __init__(self, message: str, *, code: str = "INVALID_BETSLIP") -> None:
        super().__init__(message)
        self.code = code


def default_betslips_dir(repo_root: Path | None = None) -> Path:
    if repo_root is None:
        here = Path(__file__).resolve()
        for parent in here.parents:
            if (parent / "pyproject.toml").is_file() and (parent / "inbox").is_dir():
                return parent / "betslips"
        return Path.cwd() / "betslips"
    return Path(repo_root) / "betslips"


def betslip_basename(date: str, track: str, game: str) -> str:
    """File basename without extension: {date}-{track_slug}-{GAME}."""
    d = (date or "").strip()
    t = track_slug(track or "")
    g = (game or "V85").strip().upper() or "V85"
    if not d:
        raise BetslipValidationError("date is required for basename", code="MISSING_DATE")
    if not t:
        raise BetslipValidationError("track is required for basename", code="MISSING_TRACK")
    return f"{d}-{t}-{g}"


def next_available_path(directory: str | Path, basename: str, *, ext: str = ".yaml") -> Path:
    """Return directory/basename.ext, or basename-2.ext, basename-3.ext, … if taken."""
    root = Path(directory)
    root.mkdir(parents=True, exist_ok=True)
    base = basename.strip()
    if not base:
        raise BetslipValidationError("basename is empty", code="INVALID_BASENAME")
    if not ext.startswith("."):
        ext = f".{ext}"
    candidate = root / f"{base}{ext}"
    if not candidate.exists():
        return candidate
    n = 2
    while True:
        candidate = root / f"{base}-{n}{ext}"
        if not candidate.exists():
            return candidate
        n += 1
        if n > 10_000:
            raise BetslipValidationError("too many betslip name collisions", code="NAME_COLLISION")


def _normalize_leg_map(raw: Any, *, field: str) -> dict[str, list[int]]:
    if raw is None:
        return {str(i): [] for i in range(1, NUM_LEGS + 1)}
    if not isinstance(raw, dict):
        raise BetslipValidationError(f"{field} must be a mapping of leg → horses", code="INVALID_LEGS")
    out: dict[str, list[int]] = {str(i): [] for i in range(1, NUM_LEGS + 1)}
    for key, value in raw.items():
        try:
            leg = int(key)
        except (TypeError, ValueError) as exc:
            raise BetslipValidationError(f"{field}: invalid leg key {key!r}", code="INVALID_LEG") from exc
        if leg < 1 or leg > NUM_LEGS:
            raise BetslipValidationError(f"{field}: leg {leg} out of range 1–{NUM_LEGS}", code="INVALID_LEG")
        if value is None:
            horses: list[int] = []
        elif not isinstance(value, (list, tuple)):
            raise BetslipValidationError(
                f"{field}: leg {leg} horses must be a list",
                code="INVALID_HORSES",
            )
        else:
            horses = []
            for h in value:
                try:
                    horses.append(int(h))
                except (TypeError, ValueError) as exc:
                    raise BetslipValidationError(
                        f"{field}: leg {leg} has non-integer horse {h!r}",
                        code="INVALID_HORSES",
                    ) from exc
            horses = sorted(set(horses))
        out[str(leg)] = horses
    return out


def _normalize_frozen(raw: Any) -> list[int]:
    if raw is None:
        return []
    if not isinstance(raw, (list, tuple)):
        raise BetslipValidationError("frozen_legs must be a list", code="INVALID_FROZEN")
    out: list[int] = []
    for item in raw:
        try:
            leg = int(item)
        except (TypeError, ValueError) as exc:
            raise BetslipValidationError(f"frozen_legs: invalid leg {item!r}", code="INVALID_FROZEN") from exc
        if leg < 1 or leg > NUM_LEGS:
            raise BetslipValidationError(f"frozen_legs: leg {leg} out of range", code="INVALID_FROZEN")
        if leg not in out:
            out.append(leg)
    return sorted(out)


def validate_betslip_payload(data: Any) -> dict[str, Any]:
    """Validate and normalize a betslip dict (from YAML or JSON)."""
    if not isinstance(data, dict):
        raise BetslipValidationError("betslip must be a mapping", code="INVALID_BETSLIP")

    version = data.get("vai_betslip_version", 1)
    try:
        version_i = int(version)
    except (TypeError, ValueError) as exc:
        raise BetslipValidationError(
            f"unsupported vai_betslip_version: {version!r}",
            code="UNSUPPORTED_VERSION",
        ) from exc
    if version_i not in SUPPORTED_VERSIONS:
        raise BetslipValidationError(
            f"unsupported vai_betslip_version: {version_i}",
            code="UNSUPPORTED_VERSION",
        )

    date = str(data.get("date") or "").strip()
    track = str(data.get("track") or "").strip()
    game = str(data.get("game") or "V85").strip().upper() or "V85"
    if not date:
        raise BetslipValidationError("date is required", code="MISSING_DATE")
    if not track:
        raise BetslipValidationError("track is required", code="MISSING_TRACK")

    mode = str(data.get("mode") or "random").strip().lower()
    if mode not in MODES:
        raise BetslipValidationError(f"mode must be one of {sorted(MODES)}", code="INVALID_MODE")

    stake = data.get("stake_budget_sek", 500)
    try:
        stake_f = float(stake)
    except (TypeError, ValueError) as exc:
        raise BetslipValidationError("stake_budget_sek must be a number", code="INVALID_STAKE") from exc

    seed_raw = data.get("seed", None)
    seed: int | None
    if seed_raw is None or seed_raw == "":
        seed = None
    else:
        try:
            seed = int(seed_raw)
        except (TypeError, ValueError) as exc:
            raise BetslipValidationError("seed must be an integer or null", code="INVALID_SEED") from exc

    race_card_id = data.get("race_card_id")
    if race_card_id is not None:
        race_card_id = str(race_card_id).strip() or None

    selections = _normalize_leg_map(data.get("selections"), field="selections")
    operator_pools = _normalize_leg_map(data.get("operator_pools"), field="operator_pools")
    # If operator_pools omitted empty but selections present, treat selections as pools too.
    if data.get("operator_pools") is None and any(selections[str(i)] for i in range(1, NUM_LEGS + 1)):
        operator_pools = {k: list(v) for k, v in selections.items()}

    frozen_legs = _normalize_frozen(data.get("frozen_legs"))

    expert_raw = data.get("expert")
    expert: dict[str, Any] | None = None
    if expert_raw is not None:
        if not isinstance(expert_raw, dict):
            raise BetslipValidationError("expert must be a mapping", code="INVALID_EXPERT")
        tip_id = expert_raw.get("tip_id")
        expert_name = expert_raw.get("expert_name")
        expert = {
            "tip_id": str(tip_id).strip() if tip_id else None,
            "expert_name": str(expert_name).strip() if expert_name else None,
        }

    cost_sek = data.get("cost_sek")
    if cost_sek is not None:
        try:
            cost_sek = float(cost_sek)
        except (TypeError, ValueError) as exc:
            raise BetslipValidationError("cost_sek must be a number", code="INVALID_COST") from exc

    combinations = data.get("combinations")
    if combinations is not None:
        try:
            combinations = int(combinations)
        except (TypeError, ValueError) as exc:
            raise BetslipValidationError("combinations must be an integer", code="INVALID_COMBINATIONS") from exc

    saved_at = data.get("saved_at")
    if saved_at is not None:
        saved_at = str(saved_at)

    return {
        "vai_betslip_version": version_i,
        "saved_at": saved_at,
        "date": date,
        "track": track,
        "game": game,
        "race_card_id": race_card_id,
        "mode": mode,
        "stake_budget_sek": stake_f,
        "seed": seed,
        "frozen_legs": frozen_legs,
        "operator_pools": operator_pools,
        "selections": selections,
        "expert": expert,
        "cost_sek": cost_sek,
        "combinations": combinations,
    }


def parse_betslip_yaml(text: str) -> dict[str, Any]:
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise BetslipValidationError(f"YAML parse error: {exc}", code="YAML_ERROR") from exc
    return validate_betslip_payload(data)


def dump_betslip_yaml(data: dict[str, Any]) -> str:
    """Serialize a (possibly unvalidated) payload to YAML after validation."""
    payload = validate_betslip_payload(data)
    if not payload.get("saved_at"):
        payload["saved_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    # Drop null optional keys for cleaner files
    out: dict[str, Any] = {
        "vai_betslip_version": payload["vai_betslip_version"],
        "saved_at": payload["saved_at"],
        "date": payload["date"],
        "track": payload["track"],
        "game": payload["game"],
    }
    if payload.get("race_card_id"):
        out["race_card_id"] = payload["race_card_id"]
    out["mode"] = payload["mode"]
    out["stake_budget_sek"] = payload["stake_budget_sek"]
    if payload.get("seed") is not None:
        out["seed"] = payload["seed"]
    if payload.get("frozen_legs"):
        out["frozen_legs"] = payload["frozen_legs"]
    out["operator_pools"] = payload["operator_pools"]
    out["selections"] = payload["selections"]
    if payload.get("expert") and (
        payload["expert"].get("tip_id") or payload["expert"].get("expert_name")
    ):
        out["expert"] = {k: v for k, v in payload["expert"].items() if v}
    if payload.get("cost_sek") is not None:
        out["cost_sek"] = payload["cost_sek"]
    if payload.get("combinations") is not None:
        out["combinations"] = payload["combinations"]
    return yaml.safe_dump(out, allow_unicode=True, sort_keys=False, default_flow_style=None)


def save_betslip_file(
    data: dict[str, Any],
    *,
    directory: str | Path | None = None,
    repo_root: Path | None = None,
) -> Path:
    """Validate, choose unique name, write YAML under betslips/."""
    payload = validate_betslip_payload(data)
    root = Path(directory) if directory is not None else default_betslips_dir(repo_root)
    base = betslip_basename(payload["date"], payload["track"], payload["game"])
    path = next_available_path(root, base)
    path.write_text(dump_betslip_yaml(payload), encoding="utf-8")
    return path


def _is_yaml_name(name: str) -> bool:
    lower = name.lower()
    return lower.endswith(".yaml") or lower.endswith(".yml")


def safe_betslip_path(directory: str | Path, filename: str) -> Path:
    """Resolve filename under directory only; reject traversal and non-YAML names."""
    if not isinstance(filename, str) or not filename.strip():
        raise BetslipValidationError("filename is required", code="INVALID_FILENAME")
    name = filename.strip()
    if name != Path(name).name or "/" in name or "\\" in name or name in (".", ".."):
        raise BetslipValidationError(
            f"invalid betslip filename: {filename!r}",
            code="INVALID_FILENAME",
        )
    if ".." in name:
        raise BetslipValidationError(
            f"invalid betslip filename: {filename!r}",
            code="INVALID_FILENAME",
        )
    if not _is_yaml_name(name):
        raise BetslipValidationError(
            f"betslip must be .yaml or .yml: {name!r}",
            code="INVALID_FILENAME",
        )
    root = Path(directory).resolve()
    path = (root / name).resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise BetslipValidationError(
            f"path outside betslips directory: {filename!r}",
            code="INVALID_FILENAME",
        ) from exc
    return path


def load_betslip_file(directory: str | Path, filename: str) -> tuple[Path, dict[str, Any], str]:
    """Load and validate a betslip YAML. Returns (path, payload, raw_yaml)."""
    path = safe_betslip_path(directory, filename)
    if not path.is_file():
        raise BetslipValidationError(f"betslip not found: {path.name}", code="NOT_FOUND")
    text = path.read_text(encoding="utf-8")
    payload = parse_betslip_yaml(text)
    return path, payload, text


def delete_betslip_file(directory: str | Path, filename: str) -> Path:
    """Delete one betslip YAML under directory. Returns the path that was removed."""
    path = safe_betslip_path(directory, filename)
    if not path.is_file():
        raise BetslipValidationError(f"betslip not found: {path.name}", code="NOT_FOUND")
    path.unlink()
    return path


def delete_betslip_files(
    directory: str | Path,
    filenames: list[str],
) -> dict[str, Any]:
    """Delete multiple betslips. Returns {deleted: [...], failed: [{filename, code, message}]}."""
    deleted: list[str] = []
    failed: list[dict[str, str]] = []
    if not isinstance(filenames, list):
        raise BetslipValidationError("filenames must be a list", code="INVALID_BODY")
    for raw in filenames:
        name = str(raw) if raw is not None else ""
        try:
            delete_betslip_file(directory, name)
            deleted.append(Path(name.strip()).name if name.strip() else name)
        except BetslipValidationError as exc:
            failed.append(
                {
                    "filename": name,
                    "code": exc.code,
                    "message": str(exc),
                }
            )
    return {"deleted": deleted, "failed": failed}


def betslip_summary(filename: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Metadata dict for list API."""
    return {
        "filename": filename,
        "date": payload.get("date"),
        "track": payload.get("track"),
        "game": payload.get("game"),
        "mode": payload.get("mode"),
        "saved_at": payload.get("saved_at"),
        "cost_sek": payload.get("cost_sek"),
        "combinations": payload.get("combinations"),
        "stake_budget_sek": payload.get("stake_budget_sek"),
    }


def list_betslips(
    directory: str | Path,
    *,
    date: str | None = None,
    track: str | None = None,
) -> list[dict[str, Any]]:
    """List YAML betslips under directory (newest saved_at first). Skips invalid/non-YAML."""
    root = Path(directory)
    if not root.is_dir():
        return []
    date_f = (date or "").strip() or None
    track_slug_f = track_slug(track) if track else ""
    items: list[dict[str, Any]] = []
    for path in sorted(root.iterdir()):
        if not path.is_file() or not _is_yaml_name(path.name):
            continue
        try:
            text = path.read_text(encoding="utf-8")
            payload = parse_betslip_yaml(text)
        except (OSError, BetslipValidationError, UnicodeDecodeError):
            continue
        if date_f and payload.get("date") != date_f:
            continue
        if track_slug_f and track_slug(str(payload.get("track") or "")) != track_slug_f:
            continue
        items.append(betslip_summary(path.name, payload))
    items.sort(
        key=lambda m: (m.get("saved_at") or "", m.get("filename") or ""),
        reverse=True,
    )
    return items
