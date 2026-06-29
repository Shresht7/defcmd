import pytest

from typing import Annotated, Literal

from defcmd.introspect import inspect_function_signature
from defcmd.spec import Spec
from defcmd.widgets import prompt


class ScriptedInputReader:
    def __init__(self, *, values=(), secrets=(), keypresses=()):
        self._values = iter(values)
        self._secrets = iter(secrets)
        self._keypresses = iter(keypresses)
        self.prompts: list[str] = []
        self.secret_prompts: list[tuple[str, str]] = []

    def read(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return next(self._values)

    def read_secret(self, prompt: str, mask_char: str = "*") -> str:
        self.secret_prompts.append((prompt, mask_char))
        return next(self._secrets)

    def read_keypress(self) -> str:
        return next(self._keypresses)


def test_required_str_returns_typed_value():
    def f(name: str):
        pass

    [param] = inspect_function_signature(f)
    value = prompt(param, input_reader=ScriptedInputReader(values=["Bob"]))
    assert value == "Bob"


def test_optional_blank_input_uses_default():
    def f(port: int = 8080):
        pass

    [param] = inspect_function_signature(f)
    value = prompt(param, input_reader=ScriptedInputReader(values=[""]))
    assert value == 8080


def test_required_blank_reprompts_then_succeeds():
    def f(name: str):
        pass

    [param] = inspect_function_signature(f)
    value = prompt(param, input_reader=ScriptedInputReader(values=["", "", "Charlie"]))
    assert value == "Charlie"


def test_optional_bool_blank_input_uses_default():
    def f(verbose: bool = False):
        pass

    [param] = inspect_function_signature(f)
    value = prompt(param, input_reader=ScriptedInputReader(keypresses=["enter"]))
    assert value is False


@pytest.mark.parametrize(
    ("keypress", "expected"),
    [("y", True), ("Y", True), ("n", False), ("N", False)],
)
def test_bool_variants(keypress, expected):
    def f(verbose: bool = False):
        pass

    [param] = inspect_function_signature(f)
    value = prompt(param, input_reader=ScriptedInputReader(keypresses=[keypress]))
    assert value is expected


def test_bool_invalid_input_reprompts():
    def f(verbose: bool = False):
        pass

    [param] = inspect_function_signature(f)
    value = prompt(param, input_reader=ScriptedInputReader(keypresses=["space", "down", "y"]))
    assert value is True


def test_int_invalid_then_valid():
    def f(port: int):
        pass

    [param] = inspect_function_signature(f)
    value = prompt(param, input_reader=ScriptedInputReader(values=["notanumber", "totally51", "9090"]))
    assert value == 9090
    assert isinstance(value, int)


def test_literal_choice_valid():
    def f(env: Literal["dev", "prod"] = "dev"):
        pass

    [param] = inspect_function_signature(f)
    value = prompt(param, input_reader=ScriptedInputReader(keypresses=["down", "enter"]))
    assert value == "prod"


def test_literal_default_choice_selected_on_enter():
    def f(env: Literal["dev", "prod"] = "dev"):
        pass

    [param] = inspect_function_signature(f)
    value = prompt(param, input_reader=ScriptedInputReader(keypresses=["enter"]))
    assert value == "dev"


def test_spec_help_appears_in_prompt_label():
    def f(host: Annotated[str, Spec(help="target hostname")]):
        pass

    [param] = inspect_function_signature(f)
    reader = ScriptedInputReader(values=["myhost"])

    prompt(param, input_reader=reader)
    assert "target hostname" in reader.prompts[0]


def test_no_spec_means_no_help_hint():
    def f(host: str):
        pass

    [param] = inspect_function_signature(f)
    reader = ScriptedInputReader(values=["myhost"])

    prompt(param, input_reader=reader)
    assert "target hostname" not in reader.prompts[0]


def test_spec_prompt_overrides_default_prompt():
    def f(host: Annotated[str, Spec(help="number of hours", prompt="How many hours did it take?")]):
        pass

    [param] = inspect_function_signature(f)
    reader = ScriptedInputReader(values=["myhost"])

    prompt(param, input_reader=reader)
    assert "How many hours did it take?" in reader.prompts[0]


def test_secret_param_uses_secret_reader():
    def f(password: Annotated[str, Spec(secret=True)]):
        pass

    [param] = inspect_function_signature(f)
    reader = ScriptedInputReader(secrets=["s3cr3t"])

    value = prompt(param, input_reader=reader)

    assert value == "s3cr3t"
    assert reader.secret_prompts[0][1] == "*"
    assert reader.prompts == []


def test_required_secret_blank_reprompts():
    def f(password: Annotated[str, Spec(secret=True)]):
        pass

    [param] = inspect_function_signature(f)
    value = prompt(param, input_reader=ScriptedInputReader(secrets=["", "", "s3cr3t"]))
    assert value == "s3cr3t"


def test_min_reprompts():
    def f(port: Annotated[int, Spec(min=1024)]):
        pass

    [param] = inspect_function_signature(f)
    value = prompt(param, input_reader=ScriptedInputReader(values=["80", "443", "8080"]))
    assert value == 8080


def test_max_reprompts():
    def f(port: Annotated[int, Spec(max=65535)]):
        pass

    [param] = inspect_function_signature(f)
    value = prompt(param, input_reader=ScriptedInputReader(values=["70000", "80000", "65535"]))
    assert value == 65535


def test_pattern_reprompts():
    def f(code: Annotated[str, Spec(pattern=r"^\d{4}$")]):
        pass

    [param] = inspect_function_signature(f)
    value = prompt(param, input_reader=ScriptedInputReader(values=["abc", "12345", "6789"]))
    assert value == "6789"


def test_confirm_default_true():
    def f(verbose: bool = True):
        pass

    [param] = inspect_function_signature(f)
    value = prompt(param, input_reader=ScriptedInputReader(keypresses=["enter"]))
    assert value is True


def test_confirm_default_none():
    def f(explicit: bool):
        pass

    [param] = inspect_function_signature(f)
    value = prompt(param, input_reader=ScriptedInputReader(keypresses=["y"]))
    assert value is True


def test_confirm_cached_value():
    def f(verbose: bool = False):
        pass

    [param] = inspect_function_signature(f)
    reader = ScriptedInputReader(keypresses=["y"])
    widget = _auto_widget(param, reader)
    val1 = widget.value
    val2 = widget.value
    assert val1 is True
    assert val2 is True


def test_select_down_then_up_then_enter():
    def f(env: Literal["dev", "staging", "prod"] = "dev"):
        pass

    [param] = inspect_function_signature(f)
    value = prompt(param, input_reader=ScriptedInputReader(keypresses=["down", "up", "enter"]))
    assert value == "dev"


def test_select_empty_prompt():
    from defcmd.widgets.select import SelectWidget

    widget = SelectWidget(prompt="", options=["a", "b"], input_reader=ScriptedInputReader(keypresses=["enter"]))
    assert widget.value == "a"


def test_select_default_not_in_options():
    from defcmd.widgets.select import SelectWidget

    with pytest.raises(ValueError, match="not in the list of options"):
        SelectWidget(options=["a", "b"], default="c")


def test_text_no_converter():
    def f(name: str):
        pass

    from defcmd.introspect import inspect_function_signature
    from defcmd.widgets import prompt

    [param] = inspect_function_signature(f)
    reader = ScriptedInputReader(values=["Alice"])
    widget = _auto_widget(param, reader)
    widget._converter = None
    assert widget.value == "Alice"


from defcmd.widgets import auto_widget as _auto_widget
