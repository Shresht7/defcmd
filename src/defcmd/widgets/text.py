from __future__ import annotations

from defcmd.widgets.base import Widget
from defcmd.terminal import bold, dim, red
from getpass import getpass

from typing import Any, Callable


class TextInputWidget(Widget):
    """A widget that allows the user to input text"""

    def __init__(
            self,
            prompt: str = "> ",
            *,
            sep: str = " ",
            default: Any = None,
            secret: bool = False,
            secret_char: str = "*",
            converter: Callable[[str], Any] | None = None,
            input_fn: Callable = input,
        ):
        self._prompt = prompt
        self.sep = sep
        self._default = default
        self._secret = secret
        self._secret_char = secret_char
        self._converter = converter
        self._input_fn = input_fn
        self._value: Any = default
        self._interacted: bool = False

    def render(self) -> str:
        """Render the prompt string to display"""
        label_str = bold(self._prompt) if self._prompt else ""
        default_str = dim(f"[{self._default}]" if self._default is not None else "")
        return f"{label_str} {default_str}{self.sep}"

    @property
    def value(self) -> Any:
        """Get the current value of the widget"""
        # Only prompt if we haven't been interacted with yet
        if not self._interacted:
            self._interacted = True
            self._value = self._prompt_loop()
        return self._value

    def _prompt_loop(self) -> Any:
        """Prompt the user for input until valid input is received"""
        
        prompt_str = self.render()
        while True:

            # If secret input is requested, use getpass to hide the input, otherwise use the provided input function
            if self._secret:
                raw = getpass(prompt_str, echo_char=self._secret_char).strip()
            else:
                raw = self._input_fn(prompt_str).strip()

            # If the user provides no input and a default value is set, return the default value
            # Otherwise, prompt the user again for input until valid input is received            
            if raw == "":
                if self._default is not None:
                    return self._default
                print(red("Value is required. Please enter a value."))
                continue
            
            # If no converter function is provided, return the raw input as-is
            if self._converter is None:
                return raw
        
            # If a converter function is provided, attempt to convert the raw input to the desired type
            # If conversion fails, print the error message and prompt the user again for input
            try:
                return self._converter(raw)
            except (ValueError, TypeError) as e:
                print(red(str(e)))
                continue

