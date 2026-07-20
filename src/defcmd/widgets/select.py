from __future__ import annotations

from .base import Widget
from ..terminal import bold, cyan, green, magenta, inverse, dim, Cursor, raw_mode
from ..terminal.reader import InputReader, DefaultInputReader

class SelectWidget(Widget[str]):
    """A widget that allows the user to select from a list of options"""

    def __init__(
        self,
        prompt: str | None = None,
        *,
        prompt_prefix: str = cyan("? "),
        prompt_suffix: str = ": ",
        help: str | None = None,
        selection_marker: str = magenta("▶"),
        options: list[str],
        default: str | None = None,
        input_reader: InputReader | None = None,   
    ):
        self._prompt = prompt or "select an option"
        self._prompt_prefix = prompt_prefix
        self._prompt_suffix = prompt_suffix
        self._help = help
        self._options = options
        self._default = default
        self._input_reader = input_reader or DefaultInputReader()
        self._value: str | None = None
        self._selection_marker = selection_marker
        self._interacted: bool = False
        self._hint: str = f"  {f'{green('↑↓')}{dim(' to move, ')}{green('enter')}{dim('/')}{green('space')}{dim(' to select')}'}"

        try:
            self._selected: int = 0 if default is None else options.index(default)
        except ValueError:
            raise ValueError(f"Default value '{default}' is not in the list of options: {options}")


    def render(self) -> str:
        """Render the widget as a string for display in the terminal"""
        label = bold(self._prompt) if self._prompt else ""
        if self._help:
            help_text = dim(f" ({self._help})")
            label += f"{help_text}"
        return f"{self._prompt_prefix}{label}{self._prompt_suffix}"
    
    def render_done(self) -> str:
        """Render the final state of the widget after user interaction"""
        label = bold(self._prompt)
        if self._help:
            help_text = dim(f" ({self._help})")
            label += f"{help_text}"
        checkmark = green("✓")
        return f"{checkmark} {label}{self._prompt_suffix}{self._value}"

    def prompt(self) -> str:
        """Prompt the user for input on a loop and return the value"""

        # Print the initial prompt, options and hint
        print(self.render(), flush=True)
        self._render_options()
        if self._hint:
            print(self._hint, flush=True)

        # Enter raw mode to capture keypresses
        with raw_mode():
            while self._value is None:
                key = self._input_reader.read_keypress()

                # Handle keypresses for navigation and selection
                if key == 'up' and self._selected > 0:
                    self._selected -= 1
                    self._rerender_options()
                elif key == 'down' and self._selected < len(self._options) - 1:
                    self._selected += 1
                    self._rerender_options()
                elif key == 'enter' or key == 'space':
                    self._value = self._options[self._selected]
                    break

        # Clear the options and hint from the terminal after selection
        self._clear_options()

        # Move the cursor up one line and clear the line to remove the prompt and options from the terminal
        print(Cursor.up(1), flush=True, end="")
        print(Cursor.clear_to_screen_end(), flush=True, end="")

        # Print the final form of the widget
        print(self.render_done(), flush=True)

        # Return the value of the widget
        return self._value


    def _render_options(self) -> None:
        for i, option in enumerate(self._options):
            marker = self._selection_marker if i == self._selected else " "
            option_str = " " + option + " "
            display = inverse(option_str) if i == self._selected else option_str
            print(f"{dim('|')} {marker} {display}")

    def _rerender_options(self):
        lines = len(self._options) + (1 if self._hint else 0)
        print(Cursor.up(lines) + Cursor.clear_to_screen_end(), end="")
        self._render_options()
        if self._hint:
            print(self._hint, flush=True)

    def _clear_options(self) -> None:
        lines = len(self._options) + (1 if self._hint else 0)
        print(Cursor.up(lines) + Cursor.clear_to_screen_end(), end="")


    @property
    def value(self) -> str:
        if not self._interacted:
            self._interacted = True
            return self.prompt()
        return self._value or self.prompt()
