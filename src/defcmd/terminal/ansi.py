"""
Utilities for generating ANSI escape sequences.

This module provides objects representing ANSI text styles, colors, and
cursor control sequences. It allows terminal output to be styled using
Python objects instead of manually constructing escape sequences.

The module supports:

- text styles such as bold and underline
- standard and RGB colors
- composing multiple styles
- cursor movement and screen manipulation
"""

from dataclasses import dataclass

# ANSI escape sequences are used to control text formatting, color, and other output options in terminal emulators.
ESCAPE = "\x1b"

# Control Sequence Introducer (CSI) is the prefix for ANSI escape sequences
# that control text formatting, color, and other output options in terminal emulators.
CSI = f"{ESCAPE}["

# ANSI escape code to reset all text formatting and color to default settings.
RESET = f"{CSI}0m"

# The ANSI escape code terminator is the character that indicates the end of an ANSI control sequence.
CSI_TERMINATOR = "m"

# The ANSI escape code delimiter is the character that separates multiple parameters in an ANSI escape sequence.
DELIMITER = ";"

# ---------
# ANSI CODE
# ---------

@dataclass(frozen=True, slots=True)
class ANSICode:
    """Represents a single ANSI escape code for text formatting or color in terminal output."""

    code: int
    unset_code: int = 0

    def __str__(self) -> str:
        return f"{CSI}{self.code}{CSI_TERMINATOR}"
    
    @property
    def unset(self) -> str:
        """Return the ANSI escape code to unset the current formatting or color."""
        return f"{CSI}{self.unset_code}{CSI_TERMINATOR}"

    def wrap(self, text: str) -> str:
        """Wrap the given text with the ANSI escape code to apply formatting."""
        return f"{self}{text}{self.unset}"
    
    def __call__(self, *args: object) -> str:
        return self.wrap(" ".join(str(arg) for arg in args))

# ---------------
# ANSI COLOR CODE
# ---------------

@dataclass(frozen=True, slots=True)
class ANSIColorCode(ANSICode):
    """
    Represents an ANSI color code for text color in terminal output.
    Comes with properties to get the background color and bright variants of the color code.
    """
    
    unset_code: int = 39

    @property
    def bg(self) -> ANSIColorCode:
        """Return a new ANSIColorCode instance with the background color variant of the current code."""
        return ANSIColorCode(self.code + 10, unset_code=self.unset_code + 10)

    @property
    def bright(self) -> ANSIColorCode:
        """Return a new ANSIColorCode instance with the bright variant of the current code."""
        return ANSIColorCode(self.code + 60, unset_code=self.unset_code + 60)

@dataclass(frozen=True, slots=True)
class ANSIRGBColorCode:
    """
    Represents an ANSI RGB color code for text color in terminal output.
    Comes with properties to get the background color and bright variants of the color code.

    ANSI RGB color codes are represented as a sequence of three integers (r, g, b) in the range 0-255.
    The ANSI escape sequence for RGB colors is of the form: "\x1b[38;2;<r>;<g>;<b>m" for foreground colors
    and "\x1b[48;2;<r>;<g>;<b>m" for background colors.
    """
    
    r: int
    g: int
    b: int
    code: int = 38
    unset_code: int = 39

    def __post_init__(self) -> None:
        for name, value in (
            ("r", self.r),
            ("g", self.g),
            ("b", self.b),
        ):
            if not 0 <= value <= 255:
                raise ValueError(f"{name} must be between 0 and 255 (got {value})")

    def __str__(self) -> str:
        return f"{CSI}{self.code};2;{self.r};{self.g};{self.b}{CSI_TERMINATOR}"

    @property
    def unset(self) -> str:
        """Return the ANSI escape code to unset the current RGB color."""
        return f"{CSI}{self.unset_code}{CSI_TERMINATOR}"

    def wrap(self, text: str) -> str:
        """Wrap the given text with the ANSI RGB color code to apply formatting."""
        return f"{self}{text}{self.unset}"

    def __repr__(self) -> str:
        return f"ANSIRGBColorCode(r={self.r}, g={self.g}, b={self.b}, code={self.code}, unset_code={self.unset_code})"

    @property
    def bg(self) -> ANSIRGBColorCode:
        """Return a new ANSIRGBColorCode instance with the background color variant of the current code."""
        return ANSIRGBColorCode(self.r, self.g, self.b, code=self.code + 10, unset_code=self.unset_code + 10)

# ----------
# ANSI CODES
# ----------

class ANSICodes:
    """Represents a collection of ANSI escape codes for text formatting or color in terminal output."""

    def __init__(self, *codes: ANSICode | int):
        self.codes = [code if isinstance(code, ANSICode) else ANSICode(code) for code in codes]

    def __str__(self) -> str:
        return f"{CSI}{DELIMITER.join(str(code.code) for code in self.codes)}{CSI_TERMINATOR}"
    
    def __repr__(self) -> str:
        return f"ANSICodes({', '.join(repr(code) for code in self.codes)})"

    @property
    def unset(self) -> str:
        return RESET

    def wrap(self, text: str) -> str:
        """Wrap the given text with the ANSI escape codes to apply formatting."""
        return f"{self}{text}{self.unset}"
    
    def __call__(self, *args: object) -> str:
        return self.wrap(" ".join(str(arg) for arg in args))

    def add(self, *codes: ANSICode | int) -> ANSICodes:
        """Add one or more ANSI codes to the current set of codes."""
        for code in codes:
            if isinstance(code, ANSICode):
                self.codes.append(code)
            else:
                self.codes.append(ANSICode(code))
        return self

# -------
# COMPOSE
# -------

def compose(*codes: ANSICode | int) -> ANSICodes:
    """Compose multiple ANSI codes into a single ANSICodes instance."""
    return ANSICodes(*codes)

# -----------
# ANSI STYLES
# -----------

reset = ANSICode(0)
bold = ANSICode(1, 22)
dim = ANSICode(2, 22)
italic = ANSICode(3, 23)
underline = ANSICode(4, 24)
inverse = ANSICode(7, 27)
invisible = ANSICode(8, 28)
strikethrough = ANSICode(9, 29)

# -----------
# ANSI COLORS
# -----------

black = ANSIColorCode(30)
red = ANSIColorCode(31)
green = ANSIColorCode(32)
yellow = ANSIColorCode(33)
blue = ANSIColorCode(34)
magenta = ANSIColorCode(35)
cyan = ANSIColorCode(36)
white = ANSIColorCode(37)
default = ANSIColorCode(39)

# ------
# CURSOR
# ------

class Cursor:
    """ANSI escape sequences for cursor movement and visibility control"""

    @staticmethod
    def up(n: int = 1) -> str:
        """Move the cursor up by n lines."""
        return f"{CSI}{n}A"
    
    @staticmethod
    def down(n: int = 1) -> str:
        """Move the cursor down by n lines."""
        return f"{CSI}{n}B"
    
    @staticmethod
    def forward(n: int = 1) -> str:
        """Move the cursor forward (right) by n columns."""
        return f"{CSI}{n}C"
    
    @staticmethod
    def backward(n: int = 1) -> str:
        """Move the cursor backward (left) by n columns."""
        return f"{CSI}{n}D"
    
    @staticmethod
    def column(n: int = 1) -> str:
        """Move the cursor to column n (1-based index)."""
        return f"{CSI}{n}G"

    @staticmethod
    def position(row: int = 1, col: int = 1) -> str:
        """Move the cursor to the specified row and column (1-based index)."""
        return f"{CSI}{row};{col}H"
    
    @staticmethod
    def save_position() -> str:
        """Save the current cursor position."""
        return f"{CSI}s"
    
    @staticmethod
    def restore_position() -> str:
        """Restore the cursor to the last saved position."""
        return f"{CSI}u"
    
    @staticmethod
    def hide() -> str:
        """Hide the cursor."""
        return f"{CSI}?25l"
    
    @staticmethod
    def show() -> str:
        """Show the cursor."""
        return f"{CSI}?25h"
    
    @staticmethod
    def clear_to_line_end() -> str:
        """Clear the line from the cursor position to the end of the line."""
        return f"{CSI}K"
    
    @staticmethod
    def clear_to_line_start() -> str:
        """Clear the line from the cursor position to the start of the line."""
        return f"{CSI}1K"
    
    @staticmethod
    def clear_line() -> str:
        """Clear the entire line."""
        return f"{CSI}2K"
    
    @staticmethod
    def clear_to_screen_end() -> str:
        """Clear the screen from the cursor position to the end of the screen."""
        return f"{CSI}J"
    
    @staticmethod
    def clear_to_screen_start() -> str:
        """Clear the screen from the cursor position to the start of the screen."""
        return f"{CSI}1J"
    
    @staticmethod
    def clear_screen() -> str:
        """Clear the entire screen."""
        return f"{CSI}2J"

# EXPORTS
# -------

__all__ = [
    "ANSICode",
    "ANSIColorCode",
    "ANSIRGBColorCode",
    "ANSICodes",
    "compose",

    "reset",
    "bold",
    "dim",
    "italic",
    "underline",
    "inverse",
    "invisible",
    "strikethrough",

    "black",
    "red",
    "green",
    "yellow",
    "blue",
    "magenta",
    "cyan",
    "white",
    "default",

    "Cursor",
]
