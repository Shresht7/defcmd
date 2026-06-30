import pytest

from defcmd.terminal.keypress import (
    CSI_KEY_MAP,
    KEY_MAP,
    raw_mode,
    read_keypress,
)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("a", "a"),
        ("\r", "enter"),
        ("\n", "enter"),
        ("\t", "tab"),
        (" ", "space"),
        ("\x7f", "backspace"),
        ("\b", "backspace"),
        ("\x03", "ctrl+c"),
        ("\x04", "ctrl+d"),
        ("\x1b", "escape"),
        ("5", "5"),
        ("Q", "Q"),
        ("-", "-"),
        ("é", "é"),
        ("🙂", "🙂"),
        ("", ""),
    ],
)
def test_read_keypress(raw: str, expected: str):
    assert read_keypress(inject=raw) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("\x1b[A", "up"),
        ("\x1b[B", "down"),
        ("\x1b[C", "right"),
        ("\x1b[D", "left"),
        ("\x1b[H", "home"),
        ("\x1b[F", "end"),
    ],
)
def test_read_keypress_csi(raw: str, expected: str):
    assert read_keypress(inject=raw) == expected


@pytest.mark.parametrize(
    "raw",
    [
        "\x1b[Z",      # Shift+Tab (currently unsupported)
        "\x1bOP",      # F1 (currently unsupported)
        "\x1b[999~",   # Invalid CSI sequence
    ],
)
def test_read_keypress_unknown_sequences(raw: str):
    assert read_keypress(inject=raw) == raw


def test_raw_mode_is_context_manager():
    with raw_mode():
        pass


def test_all_key_map_entries():
    """Every entry in KEY_MAP should normalize correctly."""
    for raw, expected in KEY_MAP.items():
        assert read_keypress(inject=raw) == expected


def test_all_csi_key_map_entries():
    """Every CSI mapping should normalize correctly."""
    for letter, expected in CSI_KEY_MAP.items():
        seq = f"\x1b[{letter}"
        assert read_keypress(inject=seq) == expected
