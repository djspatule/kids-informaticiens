"""
checks/desktop_checks.py — Desktop environment checks (XFCE).
"""

import logging
import subprocess

logger = logging.getLogger(__name__)


def get_xfce_wallpaper() -> str | None:
    """
    Return the current XFCE desktop wallpaper path by querying xfconf.

    Runs: xfconf-query -c xfce4-desktop -lv
    Looks for lines that contain 'last-image' and returns the path value
    (the last whitespace-separated token on the matching line).

    Returns None on any error or if xfconf-query is unavailable.
    """
    try:
        result = subprocess.run(
            ["xfconf-query", "-c", "xfce4-desktop", "-lv"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            logger.debug(
                "xfconf-query returned non-zero exit code %d: %s",
                result.returncode, result.stderr.strip(),
            )
            return None

        for line in result.stdout.splitlines():
            if "last-image" in line:
                parts = line.split()
                if parts:
                    wallpaper = parts[-1]
                    logger.debug("Current wallpaper detected: %s", wallpaper)
                    return wallpaper

        logger.debug("No 'last-image' entry found in xfconf output.")
        return None

    except FileNotFoundError:
        logger.warning("xfconf-query not found — cannot detect wallpaper.")
        return None
    except subprocess.TimeoutExpired:
        logger.warning("xfconf-query timed out.")
        return None
    except OSError as exc:
        logger.warning("xfconf-query error: %s", exc)
        return None


def check_wallpaper_changed(initial_wallpaper: str) -> bool:
    """
    Return True if the current wallpaper differs from initial_wallpaper.

    Both the current wallpaper must be non-empty AND different from the
    initial value to be considered a genuine change.
    """
    current = get_xfce_wallpaper()
    if not current:
        logger.debug("check_wallpaper_changed: could not determine current wallpaper.")
        return False
    changed = current != initial_wallpaper
    logger.debug(
        "check_wallpaper_changed: initial=%r current=%r -> %s",
        initial_wallpaper, current, changed,
    )
    return changed
