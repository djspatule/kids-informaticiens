#!/usr/bin/env python3
"""
tests/test_missions.py — Validate all mission JSON files.

Run: python3 tests/test_missions.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
MISSIONS_DIR = ROOT / "missions"

REQUIRED_FIELDS = {"id", "level", "title", "description", "hint", "check", "success_message", "points"}
VALID_CHECK_TYPES = {
    "file_exists", "file_not_exists", "file_accessed", "file_contains",
    "folder_exists", "file_moved", "file_renamed", "wallpaper_changed",
    "all_of", "any_of", "always", "never",
}

PLAYER_CONFIG = {
    "romy":  {"total": 30, "levels": 4},
    "oscar": {"total": 34, "levels": 4},
}

ERRORS = []
WARNINGS = []

def err(msg): ERRORS.append(msg)
def warn(msg): WARNINGS.append(msg)


def validate_check(check, mission_path, depth=0):
    if depth > 5:
        err(f"{mission_path}: check nesting too deep")
        return
    if not isinstance(check, dict):
        err(f"{mission_path}: check must be a dict, got {type(check)}")
        return
    t = check.get("type")
    if t not in VALID_CHECK_TYPES:
        err(f"{mission_path}: unknown check type {t!r}")
    if t in ("all_of", "any_of"):
        subs = check.get("checks", [])
        if not subs:
            warn(f"{mission_path}: {t} has empty checks list")
        for sub in subs:
            validate_check(sub, mission_path, depth + 1)


def test_player(player):
    player_dir = MISSIONS_DIR / player
    if not player_dir.exists():
        err(f"missions/{player}/ does not exist")
        return

    files = sorted(player_dir.glob("mission_*.json"))
    if not files:
        err(f"missions/{player}/ has no mission JSON files")
        return

    missions = []
    for f in files:
        try:
            m = json.load(f.open(encoding="utf-8"))
        except json.JSONDecodeError as e:
            err(f"{f.name}: invalid JSON — {e}")
            continue
        missions.append((f.name, m))

    print(f"\n  {player}: {len(missions)} missions found")

    # Check required fields
    for fname, m in missions:
        missing = REQUIRED_FIELDS - set(m.keys())
        if missing:
            err(f"{player}/{fname}: missing fields: {missing}")

        # Validate check structure
        if "check" in m:
            validate_check(m["check"], f"{player}/{fname}")

        # Level field
        level = m.get("level")
        if not isinstance(level, int) or level < 1 or level > 4:
            err(f"{player}/{fname}: 'level' must be int 1-4, got {level!r}")

        # Points
        pts = m.get("points", 0)
        if not isinstance(pts, (int, float)) or pts <= 0:
            warn(f"{player}/{fname}: unusual points value {pts!r}")

        # Image field: if present, check file exists (after generate_assets.py)
        img = m.get("image")
        if img:
            img_path = ROOT / img
            if not img_path.exists():
                warn(f"{player}/{fname}: image {img!r} not found (run generate_assets.py?)")

    # Level continuity: each level 1..4 must have at least 1 mission
    level_counts = {}
    for _, m in missions:
        lvl = m.get("level", 0)
        level_counts[lvl] = level_counts.get(lvl, 0) + 1

    for lvl in range(1, 5):
        if lvl not in level_counts:
            err(f"{player}: no missions found for level {lvl}")

    # Mission IDs must match filenames
    for fname, m in missions:
        expected_id = fname.replace(".json", "")
        if m.get("id") != expected_id:
            err(f"{player}/{fname}: id={m.get('id')!r} doesn't match filename")

    # Sequential numbering: mission_01, mission_02, ...
    stems = [f.stem for f, _ in [(MISSIONS_DIR / player / fname, m) for fname, m in missions]]
    for i, stem in enumerate(stems, 1):
        expected = f"mission_{i:02d}"
        if stem != expected:
            warn(f"{player}: expected {expected}, got {stem}")

    print(f"    Level distribution: {dict(sorted(level_counts.items()))}")
    return len(missions)


def test_configs():
    config_dir = ROOT / "config"
    for player in ("romy", "oscar"):
        cfg_path = config_dir / f"{player}.json"
        if not cfg_path.exists():
            err(f"config/{player}.json missing")
            continue
        try:
            cfg = json.load(cfg_path.open(encoding="utf-8"))
        except json.JSONDecodeError as e:
            err(f"config/{player}.json: invalid JSON — {e}")
            continue

        # Check levels field
        if "levels" not in cfg:
            err(f"config/{player}.json: missing 'levels' field")
        else:
            levels = cfg["levels"]
            if not isinstance(levels, list) or len(levels) != 4:
                err(f"config/{player}.json: 'levels' must be list of 4, got {len(levels)}")
            else:
                for i, lvl in enumerate(levels, 1):
                    for field in ("id", "name", "reward", "missions_count"):
                        if field not in lvl:
                            err(f"config/{player}.json: level {i} missing field {field!r}")

        # Check total_missions
        if "total_missions" not in cfg:
            warn(f"config/{player}.json: missing 'total_missions'")


def main():
    print("=" * 50)
    print("Mission Espace — Mission JSON Validation")
    print("=" * 50)

    test_configs()

    total_romy = test_player("romy")
    total_oscar = test_player("oscar")

    print(f"\n  Total: {total_romy} romy missions, {total_oscar} oscar missions")

    print("\n" + "=" * 50)
    if WARNINGS:
        print(f"WARNINGS ({len(WARNINGS)}):")
        for w in WARNINGS:
            print(f"  ⚠  {w}")
    if ERRORS:
        print(f"\nERRORS ({len(ERRORS)}):")
        for e in ERRORS:
            print(f"  ✗  {e}")
        print(f"\nFAILED — {len(ERRORS)} error(s)")
        sys.exit(1)
    else:
        print("ALL TESTS PASSED ✓")
        sys.exit(0)


if __name__ == "__main__":
    main()
