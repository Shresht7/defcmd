"""
Build `argparse` parsers from extracted command parameters.

This module converts `Parameter` objects produced by `introspect` into an `argparse.ArgumentParser`.
It maps Python parameter metadata onto argparse constructs such as positional arguments, optional flags,
boolean switches, choices, defaults, and type conversion.

Value conversion and validation are delegated to `convert.parse_value`,
allowing command-line arguments to be parsed according to the original function signature and any attached `Spec` constraints.
"""

from __future__ import annotations

import argparse
import os

from .introspect import Parameter
from .convert import ValidationError, parse_value

from typing import get_origin, get_args, Literal
from collections.abc import Callable

def build_parser(params: list[Parameter], description: str | None = None, parser: argparse.ArgumentParser | None = None, epilog: str | None = None) -> argparse.ArgumentParser:
    """Build an `argparse.ArgumentParser` based on the list of `Parameter` objects extracted from a function signature"""
    
    # If no parser is provided, create a new one with the given description
    if parser is None:
        parser = argparse.ArgumentParser(description=description, epilog=epilog)

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

        # Determine the default value
        default = param.default if not param.required else None
        # If the parameter has a Spec with an env attribute, attempt to resolve the value from the environment variables
        if param.spec and param.spec.env:
            raw = resolve_env(param.spec.env)
            if raw is not None:
                default = parse_value(param, raw)

        # Handle boolean parameters with a special action that creates both --flag and --no-flag options and sets the default value appropriately
        if param.annotation is bool:
            parser.add_argument(*names, action=argparse.BooleanOptionalAction, default=default, **kwargs)
            continue # Skip the rest of the loop since we've already handled this parameter

        # For other types, use the type converter function to handle conversion and validation
        kwargs["type"] = _make_type_converter(param)

        # Choices for Literal types
        origin = get_origin(param.annotation)
        if origin is Literal:
            kwargs["choices"] = list(get_args(param.annotation))

        # If the parameter is required and has no default (from env or function), add it as a positional argument...
        if param.required and default is None:
            parser.add_argument(param.name, **kwargs)
        # ...otherwise, add it as an optional argument with the appropriate flags and default value
        else:
            parser.add_argument(*names, default=default, **kwargs)

    return parser

# ----------------
# HELPER FUNCTIONS
# ----------------

def _make_type_converter(param: Parameter) -> Callable[[str], object]:
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


def resolve_env(env: str | tuple[str, ...]) -> str | None:
    """
    Resolve the value of an environment variable or a tuple of environment variables.
    If a tuple is provided, the first one that is set will be returned.
    If none are set, None will be returned.
    """
    if isinstance(env, str):
        return os.environ.get(env)
    
    for var in env:
        value = os.environ.get(var)
        if value is not None:
            return value
    
    return None
