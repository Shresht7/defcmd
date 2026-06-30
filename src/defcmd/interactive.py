"""
Utility for detecting interactive terminal sessions.

This module provides helpers for determining whether a command is running in
an interactive context where prompting the user for input is appropriate.

A session is considered interactive when no command-line arguments have been
provided and standard input is connected to a terminal. The terminal check is
injectable to simplify testing.
"""

from __future__ import annotations

import sys
from collections.abc import Callable

def _stdin_isatty() -> bool:
    return sys.stdin.isatty()

def is_interactive(argv: list[str], isatty: Callable[[], bool] = _stdin_isatty) -> bool:
    """Check if we are running in interactive mode where prompting makes sense"""
    return len(argv) == 0 and isatty()
