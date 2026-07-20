import pytest

from defcmd.terminal.ansi import *


class TestANSICode:
    def test_ansi_code_str(self):
        assert str(ANSICode(31)) == "\x1b[31m"

    def test_ansi_code_equality(self):
        assert ANSICode(31) == ANSICode(31)
        assert ANSICode(31) != ANSICode(32)

    def test_ansi_code_unset(self):
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
    def test_ansi_code_wrap(self, code, expected):
        assert code.wrap("Hello") == expected

    def test_ansi_code_call(self):
        code = ANSIColorCode(31)
        assert code("Hello") == "\x1b[31mHello\x1b[39m"

    def test_ansi_code_call_multiple_args(self):
        code = ANSIColorCode(31)
        assert code("Hello", "World") == "\x1b[31mHello World\x1b[39m"


class TestANSIColorCode:
    @pytest.mark.parametrize(
        ("code", "expected"),
        [
            (ANSIColorCode(31).bg, "\x1b[41m"),
            (ANSIColorCode(31).bright, "\x1b[91m"),
            (ANSIColorCode(31).bg.bright, "\x1b[101m"),
        ],
    )
    def test_ansi_color_variants(self, code, expected):
        assert str(code) == expected

    def test_ansi_color_variant_wrap(self):
        code = ANSIColorCode(31).bg.bright
        assert code.wrap("Hello") == "\x1b[101mHello\x1b[109m"


class TestANSICodes:
    def test_ansi_codes_str(self):
        assert str(ANSICodes(31, 1)) == "\x1b[31;1m"

    @pytest.mark.parametrize(
        ("codes", "expected"),
        [
            (ANSICodes(31, 1), "\x1b[31;1mHello\x1b[0m"),
            (ANSICodes(31, 1, 4), "\x1b[31;1;4mHello\x1b[0m"),
        ],
    )
    def test_ansi_codes_wrap(self, codes, expected):
        assert codes.wrap("Hello") == expected

    def test_ansi_codes_call(self):
        codes = ANSICodes(31, 1)
        assert codes("Hello") == "\x1b[31;1mHello\x1b[0m"

    def test_ansi_codes_call_multiple_args(self):
        codes = ANSICodes(31, 1)
        assert codes("Hello", "World") == "\x1b[31;1mHello World\x1b[0m"

    def test_ansi_codes_add(self):
        codes = ANSICodes(31)
        codes.add(1)
        assert str(codes) == "\x1b[31;1m"

    def test_ansi_codes_add_multiple(self):
        codes = ANSICodes(31)
        codes.add(1, 4, ANSICode(7))
        assert str(codes) == "\x1b[31;1;4;7m"


class TestStyles:
    def test_reset(self):
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
    def test_styles(self, style, expected):
        assert str(style) == expected


class TestColors:
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
    def test_colors(self, color, expected):
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
    def test_background_colors(self, color, expected):
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
    def test_bright_colors(self, color, expected):
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
    def test_bright_background_colors(self, color, expected):
        assert str(color) == expected


class TestCompose:
    def test_compose_class(self):
        codes = ANSICodes(bold, red, underline)

        assert str(codes) == "\x1b[1;31;4m"
        assert codes.wrap("Hello") == "\x1b[1;31;4mHello\x1b[0m"

    def test_compose_function(self):
        stylish = compose(bold, red, underline)

        assert str(stylish) == "\x1b[1;31;4m"
        assert stylish("Hello") == "\x1b[1;31;4mHello\x1b[0m"

    def test_compose_function_multiple_args(self):
        stylish = compose(bold, red, underline)

        assert stylish("Hello", "World") == "\x1b[1;31;4mHello World\x1b[0m"

    def test_compose_with_integers(self):
        stylish = compose(1, 31, 4)

        assert str(stylish) == "\x1b[1;31;4m"
        assert stylish("Hello") == "\x1b[1;31;4mHello\x1b[0m"


class TestRGB:
    def test_ansi_rgb_color(self):
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
    def test_rgb_validation(self, r, g, b):
        with pytest.raises(ValueError):
            ANSIRGBColorCode(r, g, b)


class TestCursor:
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
    def test_cursor(self, method, args, expected):
        assert method(*args) == expected


class TestColorFlag:
    def test_is_ansi_enabled_default(self):
        assert is_ansi_enabled() is True


class TestAnsiDisabled:
    """All tests in this class run with ANSI codes disabled, then restore the flag"""

    def setup_method(self):
        set_ansi_enabled(False)

    def teardown_method(self):
        set_ansi_enabled(True)

    def test_flag_functions(self):
        assert is_ansi_enabled() is False
        set_ansi_enabled(True)
        assert is_ansi_enabled() is True
        set_ansi_enabled(False)

    def test_str_returns_empty(self):
        assert str(ANSICode(31)) == ""

    def test_unset_returns_empty(self):
        assert ANSICode(31).unset == ""

    def test_wrap_returns_plain_text(self):
        assert ANSICode(31).wrap("Hello") == "Hello"

    def test_call_returns_plain_text(self):
        assert ANSICode(31)("Hello", "World") == "Hello World"

    def test_color_code_str_returns_empty(self):
        assert str(ANSIColorCode(31)) == ""

    def test_color_code_unset_returns_empty(self):
        assert ANSIColorCode(31).unset == ""

    def test_color_code_wrap_returns_plain_text(self):
        assert ANSIColorCode(31).wrap("Hello") == "Hello"

    def test_rgb_str_returns_empty(self):
        assert str(ANSIRGBColorCode(255, 0, 0)) == ""

    def test_rgb_unset_returns_empty(self):
        assert ANSIRGBColorCode(255, 0, 0).unset == ""

    def test_rgb_wrap_returns_plain_text(self):
        assert ANSIRGBColorCode(255, 0, 0).wrap("Hello") == "Hello"

    def test_codes_str_returns_empty(self):
        assert str(ANSICodes(31, 1)) == ""

    def test_codes_unset_returns_empty(self):
        assert ANSICodes(31, 1).unset == ""

    def test_codes_wrap_returns_plain_text(self):
        assert ANSICodes(31, 1).wrap("Hello") == "Hello"

    def test_codes_call_returns_plain_text(self):
        assert ANSICodes(31, 1)("Hello") == "Hello"

    def test_cursor_unaffected(self):
        assert Cursor.up() == "\x1b[1A"
        assert Cursor.clear_line() == "\x1b[2K"


class TestStripAnsi:
    def test_plain_text_unchanged(self):
        assert strip_ansi("hello world") == "hello world"

    def test_single_ansi_code_stripped(self):
        assert strip_ansi("\x1b[31m") == ""

    def test_text_with_ansi_prefix(self):
        assert strip_ansi("\x1b[31mHello") == "Hello"

    def test_text_with_ansi_surround(self):
        assert strip_ansi("\x1b[1mHello\x1b[0m") == "Hello"

    def test_text_with_ansi_between(self):
        assert strip_ansi("a\x1b[31mb\x1b[0mc") == "abc"

    def test_multiple_codes(self):
        assert strip_ansi("\x1b[1m\x1b[31m\x1b[4mtext") == "text"

    def test_rgb_ansi_stripped(self):
        assert strip_ansi("\x1b[38;2;255;0;0mRed") == "Red"

    def test_bare_escape_not_csi(self):
        assert strip_ansi("\x1bHello") == "\x1bHello"

    def test_empty_string(self):
        assert strip_ansi("") == ""

    def test_only_ansi_returns_empty(self):
        assert strip_ansi("\x1b[1m\x1b[31m") == ""

    def test_cursor_sequences_stripped(self):
        assert strip_ansi("\x1b[2J\x1b[H") == ""
