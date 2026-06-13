"""
engine/state.py — StateManager
Handles loading, saving, and resetting player game state.
"""

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)


class StateManager:
    """Manages persistent game state for a player."""

    def __init__(self, player: str, config: dict):
        self.player = player
        self.config = config
        # Save path lives inside the player's game_dir
        save_dir = Path(config["game_dir"]) / "saves"
        self.save_path = save_dir / "state.json"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load(self) -> dict:
        """Load state from disk. Creates fresh state if file is missing or corrupt."""
        if self.save_path.exists():
            try:
                with open(self.save_path, "r", encoding="utf-8") as fh:
                    state = json.load(fh)
                state = self.migrate_state(state)
                logger.info("State loaded from %s", self.save_path)
                return state
            except (json.JSONDecodeError, OSError) as exc:
                logger.warning("Could not read state file (%s) — creating fresh state", exc)
        return self._create_fresh(self.player, self.config)

    def save(self, state: dict) -> None:
        """Write state to disk atomically (write to tmp, rename)."""
        try:
            self.save_path.parent.mkdir(parents=True, exist_ok=True)
            tmp_path = self.save_path.with_suffix(".tmp")
            with open(tmp_path, "w", encoding="utf-8") as fh:
                json.dump(state, fh, indent=2, ensure_ascii=False)
            tmp_path.replace(self.save_path)
            logger.debug("State saved to %s", self.save_path)
        except OSError as exc:
            logger.error("Failed to save state: %s", exc)

    def reset(self, config: dict) -> dict:
        """Delete the save file and return a brand-new state."""
        try:
            if self.save_path.exists():
                self.save_path.unlink()
                logger.info("Save file deleted: %s", self.save_path)
        except OSError as exc:
            logger.warning("Could not delete save file: %s", exc)
        fresh = self._create_fresh(self.player, config)
        self.save(fresh)
        return fresh

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def migrate_state(self, state: dict) -> dict:
        """Add missing fields to old save files (backward compat)."""
        if "current_level" not in state:
            state["current_level"] = 1
        if "completed_levels" not in state:
            state["completed_levels"] = []
        if "level_rewards" not in state:
            state["level_rewards"] = {}
        return state

    @staticmethod
    def _create_fresh(player: str, config: dict) -> dict:
        """Return a new, empty state dict for the given player."""
        now_iso = datetime.now(timezone.utc).isoformat()
        return {
            "player": player,
            "profile": config.get("profile", "easy"),
            "current_mission": config.get("first_mission", "mission_01"),
            "completed": [],
            "mission_start_time": now_iso,
            "initial_wallpaper": "",
            "last_check": now_iso,
            "final_reward_unlocked": False,
            "secret_code": None,
            "hints_used": 0,
            "score": 0,
            "version": 1,
            "current_level": 1,
            "completed_levels": [],
            "level_rewards": {},
        }
