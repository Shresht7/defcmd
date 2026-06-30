from defcmd.widgets import TextInputWidget
from defcmd.terminal.reader import ScriptedInputReader

def test_text_input_widget_render():
    widget = TextInputWidget(prompt="Enter your name:")
    rendered = widget.render()
    assert "Enter your name:" in rendered

def test_text_input_widget_value():
    widget = TextInputWidget(prompt="Enter your name:", input_reader=ScriptedInputReader(values=["Alice"]))
    assert widget.value == "Alice"

def test_text_input_widget_default_value():
    widget = TextInputWidget(prompt="Enter your name:", default="Bob", input_reader=ScriptedInputReader(values=[""]))
    assert widget.value == "Bob"

def test_text_input_widget_reprompt_on_empty():
    widget = TextInputWidget(prompt="Enter your name:", input_reader=ScriptedInputReader(values=["", "Charlie"]))
    assert widget.value == "Charlie"
