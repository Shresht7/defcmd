from __future__ import annotations

from defcmd.widgets.base import Widget
from defcmd.terminal import bold, dim, red, cyan, green, Cursor
from defcmd.terminal.reader import InputReader, DefaultInputReader

from typing import Any, Callable

class TextInputWidget(Widget):
    """
    A widget that allows the user to input text
    
    Attributes:
        prompt (str): The prompt message to display to the user.
        prompt_prefix (str): The prefix to display before the prompt message.
        prompt_suffix (str): The suffix to display after the prompt message.
        help (str): Optional help text to display alongside the prompt.
        default (Any): The default value to use if the user presses enter without providing input.
        secret (bool): Whether the input should be hidden (e.g., for passwords).
        secret_char (str): The character to display when the input is hidden.
        converter (Callable[[str], Any]): A function to convert the raw input string to the desired type.
        input_reader (InputReader): An object responsible for reading user input from the terminal. Used to facilitate testing and customization of input handling. Defaults to DefaultInputReader if not provided.

    Methods:
        `render()`: Renders the widget as a string for display in the terminal.
        `render_done()`: Renders the final state of the widget after user interaction.
        `prompt()`: Prompts the user for input on a loop and returns the value.
        `value()`: Returns the current value of the widget. If the widget has not been interacted with yet, this will prompt the user for input. Otherwise, it will return the cached value
    """

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
        """Render the widget as a string for display in the terminal"""
        label = bold(self._prompt) if self._prompt else ""
        if self._help:
            help = dim(f" ({self._help})")
            label += f"{help}"
        if self._default is not None:
            default = dim(f"[default: {str(self._default)}]")
            label += f" {default}"
        return f"{self._prompt_prefix}{label}{self._prompt_suffix}"

    def render_done(self) -> str:
        """Render the final state of the widget after user interaction"""
        label = bold(self._prompt) if self._prompt else ""
        if self._help:
            help = dim(f" ({self._help})")
            label += f"{help}"
        value = str(self._value) if self._value is not None else ""
        if self._secret:
            value = self._secret_char * len(value)
        checkmark = green("✓")
        return f"{checkmark} {label}{self._prompt_suffix}{value}"


    def prompt(self) -> Any:
        """Prompt the user for input on a loop and return the value"""
        
        prompt = self.render()
        val = None

        # Loop until we get valid input from the user
        while val is None:

            # Read the raw input from the user
            if self._secret:
                raw = self._input_reader.read_secret(prompt, mask_char=self._secret_char).strip()
            else:
                raw = self._input_reader.read(prompt).strip()

            # If the user provides no input and a default value is set, return the default value
            # Otherwise, prompt the user again for input until valid input is received            
            if raw == "":
                if self._default is not None:
                    val = self._default
                    break
                else:
                    print(red(f"✗ error: value is required"))
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
                print(red(f"✗ error: {e}"))
                continue

        # Set the value of the widget to the converted value
        self._value = val

        # Clear the current line and restore the cursor position
        print(Cursor.up(1), flush=True, end="")
        print(Cursor.clear_to_screen_end(), flush=True, end="")

        # Print the final form of the widget
        print(self.render_done(), flush=True)

        # Return the value of the widget
        return self._value

    @property
    def value(self) -> Any:
        """Get the current value of the widget"""
        # Only prompt if we haven't been interacted with yet
        if not self._interacted:
            self._interacted = True
            self._value = self.prompt()
        return self._value
