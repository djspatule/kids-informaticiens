"""
engine/missions.py — MissionLoader
Loads mission definitions from JSON files on disk.
"""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class MissionLoader:
    """
    Loads mission JSON files from a directory.

    Mission files are named mission_01.json, mission_02.json, etc.
    The directory is relative to the project source root (game.py location).
    """

    def __init__(self, missions_dir: str | Path):
        self.missions_dir = Path(missions_dir)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load_mission(self, mission_id: str) -> dict:
        """
        Load and return a mission dict.

        Returns a safe fallback dict if the file is missing or malformed.
        """
        path = self.missions_dir / f"{mission_id}.json"
        if not path.exists():
            logger.warning("Mission file not found: %s", path)
            return self._fallback_mission(mission_id)
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            logger.debug("Loaded mission %s from %s", mission_id, path)
            return data
        except (json.JSONDecodeError, OSError) as exc:
            logger.error("Could not load mission %s: %s", mission_id, exc)
            return self._fallback_mission(mission_id)

    def list_missions(self) -> list[str]:
        """Return sorted list of mission IDs available in the missions directory."""
        if not self.missions_dir.exists():
            logger.warning("Missions directory does not exist: %s", self.missions_dir)
            return []
        ids = [
            p.stem
            for p in sorted(self.missions_dir.glob("mission_*.json"))
        ]
        logger.debug("Found missions: %s", ids)
        return ids

    def count_missions(self) -> int:
        """Return the number of mission files available."""
        return len(self.list_missions())

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _fallback_mission(mission_id: str) -> dict:
        """Return a minimal valid mission dict for graceful degradation."""
        return {
            "id": mission_id,
            "title": f"Mission {mission_id}",
            "description": (
                "Cette mission n'est pas encore disponible. "
                "Demande de l'aide à Papa !"
            ),
            "hint": "Parle à Papa pour configurer cette mission.",
            "points": 10,
            "check": {"type": "never"},
            "success_message": "Mission terminée !",
        }
