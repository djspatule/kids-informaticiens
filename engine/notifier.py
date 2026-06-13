"""
engine/notifier.py — Notifications, sound playback, and event logging.
"""

import logging
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

# Sound file mapping (freedesktop standard paths)
_SOUND_MAP = {
    "success": "/usr/share/sounds/freedesktop/stereo/complete.oga",
    "unlock":  "/usr/share/sounds/freedesktop/stereo/bell.oga",
    "start":   "/usr/share/sounds/freedesktop/stereo/dialog-information.oga",
}

# Project source root (this file is in engine/, so go up one level)
_SOURCE_ROOT = Path(__file__).parent.parent.resolve()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def send_notification(
    title: str,
    body: str,
    timeout_ms: int = 8000,
    urgency: str = "normal",
) -> None:
    """
    Send a desktop notification via notify-send.

    Fails silently if notify-send is not installed or the notification daemon
    is unavailable (common in plain XFCE sessions during early boot).
    """
    try:
        subprocess.Popen(
            [
                "notify-send",
                "--urgency", urgency,
                "--expire-time", str(timeout_ms),
                "--app-name", "Mission Espace",
                title,
                body,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        logger.debug("Notification sent: %s / %s", title, body)
    except FileNotFoundError:
        logger.debug("notify-send not found — skipping notification.")
    except OSError as exc:
        logger.debug("Could not send notification: %s", exc)


def play_sound(sound_type: str) -> None:
    """
    Play a system sound using paplay.

    sound_type must be one of: "success", "unlock", "start".
    Falls back silently if paplay is unavailable or the file does not exist.
    """
    path = _SOUND_MAP.get(sound_type)
    if not path:
        logger.warning("Unknown sound type: %r", sound_type)
        return

    if not Path(path).exists():
        logger.debug("Sound file not found: %s — skipping.", path)
        return

    try:
        subprocess.Popen(
            ["paplay", path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        logger.debug("Sound played: %s (%s)", sound_type, path)
    except FileNotFoundError:
        logger.debug("paplay not found — skipping sound.")
    except OSError as exc:
        logger.debug("Could not play sound: %s", exc)


def log_event(player: str, event: str, detail: str = "") -> None:
    """
    Append a timestamped event line to logs/{player}.log.

    Format: 2024-06-01T12:34:56Z  EVENT  detail
    Never raises — errors are swallowed so the game keeps running.
    """
    log_path = _SOURCE_ROOT / "logs" / f"{player}.log"
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        line = f"{now}  {event:<24s}  {detail}\n"
        with open(log_path, "a", encoding="utf-8") as fh:
            fh.write(line)
    except OSError as exc:
        logger.debug("log_event write failed: %s", exc)
