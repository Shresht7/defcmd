from __future__ import annotations

from defcmd.introspect import Parameter

def prompt_for_param(param: Parameter, input_fn=input) -> str:
    raw = input_fn(f"Enter value for {param.name} ({param.annotation.__name__}): ")
    if raw == "" and not param.required:
        return param.default
    return raw
