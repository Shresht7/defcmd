"""
Defines the Spec class, which represents the specification of a command, including its help text and other specifications.

This module defines the `Spec` dataclass, which stores metadata describing how a command parameter should be presented and validated.

A specification can provide:
- help text for generated documentation
- a short option name (for example, `-f`)
- prompt configuration for interactive input
- secret input handling
- environment variable sourcing for default values
- validation constraints such as minimum and maximum values,
  regular expression patterns, and custom validation functions

`Spec` instances are attached to command parameters and are consumed by the command parser, help generator, and interactive prompting system.

Path validation via `path_exists` and `path_type` is supported when the parameter is annotated as `pathlib.Path`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Literal

@dataclass(frozen=True)
class Spec:
    """Represents additional specifications for a command parameter, such as its short name, help text, prompt, and validation constraints."""

    # Attributes
    short: str | None = None                            # A short name for this parameter (e.g., a single-letter flag)
    help: str | None = None                             # The help message to show for this parameter
    prompt: str | bool | None = None                    # The prompt message to show when asking for this parameter; False to skip prompting, True to force prompt
    secret: bool = False                                # Whether this parameter is a secret (e.g., a password) and should be hidden when prompting
    env: str | tuple[str, ...] | None = None            # The environment variable(s) to source this parameter from, if applicable

    # Validation constraints
    min: int | float | None = None                      # The minimum value for this parameter (if applicable)
    max: int | float | None = None                      # The maximum value for this parameter (if applicable)
    pattern: str | None = None                          # A regex pattern that the parameter value must match (if applicable)
    validate: Callable | None = None                    # A custom validation function for this parameter (if applicable)

    # Path validation
    path_exists: bool | None = None                     # If set, raises an error if the path does not exist
    path_type: Literal["file", "dir"] | None = None     # If set, raises an error if the path is not a file or directory
    path_resolve: bool = True                           # If True, expand user and resolve to absolute path
