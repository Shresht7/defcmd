from typing import Protocol

from getpass import getpass
from defcmd.terminal.keypress import read_keypress

class InputReader(Protocol):
    def read(self, prompt: str) -> str: ...
    def read_secret(self, prompt: str, mask_char: str = "*") -> str: ...
    def read_keypress(self) -> str: ...

class DefaultInputReader:
    """Default implementation of InputReader that uses standard input and getpass"""

    def read(self, prompt: str) -> str:
        """Read input from the terminal"""
        return input(prompt)

    def read_secret(self, prompt: str, mask_char: str = "*") -> str:
        """Read a secret input from the terminal, optionally masking the input"""
        return getpass(prompt, echo_char=mask_char)    

    def read_keypress(self) -> str:
        """Read a single keypress from the terminal"""
        return read_keypress()
