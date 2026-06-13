#!/usr/bin/env python3
"""
game.py — Mission Espace: entry point.

Usage:
    python3 game.py romy
    python3 game.py oscar
    python3 game.py romy --reset
    python3 game.py romy --status
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Resolve project root early so all relative imports work regardless of cwd
# ---------------------------------------------------------------------------
SOURCE_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SOURCE_DIR))

# ---------------------------------------------------------------------------
# Logging — write to logs/<player>.log AND stderr at WARNING+
# ---------------------------------------------------------------------------

def _setup_logging(player: str, level_name: str = "INFO") -> None:
    log_dir = SOURCE_DIR / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"{player}.log"

    level = getattr(logging, level_name.upper(), logging.INFO)
    fmt = "%(asctime)s %(levelname)-8s %(name)s — %(message)s"
    datefmt = "%Y-%m-%dT%H:%M:%SZ"

    root = logging.getLogger()
    root.setLevel(level)

    # File handler — full detail
    try:
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setLevel(level)
        fh.setFormatter(logging.Formatter(fmt, datefmt=datefmt))
        root.addHandler(fh)
    except OSError as exc:
        # Can't write log file (e.g. permission denied) — continue without it
        print(f"Warning: cannot open log file {log_file}: {exc}", file=sys.stderr)

    # Console handler — warnings and above only (don't pollute terminal)
    ch = logging.StreamHandler(sys.stderr)
    ch.setLevel(logging.WARNING)
    ch.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    root.addHandler(ch)


logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------

def _load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _load_config(player: str) -> dict:
    config_dir = SOURCE_DIR / "config"
    global_cfg  = _load_json(config_dir / "global.json")
    player_cfg  = _load_json(config_dir / f"{player}.json")
    # Merge: player-specific values take priority
    merged = {**global_cfg, **player_cfg}
    # Always record where the source code lives
    merged["source_dir"] = str(SOURCE_DIR)
    return merged


# ---------------------------------------------------------------------------
# --status helper
# ---------------------------------------------------------------------------

def _print_status(player: str, config: dict) -> None:
    from engine.state import StateManager
    sm = StateManager(player, config)
    state = sm.load()

    total = config.get("total_missions", "?")
    completed = state.get("completed", [])
    current = state.get("current_mission", "N/A")
    score = state.get("score", 0)
    hints = state.get("hints_used", 0)
    reward = state.get("final_reward_unlocked", False)

    current_level = state.get("current_level", 1)
    rewards = state.get("level_rewards", {})

    print(f"\n=== Mission Espace — Statut de {config.get('display_name', player)} ===")
    print(f"  Missions terminées : {len(completed)} / {total}")
    print(f"  Mission en cours   : {current}")
    print(f"  Score              : {score} pts")
    print(f"  Indices utilisés   : {hints}")
    print(f"  Niveau actuel      : {current_level} / 4")
    if rewards:
        print(f"  Codes de niveau    : {', '.join(rewards.values())}")
    print(f"  Récompense finale  : {'OUI 🏆' if reward else 'pas encore'}")
    if completed:
        print(f"  Complétées         : {', '.join(completed)}")
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    player = args[0].lower().strip()
    flags  = set(args[1:])

    # Validate player name
    config_path = SOURCE_DIR / "config" / f"{player}.json"
    if not config_path.exists():
        print(f"Erreur : joueur inconnu '{player}'.", file=sys.stderr)
        print(f"Joueurs disponibles : romy, oscar", file=sys.stderr)
        sys.exit(1)

    # Load configuration
    try:
        config = _load_config(player)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"Erreur de configuration : {exc}", file=sys.stderr)
        sys.exit(1)

    _setup_logging(player, config.get("log_level", "INFO"))
    logger.info("=== Mission Espace démarré — joueur: %s ===", player)

    # ------------------------------------------------------------------
    # Handle --reset
    # ------------------------------------------------------------------
    if "--reset" in flags:
        from engine.state import StateManager
        sm = StateManager(player, config)
        sm.reset(config)
        print(f"Partie de {config.get('display_name', player)} réinitialisée.")
        logger.info("State reset for player %s", player)
        # Fall through and start the GUI with fresh state

    # ------------------------------------------------------------------
    # Handle --status (print and exit)
    # ------------------------------------------------------------------
    if "--status" in flags:
        _print_status(player, config)
        sys.exit(0)

    # ------------------------------------------------------------------
    # Normal game launch
    # ------------------------------------------------------------------
    from engine.state    import StateManager
    from engine.missions import MissionLoader
    from engine.checker  import CheckRunner
    from engine.gui      import MissionWindow
    from engine          import notifier

    # Resolve missions directory relative to project source
    missions_dir = SOURCE_DIR / config["missions_dir"]

    sm = StateManager(player, config)
    ml = MissionLoader(missions_dir)
    state = sm.load()

    # Record initial wallpaper if not already stored
    if not state.get("initial_wallpaper"):
        try:
            from checks.desktop_checks import get_xfce_wallpaper
            wallpaper = get_xfce_wallpaper() or ""
            state["initial_wallpaper"] = wallpaper
            sm.save(state)
            logger.info("Initial wallpaper recorded: %s", wallpaper)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Could not record initial wallpaper: %s", exc)

    cr = CheckRunner(state, config)

    notifier.log_event(player, "GAME_START", f"version={config.get('version', '?')}")
    notifier.send_notification(
        f"🚀 Bonjour {config.get('display_name', player)} !",
        "Ta mission spatiale commence maintenant. Bonne chance !",
        timeout_ms=5000,
    )

    logger.info(
        "Starting GUI — current_mission=%s score=%d",
        state.get("current_mission"), state.get("score", 0),
    )

    try:
        app = MissionWindow(player, config, sm, ml, cr)
        app.mainloop()
    except KeyboardInterrupt:
        logger.info("Game interrupted by user.")
    except Exception as exc:  # noqa: BLE001
        logger.critical("Fatal GUI error: %s", exc, exc_info=True)
        print(
            "\nErreur fatale dans le jeu. Consulte les logs pour plus de détails.",
            file=sys.stderr,
        )
        sys.exit(1)

    logger.info("=== Mission Espace terminé — joueur: %s ===", player)
    notifier.log_event(player, "GAME_EXIT")


if __name__ == "__main__":
    main()
