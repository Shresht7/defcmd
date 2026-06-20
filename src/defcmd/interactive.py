"""
This module provides a utility function to determine if the current execution context is interactive.
It checks if both standard input and output are connected to a terminal and if no command-line arguments are provided.
This is useful for deciding whether to prompt the user for input or to run in a non-interactive mode.
"""

from __future__ import annotations

import sys
from typing import Callable

def is_interactive(argv: list[str], isatty: Callable[[], bool] = lambda: sys.stdin.isatty()) -> bool:
    """Check if we are running in interactive mode where prompting makes sense"""
    return len(argv) == 0 and isatty()
