from .base import Widget
from ..terminal import bold, dim, cyan, green, red, raw_mode, Cursor
from ..terminal.reader import InputReader, DefaultInputReader
from typing import Final

UNSET: Final = object()  # Sentinel value to indicate that no default has been set

class ConfirmWidget(Widget[bool]):
    """Interactive yes/no confirmation prompt"""

    def __init__(
            self,
            prompt: str | None = None,
            *,
            prompt_prefix: str = cyan("? "),
            prompt_suffix: str = ": ",
            help: str | None = None,
            default: bool | None = None,
            input_reader: InputReader | None = None
    ):
        self._prompt = prompt or "confirm"
        self._prompt_prefix = prompt_prefix
        self._prompt_suffix = prompt_suffix
        self._help = help
        self._default = default
        self._value = UNSET
        self._input_reader = input_reader or DefaultInputReader()


    def render(self) -> str:
        """Render the widget as a string for display in the terminal"""
        label = bold(self._prompt) if self._prompt else ""
        help = dim(f" ({self._help})") if self._help else ""
        default = self._get_default_hint()
        return f"{self._prompt_prefix}{label}{help} {default}{self._prompt_suffix}"

    def _get_default_hint(self) -> str:
        res = ""
        if self._default is True:
            res = "[Y/n]"
        elif self._default is False:
            res = "[y/N]"
        else:
            res = "[y/n]"
        return dim(res)

    def render_done(self) -> str:
        """Render the final state of the widget after user interaction"""
        label = bold(self._prompt) if self._prompt else ""
        help = dim(f" ({self._help})") if self._help else ""
        value = ""
        if self._value is not UNSET:
            value = green("y") if self._value else red("n")
        checkmark = green("✓")
        return f"{checkmark} {label}{help}{self._prompt_suffix}{value}"


    def prompt(self) -> bool:
        """Prompt the user for input on a loop and return the value"""

        # Save the current cursor position
        print(Cursor.save_position(), flush=True, end="")

        # Print the prompt to the terminal
        print(self.render(), flush=True, end="")

        # Enter raw mode to read single keypresses and handle them
        with raw_mode():
            while self._value is UNSET:
                key = self._input_reader.read_keypress()
                self._handle_key(key)

        # Move the cursor back to the saved position and clear the line
        print(Cursor.restore_position(), flush=True, end="")
        print(Cursor.clear_line(), flush=True, end="")

        # Print the final form of the widget
        print(self.render_done(), flush=True)

        # Return the value as a boolean
        return bool(self._value)

    def _handle_key(self, key: str) -> None:
        """Handle a keypress event and update the widget's state accordingly"""

        key = key.lower()  # Normalize the key to lowercase for easier comparison

        if key == "enter":
            if self._default is not None:
                self._value = self._default

        elif key == "y":
            self._value = True

        elif key == "n":
            self._value = False

        # If the user presses any other key, we simply ignore it and continue prompting for input.


    @property
    def value(self) -> bool:
        """Get the current value of the widget, prompting the user if necessary"""
        if self._value is not UNSET:
            return bool(self._value)    # If the value has already been set, return it as a boolean
        return self.prompt()            # Otherwise, prompt the user for input and return the result as a boolean
