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

from .introspect import Parameter, get_inner_type, create_synthetic_parameter
from .convert import ValidationError, parse_value
from .terminal import dim, cyan

from typing import Any, get_origin, get_args, Literal
from collections.abc import Callable


def build_parser(
        params: list[Parameter],
        description: str | None = None,
        parser: argparse.ArgumentParser | None = None,
        examples: dict[str, str] | None = None,
        epilog: str | None = None,
        add_examples_flag: bool = True,
    ) -> argparse.ArgumentParser:
    """Build an `argparse.ArgumentParser` based on the list of `Parameter` objects extracted from a function signature"""

    # If no parser is provided, create a new one with the given description
    if parser is None:
        # Initialize the parser kwargs dictionary that will be passed to the ArgumentParser constructor
        argparse_kwargs = {}

        # Build the epilog for the argparse help text, including examples if provided
        if examples:
            argparse_kwargs["epilog"] = build_argparse_epilog(epilog, examples)
            argparse_kwargs["formatter_class"] = argparse.RawDescriptionHelpFormatter

        # Create the ArgumentParser with the provided description and any additional kwargs
        parser = argparse.ArgumentParser(description=description, **argparse_kwargs)


    # If examples are provided, expose a `--examples` flag that prints the examples block and exits
    if examples and add_examples_flag:
        parser.add_argument(
            "--examples",
            action=_ExamplesAction,
            examples=examples,
            help="Show usage examples and exit"
        )

    # Add arguments to the parser for each parameter in the list
    for param in params:
        names = _build_param_names(param)
        origin = get_origin(param.annotation)
        default = _resolve_default(param, origin)

        # Handle boolean parameters separately, using the `BooleanOptionalAction` to create both `--flag` and `--no-flag` options
        if param.annotation is bool:
            bool_kwargs = {}
            if param.spec and param.spec.help:
                bool_kwargs["help"] = param.spec.help
            parser.add_argument(*names, action=argparse.BooleanOptionalAction, default=default, **bool_kwargs)
            continue

        # For non-boolean parameters, build the argument keyword arguments based on the parameter's metadata and add it to the parser
        kwargs = _build_param_kwargs(param, origin, default)

        # If the parameter is required and has no default value, add it as a positional argument
        if param.required and default is None:
            parser.add_argument(param.name, **kwargs)
        # Otherwise, add it as an optional argument with the specified names and default value
        else:
            parser.add_argument(*names, default=default, **kwargs)

    return parser


# ----------------
# HELPER FUNCTIONS
# ----------------


def _build_param_names(param: Parameter) -> list[str]:
    """Build the list of argument names for a given parameter, including short and long flags if specified in the Spec"""
    names = []
    if param.spec and param.spec.short:
        names.append(f"-{param.spec.short}")
    names.append(f"--{param.name}")
    return names


def _build_param_kwargs(param: Parameter, origin: type | None, default: Any) -> dict[str, Any]:
    """Build the keyword arguments for `argparse.ArgumentParser.add_argument` based on the parameter's metadata"""

    # Initialize the kwargs dictionary that will be passed to `add_argument`
    kwargs = {} 

    # If the parameter has a Spec with a help attribute, include it in the kwargs
    if param.spec and param.spec.help:
        kwargs["help"] = param.spec.help

    # If the parameter is a list, create a synthetic parameter for the inner type and set the type converter and nargs accordingly
    if origin is list:
        inner_type = get_inner_type(param)
        synthetic = create_synthetic_parameter(param, inner_type)
        kwargs["type"] = _make_type_converter(synthetic)
        kwargs["nargs"] = "+" if param.required and default is None else "*"

    # If the parameter has a Spec with a stdin attribute, set nargs to "*" for lists or "?" for single values
    if param.spec and param.spec.stdin:
        kwargs["nargs"] = "*" if origin is list else "?"

    # If "type" is not already set in the kwargs, create a type converter for the parameter and include it
    if "type" not in kwargs:
        kwargs["type"] = _make_type_converter(param)

    # If the parameter has a Spec with a choices attribute, include it in the kwargs
    if origin is Literal:
        kwargs["choices"] = list(get_args(param.annotation))

    return kwargs


def _resolve_default(param: Parameter, origin: type | None) -> Any:
    """Resolve the default value for a parameter, checking for environment variable overrides if specified in the Spec"""

    # Start with the default value from the parameter, or None if the parameter is required
    default = param.default if not param.required else None

    # If the parameter has a Spec with an env attribute, attempt to resolve the value from the environment variables
    if param.spec and param.spec.env:
        
        # If the parameter is a list, create a synthetic parameter for the inner type and parse the environment variable value into a list of values
        if origin is list:
            inner_type = get_inner_type(param)
            synthetic = create_synthetic_parameter(param, inner_type)
            raw = _resolve_env(param.spec.env)
            if raw is not None:
                default = [parse_value(synthetic, part) for part in raw.split()]

        # Otherwise, parse the environment variable value into the expected type for the parameter
        else:
            raw = _resolve_env(param.spec.env)
            if raw is not None:
                default = parse_value(param, raw)

    return default


def _resolve_env(env: str | tuple[str, ...]) -> str | None:
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


def generate_examples_block(examples: dict[str, str] | None, show_header: bool = True) -> str | None:
    """Generate a formatted examples block for the command's help text"""
    if not examples:
        return None
    lines = ["", cyan("examples:")] if show_header else []
    cmds = list(examples.items())
    width = max(len(example) for _, example in cmds)
    for description, example in examples.items():
        description = dim(f"# {description}")
        lines.append(f"  {example.ljust(width)}        {description}")
    return "\n".join(lines)


def build_argparse_epilog(epilog: str | None, examples: dict[str, str] | None) -> str | None:
    """Build the epilog for the argparse help text, including examples if provided"""
    examples_block = generate_examples_block(examples, show_header=True)
    if epilog and examples_block:
        return f"{examples_block}\n\n{epilog}"
    if examples_block:
        return examples_block
    return epilog


class _ExamplesAction(argparse.Action):
    """Custom argparse action to print the examples and exit"""
    def __init__(self, option_strings, dest, **kwargs):
        self.examples = kwargs.pop("examples", None)
        super().__init__(option_strings, dest, nargs=0, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        width = max(len(e) for e in self.examples.values())
        for desc, cmd in self.examples.items():
            print(f"{cmd:<{width}}\t# {desc}")
        parser.exit()

