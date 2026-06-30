"""
Cross-platform terminal keypress reader.

This module provides utilities for reading single keypresses from the terminal on both Windows and Unix-like systems.
It abstracts away the platform-specific details of raw terminal input and normalizes keypresses into consistent, human-readable strings.

Supported features include:

- Reading a single keypress without waiting for Enter.
- Cross-platform handling of special keys such as arrows.
- Normalization of control characters and ANSI escape sequences.
- A context manager for enabling raw terminal mode on Unix-like systems.

Typical usage:

    with raw_mode():
        while some_condition:
            key = read_keypress()

Functions:
- `raw_mode()`: Context manager to enable raw terminal mode.
- `read_keypress()`: Reads a single keypress and returns its normalized string representation.
- `normalize()`: Normalizes raw keypress sequences into human-readable strings.
"""

from __future__ import annotations

import sys
import contextlib

__all__ = ["raw_mode", "read_keypress", "normalize"]

# Key mapping for special keys and control characters
KEY_MAP = {
    "\r": "enter",
    "\n": "enter",
    "\t": "tab",
    " ": "space",
    "\x1b": "escape",
    "\x7f": "backspace",
    "\b": "backspace",
    "\x03": "ctrl+c",
    "\x04": "ctrl+d",
}

# Mapping for ANSI escape sequences corresponding to cursor movement keys
# Arrow keys don't send a single byte (unlike letters, numbers, or enter), instead they send escape sequences like "\x1b[A" for up, "\x1b[B" for down, etc.
# So we need to detect and parse these sequences to return a normalized string representation of the keypress.
# The letter after "\x1b[" indicates the direction: A=up, B=down, C=right, D=left. H=home, F=end.
CSI_KEY_MAP = {
    "A": "up",
    "B": "down",
    "C": "right",
    "D": "left",
    "H": "home",
    "F": "end",
}

# Mapping for special keys on Windows
WIN_SPECIAL_KEY_MAP = {
    b"H": "up",
    b"P": "down",
    b"K": "left",
    b"M": "right",
}

# -----------------
# TERMINAL RAW MODE
# -----------------

@contextlib.contextmanager
def raw_mode():
    """Enable raw mode for the terminal, allowing for unbuffered input."""
    if sys.platform == "win32":
        yield # On Windows, raw mode is not needed for keypress reading (msvcrt is always raw)
    else:
        import tty, termios
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd) # save the current terminal settings
        try:
            tty.setraw(fd)          # set the terminal to raw mode (unbuffered input)
            yield
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)   # restore the original terminal settings after exiting raw mode


# --------------
# READ KEY PRESS
# --------------

def read_keypress(inject: str | None = None) -> str:
    """Read a single keypress from the terminal and return its normalized string representation."""

    # If an injected keypress is provided (for testing), normalize and return it
    if inject is not None:
        return normalize(inject)

    # Read the raw keypress from the terminal in raw mode and normalize it to a human-readable string
    raw = _read_raw_keypress()
    return normalize(raw)


def _read_raw_keypress() -> str:
    """Read a single keypress from the terminal in raw mode and return the raw string."""
    
    if sys.platform == "win32":
        import msvcrt
        
        b = msvcrt.getch()  # Read the first character from the console. This can be a regular character or a special key indicator.
        
        # Handle special keys (like arrow keys) which are sent as two-character sequences on Windows
        if b == b"\x00" or b == b"\xe0":                        # Special keys (arrows, function keys, etc.)
            b2 = msvcrt.getch()                                 # Read the second character
            return WIN_SPECIAL_KEY_MAP.get(b2, b2.decode())
        
        # Handle regular keys (letters, numbers, enter, etc.)
        return b.decode('utf-8', errors='replace')

    else:
        b = sys.stdin.read(1)                   # Read a single character

        # Handle ANSI escape sequences for special keys (like arrow keys) which start with the escape character "\x1b"
        if b == "\x1b":
            seq = b + sys.stdin.read(1)         # Read the next character

            # If the next character is "[", it indicates the start of a Control Sequence Introducer (CSI) sequence, which is used for arrow keys and other special keys. Read the next character to complete the sequence.
            if seq == "\x1b[":
                seq += sys.stdin.read(1)  # Read the next character for CSI sequences
            # If the next character is not "[", it could be a bare escape sequence (like pressing the escape key alone). In that case, we just return the escape character as is.
            elif seq[1] not in ("[", "0"):
                pass

            return seq

        # Handle regular keys (letters, numbers, enter, etc.)
        return b


# ---------
# NORMALIZE
# ---------

def normalize(seq: str) -> str:
    """Normalize the raw keypress sequence to a human-readable string."""

    # Check if the sequence is in the predefined KEY_MAP
    if seq in KEY_MAP:
        return KEY_MAP[seq]

    # Handle ANSI escape sequences for arrow keys and other special keys
    if len(seq) == 3 and seq.startswith("\x1b[") and seq[2] in CSI_KEY_MAP:
        return CSI_KEY_MAP[seq[2]]
    
    # Preserve single characters like letters, numbers, and symbols as is
    if len(seq) == 1 and seq.isprintable() or seq == "":
        return seq
    
    # For unrecognized sequences, return the raw sequence
    return seq
