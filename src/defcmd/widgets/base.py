from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

class Widget(ABC):
    """Base class for all interactive input widgets"""

    @abstractmethod
    def render(self) -> str:
        """Render the widget as a string for display in the terminal"""
        pass

    def prompt(self) -> Any:
        """Prompt the user for input on a loop and return the value"""
        pass

    @property
    @abstractmethod
    def value(self) -> Any:
        """
        Get the current value of the widget.
        If the widget has not been interacted with yet, this will prompt the user for input.
        Otherwise, it will return the cached value.
        """
        pass
