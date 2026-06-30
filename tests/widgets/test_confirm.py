import pytest

from defcmd.widgets import ConfirmWidget
from defcmd.terminal.reader import ScriptedInputReader

def test_confirm_default_true():
    widget = ConfirmWidget(prompt="Are you sure?", default=True, input_reader=ScriptedInputReader(keypresses=["enter"]))
    assert widget.value is True


def test_confirm_default_none():
    widget = ConfirmWidget(input_reader=ScriptedInputReader(keypresses=["y"]))
    assert widget.value is True


def test_confirm_cached_value():
    widget = ConfirmWidget(input_reader=ScriptedInputReader(keypresses=["y"]))
    val1 = widget.value
    val2 = widget.value
    assert val1 is True
    assert val2 is True

@pytest.mark.parametrize(
    ("keypress", "expected"),
    [("y", True), ("Y", True), ("n", False), ("N", False)],
)
def test_confirm_variants(keypress, expected):
    widget = ConfirmWidget(input_reader=ScriptedInputReader(keypresses=[keypress]))
    assert widget.value is expected
