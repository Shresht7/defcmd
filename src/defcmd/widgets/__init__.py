from defcmd.widgets.base import Widget
from defcmd.widgets.text import TextInputWidget
from defcmd.widgets.confirm import ConfirmWidget
from defcmd.widgets.select import SelectWidget
from defcmd.terminal.reader import InputReader, DefaultInputReader
from defcmd.introspect import Parameter
from defcmd.convert import parse_value

from typing import get_origin, get_args, Literal

def prompt(param: Parameter, input_reader: InputReader | None = None):
    """Prompt the user for input based on the parameter's type and specifications."""
    input_reader = DefaultInputReader() if input_reader is None else input_reader
    widget = auto_widget(param, input_reader=input_reader)
    return widget.value

# IDEA: Consider adding a maximum number of attempts before giving up and raising an exception,
# to avoid infinite loops in case of repeated invalid input.


def auto_widget(param: Parameter, input_reader: InputReader | None = None) -> Widget:
    """Return the appropriate widget class based on the type of the parameter."""

    # If no input reader is provided, use the default input reader.
    input_reader = DefaultInputReader() if input_reader is None else input_reader

    # # Build the prompt string for the parameter, which includes type hints and help text.
    prompt = _build_prompt(param)

    # Determine the default value for the parameter.
    # If the parameter is required, we set the default to None, which will force the user to provide a value.
    # If the parameter is optional, we use the default value specified in the parameter's specifications (if any).
    default = param.default if not param.required else None

    # If the parameter is of type bool, we return a ConfirmWidget, which allows the user to confirm or deny a boolean choice.
    if param.annotation is bool:
        return ConfirmWidget(prompt=prompt, default=default, input_reader=input_reader)
    
    # If the parameter annotation is a Literal, we can extract the allowed choices and return a SelectWidget, which allows the user to select from a list of options.
    origin = get_origin(param.annotation)
    if origin is Literal:
        options = list(get_args(param.annotation))
        return SelectWidget(prompt=prompt, options=options, default=default, input_reader=input_reader)

    # If the parameter is of any other type, we return a TextInputWidget, which allows the user to input text.
    # The TextInputWidget can also handle secret input (e.g., passwords) if specified in the parameter's specifications.    
    return TextInputWidget(
        prompt=prompt,
        default=default,
        converter=lambda raw: parse_value(param, raw),
        secret=param.spec.secret if param.spec else False,
        input_reader=input_reader
    )

def _build_prompt(param: Parameter) -> str:
    """Build a prompt string for the parameter, including type hints and help text."""

    # If the parameter has a custom prompt defined in its specifications, we use that.
    if param.spec and param.spec.prompt:
        return param.spec.prompt

    # # TODO: Can allow substitution of hints like %help% and %choices% in the prompt string, which would be replaced with the actual help text and choices at runtime.

    # If the parameter annotation is a Literal, we can extract the allowed choices and display them to the user in the prompt
    choices = None
    origin = get_origin(param.annotation)
    if origin is Literal:
        choices = list(get_args(param.annotation))
    type_hint = f"({', '.join(choices)})" if choices else f"({param.annotation.__name__})"
    help_hint = f" — {param.spec.help}" if param.spec and param.spec.help else ""
    return f"Enter value for {param.name}{type_hint}{help_hint}:"
