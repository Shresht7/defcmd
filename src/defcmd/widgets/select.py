from __future__ import annotations

from defcmd.widgets.base import Widget
from defcmd.terminal import bold, cyan, green, magenta, inverse, dim, Cursor, raw_mode
from defcmd.terminal.reader import InputReader, DefaultInputReader

class SelectWidget(Widget):
    
    def __init__(
        self,
        prompt: str | None = None,
        *,
        prompt_prefix: str = cyan("? "),
        prompt_suffix: str = ": ",
        selection_marker: str = magenta("▶"),
        options: list[str],
        default: str | None = None,
        input_reader: InputReader | None = None,   
    ):
        self._prompt = prompt or "select an option"
        self._prompt_prefix = prompt_prefix
        self._prompt_suffix = prompt_suffix
        self._options = options
        self._default = default
        self._input_reader = DefaultInputReader() if input_reader is None else input_reader
        self._value: str | None = None
        self._selection_marker = selection_marker
        self._interacted: bool = False

        try:
            self._selected: int = 0 if default is None else options.index(default)
        except ValueError:
            raise ValueError(f"Default value '{default}' is not in the list of options: {options}")

    def render(self) -> str:
        label = bold(self._prompt) if self._prompt else ""
        return f"{self._prompt_prefix}{label}{self._prompt_suffix}"
    
    def render_done(self) -> str:
        label = bold(self._prompt)
        checkmark = green("✓")
        return f"{checkmark} {label}{self._prompt_suffix}{self._value}"

    @property
    def value(self) -> str:
        print(self.render(), flush=True)

        self._render_options()

        with raw_mode():
            while self._value is None:
                key = self._input_reader.read_keypress()
                if key == 'up' and self._selected > 0:
                    self._selected -= 1
                    self._rerender_options()
                elif key == 'down' and self._selected < len(self._options) - 1:
                    self._selected += 1
                    self._rerender_options()
                elif key == 'enter':
                    self._value = self._options[self._selected]
                    break
        
        self._clear_options()

        print(Cursor.up(1), flush=True, end="")
        print(Cursor.clear_to_screen_end(), flush=True, end="")

        print(self.render_done(), flush=True)

        return self._value

    def _render_options(self) -> None:
        for i, option in enumerate(self._options):
            marker = self._selection_marker if i == self._selected else " "
            option_str = " " + option + " "
            display = inverse(option_str) if i == self._selected else option_str
            print(f"{dim('|')} {marker} {display}")

    def _rerender_options(self):
        # Move the cursor up to the first option
        print(Cursor.up(len(self._options)) + Cursor.clear_to_screen_end(), end="")
        self._render_options()

    def _clear_options(self) -> None:
        # Move the cursor up to the first option and clear the lines
        print(Cursor.up(len(self._options)) + Cursor.clear_to_screen_end(), end="")

