"""
Extract command-line interface parameters from a function signature
"""

from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class Parameter:
    """Represents a parameter extracted from a function signature"""
    name: str                       # name of the parameter
    annotation: Any                 # type annotation of the parameter
    required: bool                  # whether the parameter is required (no default value)
    default: Any                    # default value of the parameter (if any)
    kind: inspect._ParameterKind    # kind of the parameter (positional, keyword, var-positional, var-keyword)

def inspect_function_signature(fn) -> list[Parameter]:
    """Extract parameters from a function signature and return a list of Parameter objects"""
    params = []

    signature = inspect.signature(fn)
    for name, param in signature.parameters.items():
        params.append(
            Parameter(
                name=name,
                annotation=param.annotation,
                required=param.default is inspect.Parameter.empty, # required if no default value is provided
                default=param.default,
                kind=param.kind,
            )
        )

    return params
    