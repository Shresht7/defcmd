"""
defcmd provides a simple and intuitive way to turn any function signature into a command-line script.
"""

from importlib.metadata import version

from .runner import cmd, CLI
from .spec import Spec

__version__ = version("defcmd")

__all__ = ["cmd", "CLI", "Spec"]
