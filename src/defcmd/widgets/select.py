from __future__ import annotations

from defcmd.widgets.base import Widget
from defcmd.terminal import bold, dim, red, inverse, Cursor, raw_mode
from defcmd.terminal.reader import InputReader, DefaultInputReader

class SelectWidget(Widget):
    
    def __init__(
        self,
        prompt: str = "Select an option",
        *,
        separator: str = ": ",
        options: list[str],
        default: str | None = None,
        input_reader: InputReader | None = None,   
    ):
        self._prompt = prompt
        self._separator = separator
        self._options = options
        self._default = default
        self._input_reader = DefaultInputReader() if input_reader is None else input_reader
        self._value: str | None = None
        self._interacted: bool = False

        try:
            self._selected: int = 0 if default is None else options.index(default)
        except ValueError:
            raise ValueError(f"Default value '{default}' is not in the list of options: {options}")

    def render(self) -> str:
        label = bold(self._prompt) if self._prompt else ""
        return f"{label} {self._separator}"

    @property
    def value(self) -> str:
        prompt_str = bold(self._prompt) if self._prompt else ""
        print(prompt_str, flush=True)

        self._render_options()

        with raw_mode():
            while True:
                key = self._input_reader.read_keypress()
                if key == 'up' and self._selected > 0:
                    self._selected -= 1
                    self._rerender_options()
                elif key == 'down' and self._selected < len(self._options) - 1:
                    self._selected += 1
                    self._rerender_options()
                elif key == 'enter':
                    break
        
        self._clear_options()

        self._value = self._options[self._selected]
        return self._value

    def _render_options(self) -> None:
        for i, option in enumerate(self._options):
            marker = ">" if i == self._selected else " "
            display = inverse(option) if i == self._selected else option
            print(f"{marker} {display}")

    def _rerender_options(self):
        # Move the cursor up to the first option
        print(Cursor.up(len(self._options)) + Cursor.clear_to_screen_end(), end="")
        self._render_options()

    def _clear_options(self) -> None:
        # Move the cursor up to the first option and clear the lines
        print(Cursor.up(len(self._options)) + Cursor.clear_to_screen_end(), end="")

