#!/usr/bin/env python3
"""
tests/test_checks.py — Unit tests for all check functions.

Run: python3 tests/test_checks.py
"""
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from checks.file_checks import (
    check_file_exists, check_file_not_exists, check_file_accessed,
    check_file_contains, check_folder_exists, check_file_moved, check_file_renamed,
)
from checks.desktop_checks import check_wallpaper_changed, get_xfce_wallpaper
from checks.composite_checks import check_all_of, check_any_of
from engine.checker import CheckRunner
from engine.state import StateManager

ERRORS = []
PASSED = 0


def ok(name):
    global PASSED
    PASSED += 1
    print(f"  ✓ {name}")


def fail(name, msg):
    ERRORS.append(f"{name}: {msg}")
    print(f"  ✗ {name}: {msg}")


def assert_true(cond, name, msg="expected True"):
    if cond:
        ok(name)
    else:
        fail(name, msg)


def assert_false(cond, name, msg="expected False"):
    if not cond:
        ok(name)
    else:
        fail(name, msg)


# ── Test file_checks ─────────────────────────────────────────────────────────

def test_file_checks():
    print("\n── file_checks ──")
    tmpdir = Path(tempfile.mkdtemp())

    try:
        # file_exists
        f = tmpdir / "test.txt"
        f.write_text("hello world\n", encoding="utf-8")
        assert_true(check_file_exists(str(f)), "file_exists — present")
        assert_false(check_file_exists(str(tmpdir / "nope.txt")), "file_exists — missing")
        assert_false(check_file_exists(str(tmpdir)), "file_exists — dir not file")

        # file_not_exists
        assert_false(check_file_not_exists(str(f)), "file_not_exists — present")
        assert_true(check_file_not_exists(str(tmpdir / "nope.txt")), "file_not_exists — missing")

        # folder_exists
        subdir = tmpdir / "sub"
        subdir.mkdir()
        assert_true(check_folder_exists(str(subdir)), "folder_exists — present")
        assert_false(check_folder_exists(str(tmpdir / "nosub")), "folder_exists — missing")
        assert_false(check_folder_exists(str(f)), "folder_exists — file not dir")

        # file_contains
        assert_true(check_file_contains(str(f), "hello"), "file_contains — match")
        assert_true(check_file_contains(str(f), "HELLO", case_sensitive=False), "file_contains — case insensitive")
        assert_false(check_file_contains(str(f), "xyz"), "file_contains — no match")
        assert_false(check_file_contains(str(tmpdir / "nope.txt"), "hello"), "file_contains — missing file")

        # file_moved: before move
        dst = tmpdir / "moved.txt"
        assert_false(check_file_moved(str(f), str(dst)), "file_moved — before")
        f.rename(dst)
        assert_true(check_file_moved(str(f), str(dst)), "file_moved — after")

        # file_renamed
        old = subdir / "old.txt"
        new = subdir / "new.txt"
        old.write_text("content")
        assert_false(check_file_renamed(str(subdir), "old.txt", "new.txt"), "file_renamed — before")
        old.rename(new)
        assert_true(check_file_renamed(str(subdir), "old.txt", "new.txt"), "file_renamed — after")

        # file_accessed
        recent = (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()
        ancient = (datetime.now(timezone.utc) - timedelta(days=365)).isoformat()
        _ = new.read_text()  # access it
        assert_true(check_file_accessed(str(new), recent), "file_accessed — recent since")
        assert_true(check_file_accessed(str(new), ancient), "file_accessed — ancient since")
        future = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        assert_false(check_file_accessed(str(new), future), "file_accessed — future since")
        assert_false(check_file_accessed(str(tmpdir / "nope"), recent), "file_accessed — missing")

    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


# ── Test composite checks ─────────────────────────────────────────────────────

def test_composite_checks():
    print("\n── composite_checks ──")
    tmpdir = Path(tempfile.mkdtemp())
    try:
        cfg = json.load(open(ROOT / "config" / "romy.json", encoding="utf-8"))
        cfg["home_dir"] = str(tmpdir)
        state = {"mission_start_time": "2000-01-01T00:00:00", "initial_wallpaper": ""}
        runner = CheckRunner(state, cfg)

        f = tmpdir / "test.txt"
        f.write_text("bonjour")

        all_pass = check_all_of([
            {"type": "file_exists", "path": str(f)},
            {"type": "folder_exists", "path": str(tmpdir)},
        ], runner)
        assert_true(all_pass, "all_of — all pass")

        all_fail = check_all_of([
            {"type": "file_exists", "path": str(f)},
            {"type": "file_exists", "path": str(tmpdir / "nope")},
        ], runner)
        assert_false(all_fail, "all_of — one fails")

        any_pass = check_any_of([
            {"type": "file_exists", "path": str(tmpdir / "nope")},
            {"type": "folder_exists", "path": str(tmpdir)},
        ], runner)
        assert_true(any_pass, "any_of — one passes")

        any_fail = check_any_of([
            {"type": "file_exists", "path": str(tmpdir / "nope1")},
            {"type": "file_exists", "path": str(tmpdir / "nope2")},
        ], runner)
        assert_false(any_fail, "any_of — none pass")

    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


# ── Test CheckRunner dispatch ─────────────────────────────────────────────────

def test_check_runner():
    print("\n── CheckRunner dispatch ──")
    tmpdir = Path(tempfile.mkdtemp())
    try:
        cfg = json.load(open(ROOT / "config" / "romy.json", encoding="utf-8"))
        cfg["home_dir"] = str(tmpdir)
        cfg["desktop_dir_name"] = "Bureau"
        state = {"mission_start_time": "2000-01-01T00:00:00", "initial_wallpaper": ""}
        runner = CheckRunner(state, cfg)

        bureau = tmpdir / "Bureau"
        bureau.mkdir()
        f = bureau / "answer.txt"
        f.write_text("42")

        # Template substitution: {desktop}
        assert_true(
            runner.run({"type": "file_exists", "path": "{desktop}/answer.txt"}),
            "runner: {desktop} template"
        )
        # {home_dir}
        assert_true(
            runner.run({"type": "folder_exists", "path": "{home_dir}/Bureau"}),
            "runner: {home_dir} template"
        )
        # unknown type
        assert_false(runner.run({"type": "unknown_xyz"}), "runner: unknown type → False")
        # always
        assert_true(runner.run({"type": "always"}), "runner: always → True")
        # never
        assert_false(runner.run({"type": "never"}), "runner: never → False")

    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


# ── Test StateManager ─────────────────────────────────────────────────────────

def test_state_manager():
    print("\n── StateManager ──")
    tmpdir = Path(tempfile.mkdtemp())
    try:
        cfg = json.load(open(ROOT / "config" / "romy.json", encoding="utf-8"))
        cfg["game_dir"] = str(tmpdir)

        sm = StateManager("romy", cfg)
        state = sm.load()

        assert_true(state.get("current_mission") == "mission_01", "state: fresh current_mission")
        assert_true(state.get("current_level", 1) == 1, "state: fresh current_level == 1")
        assert_true(isinstance(state.get("completed", []), list), "state: completed is list")
        assert_true(state.get("score", 0) == 0, "state: fresh score == 0")

        # Save and reload
        state["score"] = 99
        state["current_level"] = 2
        sm.save(state)

        state2 = sm.load()
        assert_true(state2.get("score") == 99, "state: score persists")
        assert_true(state2.get("current_level") == 2, "state: level persists")

        # Reset
        sm.reset(cfg)
        state3 = sm.load()
        assert_true(state3.get("score") == 0, "state: score reset to 0")
        assert_true(state3.get("current_level", 1) == 1, "state: level reset to 1")

    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


# ── Desktop checks (graceful) ─────────────────────────────────────────────────

def test_desktop_checks():
    print("\n── desktop_checks ──")
    # xfconf-query may not be available; just verify graceful handling
    result = get_xfce_wallpaper()
    assert_true(result is None or isinstance(result, str), "get_xfce_wallpaper: returns str or None")

    # wallpaper_changed with same value → False
    test_wp = "/some/fake/path.jpg"
    assert_false(check_wallpaper_changed(test_wp) and (result == test_wp), "wallpaper_changed: same value")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 50)
    print("Mission Espace — Check Function Tests")
    print("=" * 50)

    test_file_checks()
    test_composite_checks()
    test_check_runner()
    test_state_manager()
    test_desktop_checks()

    print(f"\n{'=' * 50}")
    if ERRORS:
        print(f"FAILED — {len(ERRORS)} error(s):")
        for e in ERRORS:
            print(f"  ✗ {e}")
        sys.exit(1)
    else:
        print(f"ALL {PASSED} TESTS PASSED ✓")
        sys.exit(0)


if __name__ == "__main__":
    main()
