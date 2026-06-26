"""
Defines the Spec class, which represents the specification of a command, including its help text and other specifications.
"""

from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class Spec:
    help: str | None = None     # The help message to show for this parameter
    prompt: str | None = None   # The prompt message to show when asking for this parameter
    secret: bool = False        # Whether this parameter is a secret (e.g., a password) and should be hidden when prompting
