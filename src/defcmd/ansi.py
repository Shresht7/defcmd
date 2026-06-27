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

# ---------
# ANSI CODE
# ---------

class ANSICode:
    """Represents a single ANSI escape code for text formatting or color in terminal output."""

    def __init__(self, code: int, unset_code: int = 0):
        self.code = code
        self.unset_code = unset_code

    def __str__(self) -> str:
        return f"{CSI}{self.code}{CSI_TERMINATOR}"

    def __repr__(self) -> str:
        return f"ANSICode({self.code})"
    
    @property
    def unset(self) -> str:
        """Return the ANSI escape code to unset the current formatting or color."""
        return f"{CSI}{self.unset_code}{CSI_TERMINATOR}"

    def wrap(self, text: str) -> str:
        """Wrap the given text with the ANSI escape code to apply formatting."""
        return f"{self}{text}{self.unset}"
    
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.wrap(" ".join(str(arg) for arg in args))

# ---------------
# ANSI COLOR CODE
# ---------------

class ANSIColorCode(ANSICode):
    """
    Represents an ANSI color code for text color in terminal output.
    Comes with properties to get the background color and bright variants of the color code.
    """
    
    def __init__(self, code: int, unset_code: int = 39):
        super().__init__(code, unset_code)

    @property
    def bg(self) -> ANSIColorCode:
        """Return a new ANSIColorCode instance with the background color variant of the current code."""
        return ANSIColorCode(self.code + 10, unset_code=self.unset_code + 10)

    @property
    def bright(self) -> ANSIColorCode:
        """Return a new ANSIColorCode instance with the bright variant of the current code."""
        return ANSIColorCode(self.code + 60, unset_code=self.unset_code + 60)

class ANSIRGBColorCode(ANSICode):
    """
    Represents an ANSI RGB color code for text color in terminal output.
    Comes with properties to get the background color and bright variants of the color code.
    """
    
    def __init__(self, r: int, g: int, b: int, code: int = 38, unset_code: int = 39):
        # ANSI RGB color codes are represented as a sequence of three integers (r, g, b) in the range 0-255.
        # The ANSI escape sequence for RGB colors is of the form: "\x1b[38;2;<r>;<g>;<b>m" for foreground colors
        # and "\x1b[48;2;<r>;<g>;<b>m" for background colors.
        self.r = r
        self.g = g
        self.b = b
        super().__init__(code=code, unset_code=unset_code)  # 38 is the code for setting foreground color

    def __str__(self) -> str:
        return f"{CSI}{self.code};2;{self.r};{self.g};{self.b}{CSI_TERMINATOR}"

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
    
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.wrap(" ".join(str(arg) for arg in args))

    def add(self, *codes: ANSICode | int) -> None:
        """Add one or more ANSI codes to the current set of codes."""
        for code in codes:
            if isinstance(code, ANSICode):
                self.codes.append(code)
            else:
                self.codes.append(ANSICode(code))

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
