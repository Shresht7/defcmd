from __future__ import annotations

from defcmd.introspect import Parameter
from typing import get_origin, get_args, Literal

def prompt_for_param(param: Parameter, input_fn=None):

     # Default to the built-in input function if no custom input function is provided
    if input_fn is None:
        input_fn = lambda prompt: input(prompt)

    # If the parameter annotation is a Literal, we can extract the allowed choices and display them to the user in the prompt
    choices = None
    if get_origin(param.annotation) is Literal:
        choices = list(get_args(param.annotation))

    # Determine the hints to display in the prompt based on the parameter annotation
    annotation_hint = f"({param.annotation.__name__})" if choices is None else f"({', '.join(choices)})"
    help_hint = f" — {param.meta.help}" if param.meta and param.meta.help else ""

    # Prompt the user for input until they provide a non-blank value
    # or, if the parameter is optional, they hit Enter to accept the default value
    while True:

        # Use the parameter name and type annotation to create a helpful prompt message
        raw = input_fn(f"Enter value for {param.name}{annotation_hint}{help_hint}: ")

        if raw == "":
            # If the user provided blank input, but the parameter is required, we need to prompt again
            if param.required:
                print(f"{param.name} is required. Please enter a value.")
                continue
            # If the user provided blank input and the parameter is optional, we can return the default value
            else:
                return param.default

        # If the parameter has a set of allowed choices (like a Literal)
        if choices is not None:
            # If the user provided input that matches one of the choices, we can return it directly
            if raw in choices:
                return raw
            # If the user provided invalid input that doesn't match any of the choices, we need to prompt again
            print(f"Invalid choice. Please enter one of the following: {', '.join(choices)}")
            continue
        
        # If the parameter is a boolean, we can accept a variety of common inputs to represent true and false values
        if param.annotation is bool:
            if raw.lower() in ["true", "yes", "y", "1"]:
                return True
            elif raw.lower() in ["false", "no", "n", "0"]:
                return False
            else:
                print("Please enter a valid boolean value (true/false, yes/no, y/n, 1/0)")
                continue

        # For other types, we can attempt to convert the raw input to the correct type using the annotation. If it fails, we prompt again!
        if isinstance(param.annotation, type) and param.annotation is not str:
            try:
                return param.annotation(raw) # Attempt to convert the raw input to the correct type using the annotation
            except (ValueError, TypeError):
                print(f"Please enter a valid {param.annotation.__name__}")
                continue # If the conversion fails, we catch the exception and prompt the user again
        
        # If the annotation is not a type or is just a string, we can return the raw input as-is since there's no type conversion to be done
        return raw
