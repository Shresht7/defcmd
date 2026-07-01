from ..introspect import Parameter
from ..terminal.reader import InputReader, DefaultInputReader
from .auto_widget import auto_widget

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
