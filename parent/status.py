#!/usr/bin/env python3
"""
parent/status.py — Tableau de bord parents pour Mission Espace
Usage: python3 parent/status.py

Utilise uniquement la bibliothèque standard Python.
Lit les fichiers de sauvegarde JSON des joueurs et affiche un résumé lisible.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Chemins (ce script vit dans parent/, le projet est un niveau au-dessus)
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent

# ---------------------------------------------------------------------------
# Codes ANSI
# ---------------------------------------------------------------------------
RESET   = "\033[0m"
BOLD    = "\033[1m"
DIM     = "\033[2m"
RED     = "\033[0;31m"
GREEN   = "\033[0;32m"
YELLOW  = "\033[1;33m"
BLUE    = "\033[0;34m"
MAGENTA = "\033[0;35m"
CYAN    = "\033[0;36m"
WHITE   = "\033[0;37m"

# Couleurs des joueurs
ROMY_COLOR  = "\033[38;5;213m"   # rose/violet pâle
OSCAR_COLOR = "\033[38;5;80m"    # bleu-vert

# ---------------------------------------------------------------------------
# Chargement des configurations
# ---------------------------------------------------------------------------

def load_json(path: Path) -> dict:
    """Charge un JSON depuis un fichier. Retourne {} si absent ou invalide."""
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}


def load_player_config(player: str) -> dict:
    cfg_path = PROJECT_ROOT / "config" / f"{player}.json"
    cfg = load_json(cfg_path)
    if not cfg:
        print(f"{YELLOW}[WARN]{RESET} Config introuvable : {cfg_path}", file=sys.stderr)
    return cfg


def load_global_config() -> dict:
    return load_json(PROJECT_ROOT / "config" / "global.json")


def load_state(save_file: str) -> dict | None:
    """Charge l'état du joueur. Retourne None si la partie n'a pas encore commencé."""
    try:
        p = Path(save_file)
        if not p.exists():
            return None
        data = load_json(p)
        return data if data else None
    except (PermissionError, OSError):
        return None


# ---------------------------------------------------------------------------
# Chargement des missions (pour compter les points totaux)
# ---------------------------------------------------------------------------

def load_missions(missions_dir: str) -> dict[str, dict]:
    """Retourne un dict {mission_id: mission_data} pour le répertoire donné."""
    try:
        d = PROJECT_ROOT / missions_dir
        missions: dict[str, dict] = {}
        if not d.exists():
            return missions
        for path in sorted(d.glob("mission_*.json")):
            data = load_json(path)
            if data:
                missions[path.stem] = data
        return missions
    except (PermissionError, OSError):
        return {}


def total_points(missions: dict[str, dict]) -> int:
    return sum(m.get("points", 0) for m in missions.values())


# ---------------------------------------------------------------------------
# Formateurs
# ---------------------------------------------------------------------------

def format_timedelta(dt_iso: str) -> str:
    """Convertit un ISO-8601 en 'il y a X minutes/heures/jours'."""
    if not dt_iso:
        return "jamais"
    try:
        dt = datetime.fromisoformat(dt_iso)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        delta = now - dt
        secs = int(delta.total_seconds())
        if secs < 0:
            return "à l'instant"
        if secs < 60:
            return f"il y a {secs} seconde{'s' if secs != 1 else ''}"
        minutes = secs // 60
        if minutes < 60:
            return f"il y a {minutes} minute{'s' if minutes != 1 else ''}"
        hours = minutes // 60
        if hours < 24:
            return f"il y a {hours} heure{'s' if hours != 1 else ''}"
        days = hours // 24
        return f"il y a {days} jour{'s' if days != 1 else ''}"
    except (ValueError, OverflowError):
        return dt_iso


def mission_id_to_number(mission_id: str) -> int:
    """Extrait le numéro d'une mission_id comme 'mission_03' → 3."""
    try:
        return int(mission_id.split("_")[-1])
    except (ValueError, IndexError):
        return 0


def progress_bar(current: int, total: int, width: int = 20) -> str:
    """Barre de progression ASCII."""
    if total == 0:
        return f"[{'─' * width}]"
    filled = int(width * current / total)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}]"


# ---------------------------------------------------------------------------
# Affichage d'un joueur
# ---------------------------------------------------------------------------

def print_player_section(
    player: str,
    color: str,
    config: dict,
    state: dict | None,
    missions: dict[str, dict],
    global_cfg: dict,
) -> None:
    role  = config.get("role_title", player.capitalize())
    total = config.get("total_missions", len(missions))
    max_pts = total_points(missions)
    hint_penalty = global_cfg.get("hint_penalty_points", 5)

    # En-tête joueur
    print(f"\n{color}{BOLD}{'─' * 48}{RESET}")
    print(f"{color}{BOLD}  {'👧' if player == 'romy' else '👦'} {player.upper()} ({role}){RESET}")
    print(f"{color}{'─' * 48}{RESET}")

    if state is None:
        print(f"  {DIM}(Aucune partie commencée — le jeu n'a pas encore été lancé){RESET}")
        return

    # Mission actuelle
    current_mission_id = state.get("current_mission", "mission_01")
    completed: list[str] = state.get("completed", [])
    num_completed = len(completed)
    num_current = mission_id_to_number(current_mission_id)
    current_mission_data = missions.get(current_mission_id, {})
    current_title = current_mission_data.get("title", current_mission_id)

    # Niveau actuel
    current_level = state.get("current_level", 1)
    level_rewards = state.get("level_rewards", {})
    completed_levels = state.get("completed_levels", [])
    levels_cfg = config.get("levels", [])
    num_levels = len(levels_cfg) if levels_cfg else 4
    current_level_name = ""
    for lvl in levels_cfg:
        if lvl.get("id") == current_level:
            current_level_name = lvl.get("name", "")
            break

    # Score
    score = state.get("score", 0)
    hints_used = state.get("hints_used", 0)
    hints_penalty = hints_used * hint_penalty

    # Progression
    bar = progress_bar(num_completed, total)
    print(f"  Mission actuelle  : {BOLD}{num_current}/{total}{RESET} — {current_title}")
    print(f"  Progression       : {color}{bar}{RESET} {num_completed}/{total} terminées")

    # Niveau
    level_label = f"{current_level} / {num_levels}"
    if current_level_name:
        level_label += f" — {current_level_name}"
    print(f"  Niveau actuel     : {BOLD}{level_label}{RESET}")

    # Récompenses de niveaux débloqués
    if level_rewards:
        for lvl_id_str, reward_code in sorted(level_rewards.items()):
            print(f"  Codes débloqués   : {GREEN}{reward_code}{RESET} {DIM}(niveau {lvl_id_str}){RESET}")
    elif completed_levels:
        print(f"  Niveaux terminés  : {GREEN}{len(completed_levels)}{RESET} / {num_levels}")

    # Missions complétées
    if completed:
        done_str = "  ".join(
            f"{GREEN}✓{RESET} {mid.replace('mission_', 'm')}" for mid in completed
        )
        print(f"  Terminées         : {done_str}")
    else:
        print(f"  Terminées         : {DIM}(aucune encore){RESET}")

    # Score
    print(f"  Score             : {BOLD}{score}{RESET} / {max_pts} points", end="")
    if hints_penalty > 0:
        print(f"  {DIM}(−{hints_penalty} pts pour {hints_used} indice{'s' if hints_used != 1 else ''}){RESET}", end="")
    print()

    # Indices
    if hints_used == 0:
        print(f"  Indices utilisés  : {GREEN}0{RESET} {DIM}(parfait!){RESET}")
    else:
        print(f"  Indices utilisés  : {YELLOW}{hints_used}{RESET}")

    # Trésor final
    if state.get("final_reward_unlocked"):
        secret_code = state.get("secret_code") or config.get("secret_code", "???")
        print(f"  {BOLD}{GREEN}🏆 JEUX TERMINÉ ! Code secret : {secret_code}{RESET}")

    # Dernière activité
    last_check = state.get("last_check", "")
    print(f"  Dernière activité : {DIM}{format_timedelta(last_check)}{RESET}")


# ---------------------------------------------------------------------------
# Point d'entrée
# ---------------------------------------------------------------------------

def main() -> None:
    global_cfg = load_global_config()

    # Bannière
    print()
    print(f"{CYAN}{BOLD}╔══════════════════════════════════════════════╗{RESET}")
    print(f"{CYAN}{BOLD}║     🚀  MISSION ESPACE — TABLEAU DE BORD   ║{RESET}")
    print(f"{CYAN}{BOLD}║               PARENTS                       ║{RESET}")
    print(f"{CYAN}{BOLD}╚══════════════════════════════════════════════╝{RESET}")
    print(f"  {DIM}Version {global_cfg.get('version', '?')} — {datetime.now().strftime('%d/%m/%Y %H:%M')}{RESET}")

    # Joueurs à afficher
    players = [
        ("romy",  ROMY_COLOR),
        ("oscar", OSCAR_COLOR),
    ]

    for player, color in players:
        cfg = load_player_config(player)
        if not cfg:
            print(f"\n{YELLOW}[WARN]{RESET} Configuration introuvable pour {player} — ignoré.")
            continue

        save_file = cfg.get("save_file", f"/home/{player}/game/saves/state.json")
        missions_dir = cfg.get("missions_dir", f"missions/{player}")

        state    = load_state(save_file)
        missions = load_missions(missions_dir)

        print_player_section(player, color, cfg, state, missions, global_cfg)

    # Séparateur final
    print(f"\n{CYAN}{BOLD}{'─' * 48}{RESET}")

    # Commandes utiles
    src = global_cfg.get("source_dir", str(PROJECT_ROOT))
    print(f"\n{BOLD}💡 Commandes utiles :{RESET}")
    print(f"   {DIM}# Lancer le jeu pour un joueur :{RESET}")
    print(f"   python3 {src}/game.py romy")
    print(f"   python3 {src}/game.py oscar")
    print()
    print(f"   {DIM}# Réinitialiser complètement un joueur :{RESET}")
    print(f"   sudo bash {src}/setup/reset_player.sh romy")
    print(f"   sudo bash {src}/setup/reset_player.sh oscar")
    print()
    print(f"   {DIM}# Réinitialiser seulement la progression (sans recréer les fichiers) :{RESET}")
    print(f"   python3 {src}/game.py romy --reset")
    print(f"   python3 {src}/game.py oscar --reset")
    print()
    print(f"   {DIM}# Désinstaller le jeu :{RESET}")
    print(f"   sudo bash {src}/setup/uninstall.sh")
    print()


if __name__ == "__main__":
    # Désactiver les couleurs si la sortie n'est pas un terminal
    if not sys.stdout.isatty():
        for name in ("RESET", "BOLD", "DIM", "RED", "GREEN", "YELLOW",
                     "BLUE", "MAGENTA", "CYAN", "WHITE",
                     "ROMY_COLOR", "OSCAR_COLOR"):
            globals()[name] = ""

    main()
