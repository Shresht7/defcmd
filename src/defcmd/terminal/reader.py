"""
This module provides an abstraction for reading input from the terminal, including standard input, secret input (like passwords), and keypresses.

It defines a protocol for input readers and provides two implementations:
- a `DefaultInputReader` that uses standard `input` and `getpass` functions for reading input from the terminal
- a `ScriptedInputReader` that allows for predefined input values, useful for testing purposes.
"""

from typing import Protocol

from getpass import getpass

from .keypress import read_keypress

from collections.abc import Iterable

__all__ = [
    "InputReader",
    "DefaultInputReader",
    "ScriptedInputReader",
]

# INPUT READER
# ------------

class InputReader(Protocol):
    """Protocol describing objects capable of reading terminal input"""
    def read(self, prompt: str) -> str: ...
    def read_secret(self, prompt: str, mask_char: str = "*") -> str: ...
    def read_keypress(self) -> str: ...


# DEFAULT INPUT READER
# --------------------

class DefaultInputReader:
    """Default implementation of InputReader that uses standard `input` and `getpass` functions for reading input from the terminal"""

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
    InputReader implementation backed by predefined values.

    Useful for unit tests where interactive terminal input is undesirable.
    Each call to a read method consumes the next value from its corresponding sequence.
    """

    def __init__(
            self,
            *, 
            values: Iterable[str] = (), 
            secrets: Iterable[str] = (), 
            keypresses: Iterable[str] = ()
        ):
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

