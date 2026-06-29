from defcmd.widgets.base import Widget
from defcmd.terminal import bold, dim, raw_mode
from defcmd.terminal.reader import InputReader, DefaultInputReader

_UNSET = object()  # Sentinel value to indicate that no default has been set

class ConfirmWidget(Widget):
    
    def __init__(
            self,
            prompt: str = "Confirm",
            *,
            sep: str = "? ",
            default: bool | None = None,
            input_reader: InputReader | None = None
    ):
        self._prompt = prompt
        self._sep = sep
        self._default = default
        self._value = _UNSET
        self._input_reader = DefaultInputReader() if input_reader is None else input_reader 
        self._interacted: bool = False

    def render(self) -> str:
        label = bold(self._prompt) if self._prompt else ""
        default_str = self._get_default_str()
        return f"{label} {default_str}{self._sep}"

    def _get_default_str(self) -> str:
        res = ""
        if self._default is True:
            res = "[Y/n]"
        elif self._default is False:
            res = "[y/N]"
        else:
            res = "[y/n]"
        return dim(res)

    @property
    def value(self) -> bool:
        if self._value is not _UNSET:
            return bool(self._value)

        prompt_str = self.render()
        print(prompt_str, end="", flush=True)

        with raw_mode():
            while True:
                key = self._input_reader.read_keypress()
                if key == "enter":
                    if self._default is not None:
                        self._value = self._default
                        print()  # Move to the next line after the prompt
                        break
                elif key.lower() == "y":
                    self._value = True
                    print('y')  # Move to the next line after the prompt
                    break
                elif key.lower() == "n":
                    self._value = False
                    print('n')  # Move to the next line after the prompt
                    break
                # If the user presses any other key, we simply ignore it and continue prompting for input.

        return self._value
