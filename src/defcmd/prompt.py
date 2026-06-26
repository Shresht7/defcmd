from __future__ import annotations

from defcmd.introspect import Parameter
from defcmd.convert import ValidationError, parse_value
from typing import get_origin, get_args, Literal
from getpass import getpass

def prompt_for_param(param: Parameter, input_fn=None):

     # Default to the built-in input function if no custom input function is provided
    if input_fn is None:
        input_fn = lambda prompt: input(prompt)

    # If the parameter annotation is a Literal, we can extract the allowed choices and display them to the user in the prompt
    choices = None
    origin = get_origin(param.annotation)
    if origin is Literal:
        choices = list(get_args(param.annotation))

    # Determine the prompt message to display to the user.
    # If the parameter has a custom prompt defined in its specifications, we use that.
    # Otherwise, we construct a prompt message based on the parameter name, type annotation, and help text (if available).
    prompt = ""
    if param.spec and param.spec.prompt:
        prompt = param.spec.prompt
    else:
        # Determine the hints to display in the prompt based on the parameter annotation
        annotation_hint = f"({param.annotation.__name__})" if choices is None else f"({', '.join(choices)})"
        help_hint = f" — {param.spec.help}" if param.spec and param.spec.help else ""
        prompt = f"Enter value for {param.name}{annotation_hint}{help_hint}:"
    prompt += " "  # Add a space after the prompt for better readability

    # TODO: Can allow substitution of hints like %help% and %choices% in the prompt string, which would be replaced with the actual help text and choices at runtime.

    # Determine if the parameter is a secret (e.g., a password) and should be hidden when prompting.
    is_secret = param.spec.secret if param.spec else False

    # Prompt the user for input until they provide a non-blank value
    # or, if the parameter is optional, they hit Enter to accept the default value
    while True:

        # Prompt the user for input and read the response.
        raw = _prompt(prompt, is_secret=is_secret, input_fn=input_fn)

        if raw == "":
            # If the user provided blank input, but the parameter is required, we need to prompt again
            if param.required:
                print(f"{param.name} is required. Please enter a value.")
                continue
            # If the user provided blank input and the parameter is optional, we can return the default value
            else:
                return param.default
        
        # Parse the user input into the expected type for the parameter
        # If we encounter a ValidationError, print the error message and prompt the user again
        try:
            return parse_value(param, raw)
        except ValidationError as e:
            print(f"Error: {e}")
            continue

        # IDEA: Consider adding a maximum number of attempts before giving up and raising an exception,
        # to avoid infinite loops in case of repeated invalid input.

# ----------------
# HELPER FUNCTIONS
# ----------------

def _prompt(msg: str, is_secret=False, input_fn=None):
    """Prompt the user for input with a given message and return the input value.
    If is_secret is True, the input will be hidden (e.g., for passwords).
    """
    # Default to the built-in input function if no custom input function is provided
    # This allows for mocking the input function for unit tests.
    if input_fn is None:
        input_fn = lambda prompt: input(prompt)

    # If the input is secret, use getpass to hide the input;
    # otherwise, use the provided input function.
    if is_secret:
        response = getpass(msg, echo_char="*")
    else:
        response = input_fn(msg)

    # Trim the response before returning it
    return response.strip()
