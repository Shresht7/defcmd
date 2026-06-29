from defcmd.widgets.base import Widget
from defcmd.terminal import bold, dim, cyan, green, raw_mode, Cursor
from defcmd.terminal.reader import InputReader, DefaultInputReader

_UNSET = object()  # Sentinel value to indicate that no default has been set

class ConfirmWidget(Widget):
    def __init__(
            self,
            prompt: str | None = None,
            *,
            prompt_prefix: str = cyan("? "),
            prompt_suffix: str = ": ",
            default: bool | None = None,
            input_reader: InputReader | None = None
    ):
        self._prompt = prompt or "confirm"
        self._prompt_prefix = prompt_prefix
        self._prompt_suffix = prompt_suffix
        self._default = default
        self._value = _UNSET
        self._value_str = ""
        self._input_reader = DefaultInputReader() if input_reader is None else input_reader 
        self._interacted: bool = False

    def render(self) -> str:
        label = bold(self._prompt) if self._prompt else ""
        default_str = self._get_default_str()
        return f"{self._prompt_prefix}{label} {default_str}{self._prompt_suffix}"

    def _get_default_str(self) -> str:
        res = ""
        if self._default is True:
            res = "[Y/n]"
        elif self._default is False:
            res = "[y/N]"
        else:
            res = "[y/n]"
        return dim(res)

    def render_done(self) -> str:
        label = bold(self._prompt) if self._prompt else ""
        checkmark = green("✓")
        if self._value_str == "":
            self._value_str = "yes" if self._default is True else "no" if self._default is False else ""
        return f"{checkmark} {label}{self._prompt_suffix}{self._value_str}"

    def prompt(self) -> bool:

        # Save the current cursor position
        print(Cursor.save_position(), flush=True, end="")

        # Print the prompt to the terminal
        print(self.render(), flush=True, end="")

        # Enter raw mode to read single keypresses
        with raw_mode():
            while self._value is _UNSET:
                key = self._input_reader.read_keypress()

                if key == "enter":
                    if self._default is not None:
                        self._value = self._default
                elif key.lower() == "y":
                    self._value = True
                    self._value_str = key
                elif key.lower() == "n":
                    self._value = False
                    self._value_str = key

                # If the user presses any other key, we simply ignore it and continue prompting for input.

        # Move the cursor back to the saved position and clear the line
        print(Cursor.restore_position(), flush=True, end="")
        print(Cursor.clear_line(), flush=True, end="")

        # Print the final form of the widget
        print(self.render_done(), flush=True)

        return bool(self._value)

    @property
    def value(self) -> bool:
        if self._value is not _UNSET:
            return bool(self._value)
        return self.prompt()
