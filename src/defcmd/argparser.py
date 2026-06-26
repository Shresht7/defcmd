"""
This module contains the logic for building an `argparse.ArgumentParser` based on the list of `Parameter` objects extracted from a function signature.
It defines a single function, `build_parser`, which takes a list of `Parameter` objects
and returns an `ArgumentParser` that can be used to parse command-line arguments corresponding to those parameters.
"""

from __future__ import annotations

import argparse
from .introspect import Parameter

from typing import get_origin, get_args, Literal

def build_parser(params: list[Parameter], description: str | None = None) -> argparse.ArgumentParser:
    """Build an `argparse.ArgumentParser` based on the list of `Parameter` objects extracted from a function signature"""
    parser = argparse.ArgumentParser(description=description)

    for param in params:

        names = []
        if param.spec and param.spec.short:
            names.append(f"-{param.spec.short}")
        names.append(f"--{param.name}")

        # Setup the common kwargs for both required and optional parameters
        kwargs = {}

        # If the parameter has a Spec with a help message, include that in the argument definition so it shows up in the --help output
        if param.spec and param.spec.help:
            kwargs["help"] = param.spec.help

        # Handle boolean parameters with a special action that creates both --flag and --no-flag options and sets the default value appropriately
        if param.annotation is bool:
            default = param.default if not param.required else False
            parser.add_argument(*names, action=argparse.BooleanOptionalAction, default=default, **kwargs)
            continue # Skip the rest of the loop since we've already handled this parameter

        # If the annotation is a Literal, we can use the choices argument to restrict the allowed values
        if get_origin(param.annotation) is Literal:
            kwargs["choices"] = list(get_args(param.annotation))
        # If it's a regular type, we can use the type argument to automatically convert the input string to the correct type
        elif isinstance(param.annotation, type):
            kwargs["type"] = param.annotation

        # For required parameters, add a positional argument. For optional parameters, add a flag with the default value.
        if param.required:
            parser.add_argument(param.name, **kwargs)
        else:
            parser.add_argument(*names, default=param.default, **kwargs)

    return parser
