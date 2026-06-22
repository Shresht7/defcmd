"""
Extract command-line interface parameters from a function signature
"""

from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Annotated, Any, get_args, get_origin

from defcmd.spec import Spec

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
    meta: Spec | None = None        # optional metadata for the parameter, such as help text

def inspect_function_signature(fn) -> list[Parameter]:
    """Extract parameters from a function signature and return a list of Parameter objects"""
    params = []

    signature = inspect.signature(fn)
    for name, param in signature.parameters.items():

        # Check for unsupported parameter kinds (*args and **kwargs)
        if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
            raise UnsupportedSignatureError(
                f"Parameter '{name}' in {fn.__name__}() is *args or **kwargs, "
                "which defcmd does not support yet."
            )
 
        annotation = param.annotation   # the type annotation of the parameter, which may be an Annotated type containing metadata
        meta = None                     # optional metadata extracted from the annotation, such as help text, if the annotation is an Annotated type with a Spec instance as extra metadata

        # If the annotation is an Annotated type, extract the actual type annotation and any Spec metadata from it
        if get_origin(annotation) is Annotated:
            args = get_args(annotation) 
            # Annotated[str, Spec(help="...")] --> args = (str, Spec(help="..."))
            annotation = args[0]
            for extra in args[1:]:
                if isinstance(extra, Spec):
                    meta = extra
                    break

        # Create a Parameter object for each parameter in the function signature and append it to the list
        params.append(
            Parameter(
                name=name,
                annotation=annotation,
                required=param.default is inspect.Parameter.empty, # required if no default value is provided
                default=param.default,
                kind=param.kind,
                meta=meta,
            )
        )

    return params
    