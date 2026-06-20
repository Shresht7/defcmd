from __future__ import annotations

from defcmd.introspect import Parameter

def prompt_for_param(param: Parameter, input_fn=input) -> str:
    while True:
        raw = input_fn(f"Enter value for {param.name} ({param.annotation.__name__}): ")
        if raw == "":
            if param.required:
                continue    # If the parameter is required, we can't accept blank input, so we prompt again
            else:
                return param.default
        else:
            return raw
