"""
Base classes for interactive terminal widgets.

This module defines the `Widget` abstract base class, which provides the
common interface implemented by all interactive widgets in defcmd.

A widget is responsible for:

- rendering itself for display in the terminal
- interacting with the user to collect input
- exposing its current value

Concrete widgets, such as text inputs, password prompts, confirmation
dialogs, and selection menus, should inherit from `Widget` and implement
its abstract methods.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")

class Widget(ABC, Generic[T]):
    """Base class for all interactive input widgets"""

    @abstractmethod
    def render(self) -> str:
        """Render the widget as a string for display in the terminal"""
        ...

    @abstractmethod
    def prompt(self) -> T:
        """Prompt the user for input on a loop and return the value"""
        ...

    @property
    @abstractmethod
    def value(self) -> T:
        """Get the current value of the widget."""
        ...
