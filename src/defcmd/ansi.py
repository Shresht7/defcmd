from typing import Any

# ANSI escape sequences are used to control text formatting, color, and other output options in terminal emulators.
ESCAPE = "\x1b"

# Control Sequence Introducer (CSI) is the prefix for ANSI escape sequences
# that control text formatting, color, and other output options in terminal emulators.
CSI = f"{ESCAPE}["

# ANSI escape code to reset all text formatting and color to default settings.
RESET = f"{CSI}0m"

# The ANSI escape code terminator is the character that indicates the end of an ANSI escape sequence.
CSI_TERMINATOR = "m"

# The ANSI escape code delimiter is the character that separates multiple parameters in an ANSI escape sequence.
DELIMITER = ";"

class ANSICode:
    def __init__(self, code: int):
        self.code = code

    def __str__(self) -> str:
        return f"{CSI}{self.code}{CSI_TERMINATOR}"

    def __repr__(self) -> str:
        return f"ANSICode({self.code})"
    
    def wrap(self, text: str) -> str:
        """Wrap the given text with the ANSI escape code to apply formatting."""
        return f"{self}{text}{RESET}"

    # TODO: Add some guards around bg and bright to ensure that the code is in the correct range for background colors and bright colors, respectively.

    @property
    def bg(self) -> ANSICode:
        """Return a new ANSICode instance with the background color variant of the current code."""
        return ANSICode(self.code + 10)

    @property
    def bright(self) -> ANSICode:
        """Return a new ANSICode instance with the bright variant of the current code."""
        return ANSICode(self.code + 60)

    @staticmethod
    def RESET() -> str:
        """Return the ANSI escape code to reset all text formatting and color to default settings."""
        return RESET
    
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.wrap(" ".join(str(arg) for arg in args))

    def __add__(self, other: ANSICode | int) -> ANSICodes:
        """Combine this ANSICode with another ANSICode or an integer to create an ANSICodes instance."""
        if isinstance(other, int):
            other = ANSICode(other)
        return ANSICodes(self, other)
    
    def __radd__(self, other: ANSICode | int) -> ANSICodes:
        """Combine this ANSICode with another ANSICode or an integer to create an ANSICodes instance."""
        if isinstance(other, int):
            other = ANSICode(other)
        return ANSICodes(other, self)

class ANSICodes:
    def __init__(self, *codes: ANSICode | int):
        self.codes = [code if isinstance(code, ANSICode) else ANSICode(code) for code in codes]

    def add(self, *codes: ANSICode | int) -> None:
        """Add one or more ANSI codes to the current set of codes."""
        for code in codes:
            if isinstance(code, ANSICode):
                self.codes.append(code)
            else:
                self.codes.append(ANSICode(code))

    def __str__(self) -> str:
        return f"{CSI}{DELIMITER.join(str(code.code) for code in self.codes)}{CSI_TERMINATOR}"
    
    def __repr__(self) -> str:
        return f"ANSICodes({', '.join(repr(code) for code in self.codes)})"

    def wrap(self, text: str) -> str:
        """Wrap the given text with the ANSI escape codes to apply formatting."""
        return f"{self}{text}{RESET}"
    
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.wrap(" ".join(str(arg) for arg in args))

def compose(*codes: ANSICode | int) -> ANSICodes:
    """Compose multiple ANSI codes into a single ANSICodes instance."""
    return ANSICodes(*codes)

reset = ANSICode(0)
bold = ANSICode(1)
dim = ANSICode(2)
italic = ANSICode(3)
underline = ANSICode(4)
inverse = ANSICode(7)
invisible = ANSICode(8)
strikethrough = ANSICode(9)

black = ANSICode(30)
red = ANSICode(31)
green = ANSICode(32)
yellow = ANSICode(33)
blue = ANSICode(34)
magenta = ANSICode(35)
cyan = ANSICode(36)
white = ANSICode(37)
default = ANSICode(39)
