"""
This module contains the logic for building an `argparse.ArgumentParser` based on the list of `Parameter` objects extracted from a function signature.
It defines a single function, `build_parser`, which takes a list of `Parameter` objects
and returns an `ArgumentParser` that can be used to parse command-line arguments corresponding to those parameters.
"""

from __future__ import annotations

import argparse
from .introspect import Parameter

from defcmd.convert import ValidationError, parse_value

from typing import get_origin, get_args, Literal

def build_parser(params: list[Parameter], description: str | None = None, parser: argparse.ArgumentParser | None = None) -> argparse.ArgumentParser:
    """Build an `argparse.ArgumentParser` based on the list of `Parameter` objects extracted from a function signature"""
    
    # If no parser is provided, create a new one with the given description
    if parser is None:
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

        # For other types, use the type converter function to handle conversion and validation
        kwargs["type"] = _make_type_converter(param)

        # Choices for Literal types
        origin = get_origin(param.annotation)
        if origin is Literal:
            kwargs["choices"] = list(get_args(param.annotation))

        # For required parameters, add a positional argument. For optional parameters, add a flag with the default value.
        if param.required:
            parser.add_argument(param.name, **kwargs)
        else:
            parser.add_argument(*names, default=param.default, **kwargs)

    return parser

# ----------------
# HELPER FUNCTIONS
# ----------------

def _make_type_converter(param: Parameter):
    """
    Create a type converter function for a given parameter that will be used by argparse to convert
    the raw string input into the expected type and validate it against any Spec constraints
    """
    def type_fn(raw: str):
        try:
            return parse_value(param, raw)
        except ValidationError as e:
            raise argparse.ArgumentTypeError(str(e)) from e
    return type_fn
