"""
checks/composite_checks.py — Logical combinator checks (all_of / any_of).

These delegate back to the main CheckRunner so that any check type can be
nested inside a composite.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass  # avoid circular import; CheckRunner is passed in at call time

logger = logging.getLogger(__name__)


def check_all_of(checks: list, runner) -> bool:
    """
    Return True only when ALL sub-checks pass.

    Short-circuits on the first failure.
    """
    for spec in checks:
        if not runner.run(spec):
            logger.debug("check_all_of: sub-check failed: %s", spec)
            return False
    logger.debug("check_all_of: all %d sub-checks passed", len(checks))
    return True


def check_any_of(checks: list, runner) -> bool:
    """
    Return True when AT LEAST ONE sub-check passes.

    Short-circuits on the first success.
    """
    for spec in checks:
        if runner.run(spec):
            logger.debug("check_any_of: sub-check passed: %s", spec)
            return True
    logger.debug("check_any_of: none of %d sub-checks passed", len(checks))
    return False
