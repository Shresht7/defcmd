import pytest

from defcmd.terminal.reader import ScriptedInputReader
from defcmd.widgets.select import SelectWidget

def test_select_widget_render():
    w = SelectWidget(prompt="Pick", options=["a", "b"])
    assert "Pick" in w.render()

def test_select_empty_prompt():
    widget = SelectWidget(prompt="", options=["a", "b"], input_reader=ScriptedInputReader(keypresses=["enter"]))
    assert widget.value == "a"

def test_select_down_then_up_then_enter():
    value = SelectWidget(
        prompt="Pick",
        options=["dev", "staging", "prod"],
        input_reader=ScriptedInputReader(keypresses=["down", "up", "enter"])
    ).value
    assert value == "dev"

def test_select_default_not_in_options():
    with pytest.raises(ValueError, match="not in the list of options"):
        SelectWidget(options=["a", "b"], default="c")
