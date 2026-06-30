"""
Utilities for interacting with the terminal.

The `defcmd.terminal` package provides cross-platform abstractions for terminal input and output, including:

- ANSI escape codes for styling terminal text.
- Cursor movement and screen manipulation.
- Reading standard input and secret input.
- Reading individual keypresses.
"""

from .ansi import *
from .keypress import read_keypress, raw_mode
from .reader import InputReader, DefaultInputReader, ScriptedInputReader
