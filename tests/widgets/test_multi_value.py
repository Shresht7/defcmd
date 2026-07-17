from defcmd.widgets import MultiValueWidget
from defcmd.terminal.reader import ScriptedInputReader

def test_multi_value_collects_values():
    widget = MultiValueWidget(
        prompt="Items",
        input_reader=ScriptedInputReader(values=["a", "b", ""]),
    )
    assert widget.value == ["a", "b"]

def test_multi_value_empty():
    widget = MultiValueWidget(
        prompt="Items",
        input_reader=ScriptedInputReader(values=[""]),
    )
    assert widget.value == []
