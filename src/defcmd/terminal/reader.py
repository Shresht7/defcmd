from typing import Protocol

from getpass import getpass
from defcmd.terminal.keypress import read_keypress

# INPUT READER
# ------------

class InputReader(Protocol):
    def read(self, prompt: str) -> str: ...
    def read_secret(self, prompt: str, mask_char: str = "*") -> str: ...
    def read_keypress(self) -> str: ...

# DEFAULT INPUT READER
# --------------------

class DefaultInputReader:
    """Default implementation of InputReader that uses standard input and getpass functions for reading input from the terminal"""

    def read(self, prompt: str) -> str:
        """Read input from the terminal"""
        return input(prompt)

    def read_secret(self, prompt: str, mask_char: str = "*") -> str:
        """Read a secret input from the terminal, optionally masking the input"""
        return getpass(prompt, echo_char=mask_char)    

    def read_keypress(self) -> str:
        """Read a single keypress from the terminal"""
        return read_keypress()

# SCRIPTED INPUT READER
# ---------------------

class ScriptedInputReader:
    """
    An InputReader implementation that returns scripted values for testing purposes.
    It allows you to specify a sequence of values, secrets, and keypresses that will be returned when the corresponding read methods are called.
    This is useful for testing code that relies on user input without requiring actual user interaction
    """

    def __init__(self, *, values=(), secrets=(), keypresses=()):
        self._values = iter(values)
        self._secrets = iter(secrets)
        self._keypresses = iter(keypresses)
        self.prompts: list[str] = []
        self.secret_prompts: list[tuple[str, str]] = []

    def read(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return next(self._values)

    def read_secret(self, prompt: str, mask_char: str = "*") -> str:
        self.secret_prompts.append((prompt, mask_char))
        return next(self._secrets)

    def read_keypress(self) -> str:
        return next(self._keypresses)

