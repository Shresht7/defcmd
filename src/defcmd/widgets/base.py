from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

class Widget(ABC):
    """Base class for all interactive input widgets"""

    @abstractmethod
    def render(self) -> str:
        """Render the widget as a string for display in the terminal"""
        pass

    @property
    @abstractmethod
    def value(self) -> Any:
        """Get the current value of the widget"""
        pass
