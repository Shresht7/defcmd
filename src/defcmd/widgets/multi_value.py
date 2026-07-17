from __future__ import annotations

from .base import Widget
from ..terminal import bold, dim, green, red, cyan, Cursor
from ..terminal.reader import InputReader, DefaultInputReader
from ..convert import ValidationError

from typing import Any, Callable



class MultiValueWidget(Widget[list]):
    """A widget that prompts the user for multiple values, one at a time"""

    def __init__(
        self,
        prompt: str,
        *,
        help: str | None = None,
        default: list | None = None,
        converter: Callable[[str], Any] | None = None,
        input_reader: InputReader | None = None,
    ):
        self._prompt = prompt
        self._help = help
        self._default = default or []
        self._converter = converter
        self._input_reader = input_reader or DefaultInputReader()
        self._value: list | None = None


    def render(self) -> str:
        label = bold(self._prompt) if self._prompt else ""
        if self._help:
            label += dim(f" ({self._help})")
        hint = dim(" (leave blank to finish)")
        return f"{cyan("? ")}{label}{hint} "

    
    def render_done(self) -> str:
        label = bold(self._prompt) if self._prompt else ""
        count = len(self._value) if self._value else 0
        summary = dim(f"{count} value(s)")
        return f"{green('✔')} {label}: {summary}"


    def prompt(self) -> list:
        """Prompt the user for multiple values until they leave the input blank"""
        values = []
        index = 1

        while True:
            prompt_text = f"{cyan('? ')}{bold(f'{self._prompt} [{index}]')}{dim(' (leave blank to finish)')} "
            raw = self._input_reader.read(prompt_text).strip()
            if not raw or raw == "":
                break

            val = None
            try:
                val = self._converter(raw) if self._converter else raw
            except ValidationError as e:
                print(f"{red('✖')} {e}")
                continue

            values.append(val)
            index += 1

        print(Cursor.up(index) + Cursor.clear_to_screen_end(), end="", flush=True)
        self._value = values
        print(self.render_done(), flush=True)
        return values
    

    @property
    def value(self) -> list:
        """Return the collected values, or the default if none were collected"""
        if self._value is None:
            self._value = self.prompt()
        return self._value
