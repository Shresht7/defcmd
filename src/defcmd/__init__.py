"""
defcmd provides a simple and intuitive way to turn any function signature into a command-line script.
"""

from defcmd.runner import cmd, CLI
from defcmd.spec import Spec

__version__ = "0.1.0"
__all__ = ["cmd", "CLI", "Spec"]
