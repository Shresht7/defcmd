from ..terminal.reader import InputReader, DefaultInputReader
from ..introspect import Parameter
from ..convert import parse_value

from .base import Widget
from .text import TextInputWidget
from .confirm import ConfirmWidget
from .select import SelectWidget
from .multi_value import MultiValueWidget

from typing import get_origin, get_args, Literal


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

    # Handle list[T] for multi-value input
    if origin is list:
        inner_args = get_args(param.annotation)
        inner_type = inner_args[0] if inner_args else str
        synthetic_param = Parameter(name=param.name, annotation=inner_type, required=False, default=None, kind=param.kind, spec=param.spec)
        converter = lambda raw: parse_value(synthetic_param, raw)
        return MultiValueWidget(prompt=prompt, help=help, default=default, converter=converter, input_reader=input_reader)

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
