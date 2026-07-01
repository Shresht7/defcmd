from defcmd.widgets.base import Widget
from defcmd.widgets.text import TextInputWidget
from defcmd.widgets.confirm import ConfirmWidget
from defcmd.widgets.select import SelectWidget
from defcmd.terminal.reader import InputReader, DefaultInputReader
from defcmd.introspect import Parameter
from defcmd.convert import parse_value

from typing import get_origin, get_args, Literal

def prompt(param: Parameter, *, prompt_optional: bool = True, input_reader: InputReader | None = None):
    """Prompt the user for input based on the parameter's type and specifications"""

    # If no input reader is provided, use the default input reader
    input_reader = DefaultInputReader() if input_reader is None else input_reader

    # Determine if the parameter has a spec and if it has a prompt attribute. This will help us decide how to prompt the user for input
    spec_prompt = param.spec.prompt if param.spec else None

    # Spec(prompt=False) explicitly skips prompting and uses the default value if available
    if spec_prompt is False:
        # If the parameter is required and has no default, we raise an error
        if param.required:
            raise ValueError(
                f"Cannot skip prompt for required parameter '{param.name}'"
            )
        # Otherwise, we return the default value for the parameter
        return param.default

    # Spec(prompt=True) or Spec(prompt="...") overrides global
    if spec_prompt is True or isinstance(spec_prompt, str):
        widget = auto_widget(param, input_reader=input_reader)
        return widget.value

    # Global prompt_optional flag: skip optional params, use their defaults
    if not prompt_optional and not param.required:
        return param.default

    # Otherwise, prompt the user for input using the appropriate widget based on the parameter's type
    widget = auto_widget(param, input_reader=input_reader)
    return widget.value


def auto_widget(param: Parameter, input_reader: InputReader | None = None) -> Widget:
    """Return the appropriate widget class based on the type of the parameter."""

    # If no input reader is provided, use the default input reader
    input_reader = DefaultInputReader() if input_reader is None else input_reader

    # Determine the prompt to use for the widget
    spec_prompt = param.spec.prompt if param.spec else None
    prompt = param.name
    if isinstance(spec_prompt, str):
        prompt = spec_prompt

    # Determine the help text to use for the widget
    help = param.spec.help if param.spec and param.spec.help else None

    # Determine the default value for the parameter.
    # If the parameter is required, we set the default to None, which will force the user to provide a value.
    # If the parameter is optional, we use the default value specified in the parameter's specifications (if any).
    default = param.default if not param.required else None

    # If the parameter is of type bool, we return a ConfirmWidget, which allows the user to confirm or deny a boolean choice.
    if param.annotation is bool:
        return ConfirmWidget(prompt=prompt, default=default, input_reader=input_reader, help=help)
    
    # If the parameter annotation is a Literal, we can extract the allowed choices and return a SelectWidget, which allows the user to select from a list of options.
    origin = get_origin(param.annotation)
    if origin is Literal:
        options = list(get_args(param.annotation))
        return SelectWidget(prompt=prompt, options=options, default=default, input_reader=input_reader, help=help)

    # If the parameter is of any other type, we return a TextInputWidget, which allows the user to input text.
    # Use the Spec prompt if provided, otherwise fall back to the parameter name as the label.
    return TextInputWidget(
        prompt=prompt,
        help=help,
        converter=lambda raw: parse_value(param, raw),
        secret=param.spec.secret if param.spec else False,
        default=default,
        input_reader=input_reader,
    )
