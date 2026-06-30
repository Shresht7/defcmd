import pytest

from defcmd.terminal.reader import (
    DefaultInputReader,
    ScriptedInputReader,
)


# DEFAULT INPUT READER
# --------------------


def test_default_reader_read(monkeypatch):
    monkeypatch.setattr(
        "builtins.input",
        lambda _: "typed input",
    )

    assert DefaultInputReader().read("name:") == "typed input"


def test_default_reader_read_secret(monkeypatch):
    calls = []

    monkeypatch.setattr(
        "defcmd.terminal.reader.getpass",
        lambda prompt, echo_char="*": (
            calls.append((prompt, echo_char)),
            "secret-value",
        )[1],
    )

    result = DefaultInputReader().read_secret(
        "password:",
        mask_char="*",
    )

    assert result == "secret-value"
    assert calls == [("password:", "*")]


def test_default_reader_mask_char_forwarded(monkeypatch):
    calls = []

    monkeypatch.setattr(
        "defcmd.terminal.reader.getpass",
        lambda prompt, echo_char="*": (
            calls.append((prompt, echo_char)),
            "x",
        )[1],
    )

    DefaultInputReader().read_secret(
        "token:",
        mask_char="#",
    )

    assert calls == [("token:", "#")]


def test_default_reader_read_keypress(monkeypatch):
    monkeypatch.setattr(
        "defcmd.terminal.reader.read_keypress",
        lambda: "enter",
    )

    assert DefaultInputReader().read_keypress() == "enter"


# SCRIPTED INPUT READER
# ---------------------


@pytest.fixture
def scripted_reader() -> ScriptedInputReader:
    return ScriptedInputReader(
        values=["Alice", "Bob"],
        secrets=["secret1", "secret2"],
        keypresses=["up", "down", "enter"],
    )


def test_scripted_reader_read(scripted_reader):
    assert scripted_reader.read("name:") == "Alice"
    assert scripted_reader.read("name:") == "Bob"
    assert scripted_reader.prompts == [
        "name:",
        "name:",
    ]


def test_scripted_reader_read_secret(scripted_reader):
    assert scripted_reader.read_secret("password:") == "secret1"
    assert scripted_reader.read_secret("password:") == "secret2"
    assert scripted_reader.secret_prompts == [
        ("password:", "*"),
        ("password:", "*"),
    ]


def test_scripted_reader_read_keypress(scripted_reader):
    assert scripted_reader.read_keypress() == "up"
    assert scripted_reader.read_keypress() == "down"
    assert scripted_reader.read_keypress() == "enter"


def test_scripted_reader_exhausted_values(scripted_reader):
    scripted_reader.read("name:")
    scripted_reader.read("name:")

    with pytest.raises(StopIteration):
        scripted_reader.read("name:")


def test_scripted_reader_exhausted_secrets(scripted_reader):
    scripted_reader.read_secret("password:")
    scripted_reader.read_secret("password:")

    with pytest.raises(StopIteration):
        scripted_reader.read_secret("password:")


def test_scripted_reader_exhausted_keypresses(scripted_reader):
    scripted_reader.read_keypress()
    scripted_reader.read_keypress()
    scripted_reader.read_keypress()

    with pytest.raises(StopIteration):
        scripted_reader.read_keypress()
