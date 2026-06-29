import pytest

from defcmd.terminal.reader import DefaultInputReader


def test_default_reader_read(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _p: "typed input")
    assert DefaultInputReader().read("name:") == "typed input"


def test_default_reader_read_secret(monkeypatch):
    calls = []
    monkeypatch.setattr(
        "defcmd.terminal.reader.getpass",
        lambda prompt, echo_char="*": calls.append((prompt, echo_char)) or "secret-value",
    )
    result = DefaultInputReader().read_secret("password:", mask_char="*")
    assert result == "secret-value"
    assert calls[0] == ("password:", "*")


def test_default_reader_read_keypress(monkeypatch):
    monkeypatch.setattr(
        "defcmd.terminal.reader.read_keypress",
        lambda: "enter",
    )
    assert DefaultInputReader().read_keypress() == "enter"


def test_select_widget_render():
    from defcmd.widgets.select import SelectWidget

    w = SelectWidget(prompt="Pick", options=["a", "b"])
    assert "Pick" in w.render()


def test_default_reader_mask_char_forwarded(monkeypatch):
    calls = []
    monkeypatch.setattr(
        "defcmd.terminal.reader.getpass",
        lambda prompt, echo_char="*": calls.append((prompt, echo_char)) or "x",
    )
    DefaultInputReader().read_secret("token:", mask_char="#")
    assert calls[0][1] == "#"
