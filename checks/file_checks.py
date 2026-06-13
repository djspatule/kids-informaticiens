"""
checks/file_checks.py — Filesystem-based mission checks.

All path arguments support ~ expansion.
"""

import logging
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)


def _resolve(path: str) -> Path:
    """Expand ~ and return a resolved Path."""
    return Path(path).expanduser()


# ---------------------------------------------------------------------------
# Individual check functions
# ---------------------------------------------------------------------------

def check_file_exists(path: str) -> bool:
    """Return True if the file exists (not a directory)."""
    try:
        result = _resolve(path).is_file()
        logger.debug("check_file_exists(%s) -> %s", path, result)
        return result
    except OSError as exc:
        logger.warning("check_file_exists error for %s: %s", path, exc)
        return False


def check_file_not_exists(path: str) -> bool:
    """Return True if the file does NOT exist."""
    try:
        result = not _resolve(path).exists()
        logger.debug("check_file_not_exists(%s) -> %s", path, result)
        return result
    except OSError as exc:
        logger.warning("check_file_not_exists error for %s: %s", path, exc)
        return False


def check_file_accessed(path: str, since_iso: str) -> bool:
    """
    Return True if the file was accessed (atime) more recently than since_iso.

    since_iso must be a valid ISO-8601 datetime string (with or without TZ).
    """
    try:
        p = _resolve(path)
        if not p.exists():
            return False
        atime = p.stat().st_atime
        # Parse the reference time; assume UTC if no timezone present
        ref_dt = datetime.fromisoformat(since_iso)
        if ref_dt.tzinfo is None:
            ref_dt = ref_dt.replace(tzinfo=timezone.utc)
        ref_ts = ref_dt.timestamp()
        result = atime > ref_ts
        logger.debug(
            "check_file_accessed(%s, since=%s) atime=%.0f ref=%.0f -> %s",
            path, since_iso, atime, ref_ts, result,
        )
        return result
    except (OSError, ValueError) as exc:
        logger.warning("check_file_accessed error for %s: %s", path, exc)
        return False


def check_file_contains(path: str, text: str, case_sensitive: bool = False) -> bool:
    """Return True if the file exists and contains the given text."""
    try:
        p = _resolve(path)
        if not p.is_file():
            return False
        content = p.read_text(encoding="utf-8", errors="replace")
        if not case_sensitive:
            result = text.lower() in content.lower()
        else:
            result = text in content
        logger.debug("check_file_contains(%s, %r) -> %s", path, text, result)
        return result
    except OSError as exc:
        logger.warning("check_file_contains error for %s: %s", path, exc)
        return False


def check_folder_exists(path: str) -> bool:
    """Return True if the directory exists."""
    try:
        result = _resolve(path).is_dir()
        logger.debug("check_folder_exists(%s) -> %s", path, result)
        return result
    except OSError as exc:
        logger.warning("check_folder_exists error for %s: %s", path, exc)
        return False


def check_file_moved(src: str, dst: str) -> bool:
    """
    Return True if a file has been moved from src to dst.

    Condition: src must NOT exist AND dst must exist.
    """
    try:
        src_gone = not _resolve(src).exists()
        dst_here = _resolve(dst).is_file()
        result = src_gone and dst_here
        logger.debug("check_file_moved(%s -> %s) -> %s", src, dst, result)
        return result
    except OSError as exc:
        logger.warning("check_file_moved error (%s -> %s): %s", src, dst, exc)
        return False


def check_file_renamed(dir: str, old_name: str, new_name: str) -> bool:
    """
    Return True if a file has been renamed within a directory.

    Condition: old_name must NOT exist in dir, and new_name must exist in dir.
    """
    try:
        d = _resolve(dir)
        old_gone = not (d / old_name).exists()
        new_here = (d / new_name).is_file()
        result = old_gone and new_here
        logger.debug(
            "check_file_renamed(%s: %s -> %s) -> %s",
            dir, old_name, new_name, result,
        )
        return result
    except OSError as exc:
        logger.warning(
            "check_file_renamed error (%s / %s -> %s): %s",
            dir, old_name, new_name, exc,
        )
        return False
