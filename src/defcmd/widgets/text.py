from __future__ import annotations

from defcmd.widgets.base import Widget
from defcmd.terminal import bold, dim, red, cyan, green, Cursor
from defcmd.terminal.reader import InputReader, DefaultInputReader

from typing import Any, Callable

class TextInputWidget(Widget):
    """A widget that allows the user to input text"""

    def __init__(
            self,
            prompt: str,
            *,
            prompt_prefix: str = cyan("? "),
            prompt_suffix: str = ": ",
            help: str | None = None,
            default: Any = None,
            secret: bool = False,
            secret_char: str = "*",
            converter: Callable[[str], Any] | None = None,
            input_reader: InputReader | None = None,
        ):
        self._prompt = prompt
        self._prompt_prefix = prompt_prefix
        self._prompt_suffix = prompt_suffix
        self._help = help
        self._default = default
        self._secret = secret
        self._secret_char = secret_char
        self._converter = converter
        self._input_reader = DefaultInputReader() if input_reader is None else input_reader
        self._value: Any = default
        self._interacted: bool = False

    def render(self) -> str:
        """Render the prompt string to display"""
        label_str = bold(self._prompt) if self._prompt else ""
        if self._help:
            help_str = dim(f" ({self._help})")
            label_str += f"{help_str}"
        if self._default is not None:
            default_str = dim(f"[default: {str(self._default)}]")
            label_str += f" {default_str}"
        return f"{self._prompt_prefix}{label_str}{self._prompt_suffix}"

    def render_done(self) -> str:
        label_str = bold(self._prompt) if self._prompt else ""
        if self._help:
            help_str = dim(f" ({self._help})")
            label_str += f"{help_str}"
        value_str = str(self._value) if self._value is not None else ""
        if self._secret:
            value_str = self._secret_char * len(value_str)
        checkmark = green("✓")
        return f"{checkmark} {label_str}{self._prompt_suffix}{value_str}"


    def prompt(self) -> Any:
        """Prompt the user for input until valid input is received"""
        
        prompt_str = self.render()
        val = None
        while val is None:

            # Read the raw input from the user
            if self._secret:
                raw = self._input_reader.read_secret(prompt_str, mask_char=self._secret_char).strip()
            else:
                raw = self._input_reader.read(prompt_str).strip()

            # If the user provides no input and a default value is set, return the default value
            # Otherwise, prompt the user again for input until valid input is received            
            if raw == "":
                if self._default is not None:
                    val = self._default
                    break
                else:
                    print(red("Error: Value is required. Please enter a value."))
                continue
            
            # If no converter function is provided, return the raw input as-is
            if self._converter is None:
                val = raw
                break

            # If a converter function is provided, attempt to convert the raw input to the desired type
            # If conversion fails, print the error message and prompt the user again for input
            try:
                val = self._converter(raw)
                break
            except (ValueError, TypeError) as e:
                print(red(f"Error: {e}"))
                continue

        # Set the value of the widget to the converted value
        self._value = val

        # Clear the current line and restore the cursor position
        print(Cursor.up(1), flush=True, end="")
        print(Cursor.clear_to_screen_end(), flush=True, end="")

        # Print the final form of the widget
        print(self.render_done(), flush=True)

        return self._value

    @property
    def value(self) -> Any:
        """Get the current value of the widget"""
        # Only prompt if we haven't been interacted with yet
        if not self._interacted:
            self._interacted = True
            self._value = self.prompt()
        return self._value
