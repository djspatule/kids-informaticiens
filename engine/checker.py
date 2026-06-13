"""
engine/checker.py — CheckRunner
Dispatches mission check specifications to their implementation functions.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Lazy imports of check modules (avoids import-time side effects)
# ---------------------------------------------------------------------------

def _file_checks():
    from checks import file_checks
    return file_checks


def _desktop_checks():
    from checks import desktop_checks
    return desktop_checks


def _composite_checks():
    from checks import composite_checks
    return composite_checks


class CheckRunner:
    """
    Evaluates a check specification dict and returns True/False.

    A check_spec is a dict with at least a "type" key, e.g.:
        {"type": "file_exists", "path": "~/Bureau/mon_fichier.txt"}
    """

    def __init__(self, state: dict, config: dict):
        self.state = state
        self.config = config

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self, check_spec: dict) -> bool:
        """
        Dispatch a check spec to the appropriate implementation.

        Returns False (not True!) on unknown or misconfigured specs so that
        kids are never accidentally marked as having passed a broken check.
        """
        if not isinstance(check_spec, dict):
            logger.warning("check_spec is not a dict: %r", check_spec)
            return False

        check_type = check_spec.get("type", "")

        try:
            return self._dispatch(check_type, check_spec)
        except Exception as exc:  # noqa: BLE001
            logger.error(
                "Unexpected error running check type=%r: %s", check_type, exc,
                exc_info=True,
            )
            return False

    # ------------------------------------------------------------------
    # Dispatch table
    # ------------------------------------------------------------------

    def _dispatch(self, check_type: str, spec: dict) -> bool:
        fc = _file_checks()
        dc = _desktop_checks()
        cc = _composite_checks()

        match check_type:
            # ---- file system ----
            case "file_exists":
                return fc.check_file_exists(self._sub(spec, "path"))

            case "file_not_exists":
                return fc.check_file_not_exists(self._sub(spec, "path"))

            case "file_accessed":
                return fc.check_file_accessed(
                    self._sub(spec, "path"),
                    spec.get("since", self.state.get("mission_start_time", "")),
                )

            case "file_contains":
                return fc.check_file_contains(
                    self._sub(spec, "path"),
                    spec.get("text", ""),
                    spec.get("case_sensitive", False),
                )

            case "folder_exists":
                return fc.check_folder_exists(self._sub(spec, "path"))

            case "file_moved":
                return fc.check_file_moved(
                    self._sub(spec, "src"),
                    self._sub(spec, "dst"),
                )

            case "file_renamed":
                return fc.check_file_renamed(
                    self._sub(spec, "dir"),
                    spec.get("old_name", ""),
                    spec.get("new_name", ""),
                )

            # ---- desktop ----
            case "wallpaper_changed":
                initial = spec.get(
                    "initial_wallpaper",
                    self.state.get("initial_wallpaper", ""),
                )
                return dc.check_wallpaper_changed(initial)

            # ---- composites ----
            case "all_of":
                return cc.check_all_of(spec.get("checks", []), self)

            case "any_of":
                return cc.check_any_of(spec.get("checks", []), self)

            # ---- special values ----
            case "always":
                # Useful for testing/demo missions that pass immediately
                return True

            case "never":
                # Placeholder for unimplemented missions
                return False

            case _:
                logger.warning("Unknown check type: %r", check_type)
                return False

    # ------------------------------------------------------------------
    # Template substitution helpers
    # ------------------------------------------------------------------

    def _sub(self, spec: dict, key: str) -> str:
        """
        Return spec[key], substituting template variables from config/state.

        Supported placeholders (in the JSON value strings):
          {home_dir}   → config["home_dir"]
          {game_dir}   → config["game_dir"]
          {desktop}    → config["home_dir"] / config["desktop_dir_name"]
          {player}     → config["player"]
        """
        raw = spec.get(key, "")
        if not isinstance(raw, str):
            return str(raw)

        home = self.config.get("home_dir", "~")
        desktop_name = self.config.get("desktop_dir_name", "Bureau")

        return (
            raw
            .replace("{home_dir}", home)
            .replace("{game_dir}", self.config.get("game_dir", ""))
            .replace("{desktop}", f"{home}/{desktop_name}")
            .replace("{player}", self.config.get("player", ""))
        )
