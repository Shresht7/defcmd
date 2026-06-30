import pytest

from defcmd.terminal.ansi import *

# ---------
# ANSI CODE
# ---------


def test_ansi_code_str():
    assert str(ANSICode(31)) == "\x1b[31m"

def test_ansi_code_equality():
    assert ANSICode(31) == ANSICode(31)
    assert ANSICode(31) != ANSICode(32)

def test_ansi_code_unset():
    code = ANSICode(31, unset_code=39)
    assert code.unset_code == 39
    assert code.unset == "\x1b[39m"


@pytest.mark.parametrize(
    ("code", "expected"),
    [
        (ANSICode(31), "\x1b[31mHello\x1b[0m"),
        (ANSICode(32, unset_code=39), "\x1b[32mHello\x1b[39m"),
        (ANSIColorCode(31), "\x1b[31mHello\x1b[39m"),
    ],
)
def test_ansi_code_wrap(code, expected):
    assert code.wrap("Hello") == expected


def test_ansi_code_call():
    code = ANSIColorCode(31)
    assert code("Hello") == "\x1b[31mHello\x1b[39m"


def test_ansi_code_call_multiple_args():
    code = ANSIColorCode(31)
    assert code("Hello", "World") == "\x1b[31mHello World\x1b[39m"


@pytest.mark.parametrize(
    ("code", "expected"),
    [
        (ANSIColorCode(31).bg, "\x1b[41m"),
        (ANSIColorCode(31).bright, "\x1b[91m"),
        (ANSIColorCode(31).bg.bright, "\x1b[101m"),
    ],
)
def test_ansi_color_variants(code, expected):
    assert str(code) == expected


def test_ansi_color_variant_wrap():
    code = ANSIColorCode(31).bg.bright
    assert code.wrap("Hello") == "\x1b[101mHello\x1b[109m"


# ----------
# ANSI CODES
# ----------


def test_ansi_codes_str():
    assert str(ANSICodes(31, 1)) == "\x1b[31;1m"

@pytest.mark.parametrize(
    ("codes", "expected"),
    [
        (ANSICodes(31, 1), "\x1b[31;1mHello\x1b[0m"),
        (ANSICodes(31, 1, 4), "\x1b[31;1;4mHello\x1b[0m"),
    ],
)

def test_ansi_codes_wrap(codes, expected):
    assert codes.wrap("Hello") == expected


def test_ansi_codes_call():
    codes = ANSICodes(31, 1)
    assert codes("Hello") == "\x1b[31;1mHello\x1b[0m"


def test_ansi_codes_call_multiple_args():
    codes = ANSICodes(31, 1)
    assert codes("Hello", "World") == "\x1b[31;1mHello World\x1b[0m"


def test_ansi_codes_add():
    codes = ANSICodes(31)
    codes.add(1)
    assert str(codes) == "\x1b[31;1m"


def test_ansi_codes_add_multiple():
    codes = ANSICodes(31)
    codes.add(1, 4, ANSICode(7))
    assert str(codes) == "\x1b[31;1;4;7m"


# -----
# USAGE
# -----


def test_reset():
    assert str(reset) == "\x1b[0m"


@pytest.mark.parametrize(
    ("style", "expected"),
    [
        (bold, "\x1b[1m"),
        (dim, "\x1b[2m"),
        (italic, "\x1b[3m"),
        (underline, "\x1b[4m"),
        (inverse, "\x1b[7m"),
        (invisible, "\x1b[8m"),
        (strikethrough, "\x1b[9m"),
    ],
)
def test_styles(style, expected):
    assert str(style) == expected


@pytest.mark.parametrize(
    ("color", "expected"),
    [
        (black, "\x1b[30m"),
        (red, "\x1b[31m"),
        (green, "\x1b[32m"),
        (yellow, "\x1b[33m"),
        (blue, "\x1b[34m"),
        (magenta, "\x1b[35m"),
        (cyan, "\x1b[36m"),
        (white, "\x1b[37m"),
        (default, "\x1b[39m"),
    ],
)
def test_colors(color, expected):
    assert str(color) == expected


@pytest.mark.parametrize(
    ("color", "expected"),
    [
        (black.bg, "\x1b[40m"),
        (red.bg, "\x1b[41m"),
        (green.bg, "\x1b[42m"),
        (yellow.bg, "\x1b[43m"),
        (blue.bg, "\x1b[44m"),
        (magenta.bg, "\x1b[45m"),
        (cyan.bg, "\x1b[46m"),
        (white.bg, "\x1b[47m"),
    ],
)
def test_background_colors(color, expected):
    assert str(color) == expected


@pytest.mark.parametrize(
    ("color", "expected"),
    [
        (black.bright, "\x1b[90m"),
        (red.bright, "\x1b[91m"),
        (green.bright, "\x1b[92m"),
        (yellow.bright, "\x1b[93m"),
        (blue.bright, "\x1b[94m"),
        (magenta.bright, "\x1b[95m"),
        (cyan.bright, "\x1b[96m"),
        (white.bright, "\x1b[97m"),
    ],
)
def test_bright_colors(color, expected):
    assert str(color) == expected


@pytest.mark.parametrize(
    ("color", "expected"),
    [
        (black.bg.bright, "\x1b[100m"),
        (red.bg.bright, "\x1b[101m"),
        (green.bg.bright, "\x1b[102m"),
        (yellow.bg.bright, "\x1b[103m"),
        (blue.bg.bright, "\x1b[104m"),
        (magenta.bg.bright, "\x1b[105m"),
        (cyan.bg.bright, "\x1b[106m"),
        (white.bg.bright, "\x1b[107m"),
    ],
)
def test_bright_background_colors(color, expected):
    assert str(color) == expected


def test_compose_class():
    codes = ANSICodes(bold, red, underline)

    assert str(codes) == "\x1b[1;31;4m"
    assert codes.wrap("Hello") == "\x1b[1;31;4mHello\x1b[0m"


def test_compose_function():
    stylish = compose(bold, red, underline)

    assert str(stylish) == "\x1b[1;31;4m"
    assert stylish("Hello") == "\x1b[1;31;4mHello\x1b[0m"


def test_compose_function_multiple_args():
    stylish = compose(bold, red, underline)

    assert stylish("Hello", "World") == "\x1b[1;31;4mHello World\x1b[0m"


def test_compose_with_integers():
    stylish = compose(1, 31, 4)

    assert str(stylish) == "\x1b[1;31;4m"
    assert stylish("Hello") == "\x1b[1;31;4mHello\x1b[0m"


def test_ansi_rgb_color():
    rgb = ANSIRGBColorCode(255, 12, 25)

    assert str(rgb) == "\x1b[38;2;255;12;25m"
    assert str(rgb.bg) == "\x1b[48;2;255;12;25m"
    assert rgb.wrap("Hello") == "\x1b[38;2;255;12;25mHello\x1b[39m"

@pytest.mark.parametrize(
    ("r", "g", "b"),
    [
        (-1, 0, 0),
        (0, -1, 0),
        (0, 0, -1),
        (256, 0, 0),
        (0, 256, 0),
        (0, 0, 256),
    ],
)
def test_rgb_validation(r, g, b):
    with pytest.raises(ValueError):
        ANSIRGBColorCode(r, g, b)

# ------
# CURSOR
# ------


@pytest.mark.parametrize(
    ("method", "args", "expected"),
    [
        (Cursor.up, (), "\x1b[1A"),
        (Cursor.up, (3,), "\x1b[3A"),
        (Cursor.down, (), "\x1b[1B"),
        (Cursor.down, (5,), "\x1b[5B"),
        (Cursor.forward, (), "\x1b[1C"),
        (Cursor.forward, (10,), "\x1b[10C"),
        (Cursor.backward, (), "\x1b[1D"),
        (Cursor.backward, (4,), "\x1b[4D"),
        (Cursor.column, (5,), "\x1b[5G"),
        (Cursor.position, (3, 5), "\x1b[3;5H"),
        (Cursor.save_position, (), "\x1b[s"),
        (Cursor.restore_position, (), "\x1b[u"),
        (Cursor.hide, (), "\x1b[?25l"),
        (Cursor.show, (), "\x1b[?25h"),
        (Cursor.clear_to_line_end, (), "\x1b[K"),
        (Cursor.clear_to_line_start, (), "\x1b[1K"),
        (Cursor.clear_line, (), "\x1b[2K"),
        (Cursor.clear_to_screen_end, (), "\x1b[J"),
        (Cursor.clear_to_screen_start, (), "\x1b[1J"),
        (Cursor.clear_screen, (), "\x1b[2J"),
    ],
)
def test_cursor(method, args, expected):
    assert method(*args) == expected
