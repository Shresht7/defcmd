"""
Extract command-line interface parameters from a function signature

This module converts Python function signatures into a structured representation
that can be consumed by the command parser, interactive prompting system, and help generator.

Each function parameter is represented as a `Parameter` object containing
its name, type annotation, default value, parameter kind,
and any additional metadata provided through `typing.Annotated` and `Spec`.

Function signatures that cannot be represented as command-line interfaces,
such as those containing `*args` or `**kwargs`, raise `UnsupportedSignatureError`.
"""


from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Annotated, Any, get_args, get_origin, get_type_hints
from collections.abc import Callable

from .spec import Spec


class UnsupportedSignatureError(TypeError):
    """Raised when a function signature cannot be represented as a command-line interface"""
    pass


@dataclass(frozen=True)
class Parameter:
    """Represents a parameter extracted from a function signature"""
    name: str                       # name of the parameter
    annotation: Any                 # type annotation of the parameter
    required: bool                  # whether the parameter is required (no default value)
    default: Any                    # default value of the parameter (if any)
    kind: inspect._ParameterKind    # kind of the parameter (positional, keyword, var-positional, var-keyword)
    spec: Spec | None = None        # optional specifications for the parameter, such as help text



def inspect_function_signature(fn: Callable[..., Any]) -> list[Parameter]:
    """Extract parameters from a function signature and return a list of Parameter objects"""
    params = []

    # Get the function signature and resolved type hints, including any `Annotated` metadata
    signature = inspect.signature(fn)
    resolved_hints = get_type_hints(fn, include_extras=True)
    for name, param in signature.parameters.items():

        # Check for unsupported parameter kinds (*args and **kwargs)
        if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
            raise UnsupportedSignatureError(
                f"Parameter '{name}' in {fn.__name__}() is *args or **kwargs, "
                "which defcmd does not support yet."
            )

        # Extract the type annotation and any Spec metadata from the parameter
        annotation = resolved_hints.get(name, param.annotation)
        spec = None

        # If the annotation is an Annotated type, extract the actual type and any Spec from the metadata arguments
        if get_origin(annotation) is Annotated:
            args = get_args(annotation) 
            # Annotated[str, Spec(help="...")] --> args = (str, Spec(help="..."))
            annotation = args[0]
            for extra in args[1:]:
                if isinstance(extra, Spec):
                    spec = extra
                    break

        # Create a Parameter object for each parameter in the function signature and append it to the list
        params.append(
            Parameter(
                name=name,
                annotation=annotation,
                required=param.default is inspect.Parameter.empty, # required if no default value is provided
                default=param.default,
                kind=param.kind,
                spec=spec,
            )
        )

    return params
    