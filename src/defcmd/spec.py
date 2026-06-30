"""
Defines the Spec class, which represents the specification of a command, including its help text and other specifications.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

@dataclass(frozen=True)
class Spec:
    """Represents additional specifications for a command parameter, such as its short name, help text, prompt, and validation constraints."""

    # Attributes
    short: str | None = None            # A short name for this parameter (e.g., a single-letter flag)
    help: str | None = None             # The help message to show for this parameter
    prompt: str | None = None           # The prompt message to show when asking for this parameter
    secret: bool = False                # Whether this parameter is a secret (e.g., a password) and should be hidden when prompting

    # Validation constraints
    min: int | float | None = None      # The minimum value for this parameter (if applicable)
    max: int | float | None = None      # The maximum value for this parameter (if applicable)
    pattern: str | None = None          # A regex pattern that the parameter value must match (if applicable)
    validate: Callable | None = None    # A custom validation function for this parameter (if applicable)
