"""
Describes how a command parameter should be presented, validated, and sourced.

This module defines the `Spec` dataclass, which stores metadata for a single function
parameter in the command-line interface.

A specification can provide:
- help text shown in `--help` output
- a short option name (for example, `-f`)
- prompt configuration for interactive input (custom message, skip, or force)
- secret input handling (hidden input)
- environment variable sourcing for default values
- validation constraints: minimum/maximum values, regex patterns, custom validators
- path validation: existence checks, file/directory type, and resolution
- stdin support for piped input

`Spec` instances are attached to parameters via `typing.Annotated` and consumed by the
argparse builder, help generator, interactive wizard, and stdin injection logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Literal

@dataclass(frozen=True)
class Spec:
    """Represents additional specifications for a command parameter, such as its short name, help text, prompt, and validation constraints."""

    # Attributes
    short: str | None = None                            # A short name for this parameter (e.g., a single-letter flag)
    help: str | None = None                             # The help message to show for this parameter
    prompt: str | bool | None = None                    # The prompt message to show when asking for this parameter; False to skip prompting, True to force prompt
    secret: bool = False                                # Whether this parameter is a secret (e.g., a password) and should be hidden when prompting
    env: str | tuple[str, ...] | None = None            # The environment variable(s) to source this parameter from, if applicable

    # Validation
    min: int | float | None = None                      # Minimum value (numeric parameters)
    max: int | float | None = None                      # Maximum value (numeric parameters)
    pattern: str | None = None                          # Regex pattern the value must match
    validate: Callable[[Any], Any] | None = None        # Custom validator function to validate the value; raises ValidationError if invalid
    # Path
    path_exists: bool | None = None                     # Raise an error if the path does not exist
    path_type: Literal["file", "dir"] | None = None     # Require the path to be a file or directory
    path_resolve: bool = True                           # Expand ~ and resolve to an absolute path

    # Standard Input
    stdin: bool = False                                 # Whether the parameter can receive its value from stdin
    delimiter: str = "\n"                               # Delimiter to split stdin content (for `list[T]` params with `stdin=True`)
