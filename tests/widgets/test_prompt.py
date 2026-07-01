import pytest

from typing import Annotated, Literal

from defcmd.introspect import inspect_function_signature
from defcmd.spec import Spec
from defcmd.widgets import prompt, auto_widget, SelectWidget, ConfirmWidget, TextInputWidget
from defcmd.terminal.reader import ScriptedInputReader

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


def test_spec_prompt_overrides_default_prompt():
    def f(host: Annotated[str, Spec(help="number of hours", prompt="How many hours did it take?")]):
        pass

    [param] = inspect_function_signature(f)
    reader = ScriptedInputReader(values=["myhost"])

    prompt(param, input_reader=reader)
    assert "How many hours did it take?" in reader.prompts[0]


def test_spec_prompt_overrides_bool_prompt():
    def f(verbose: Annotated[bool, Spec(prompt="Enable logging")] = False):
        pass

    [param] = inspect_function_signature(f)
    value = prompt(param, input_reader=ScriptedInputReader(keypresses=["y"]))
    assert value is True


def test_spec_prompt_overrides_literal_prompt():
    def f(env: Annotated[Literal["dev", "prod"], Spec(prompt="Target environment")] = "dev"):
        pass

    [param] = inspect_function_signature(f)
    value = prompt(param, input_reader=ScriptedInputReader(keypresses=["enter"]))
    assert value == "dev"


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

def test_spec_prompt_false_skips_prompt_and_uses_default():
    def f(host: Annotated[str, Spec(prompt=False)] = "localhost"):
        pass

    [param] = inspect_function_signature(f)
    # No input reader passed, would error if it tried to prompt
    value = prompt(param)
    assert value == "localhost"


def test_spec_prompt_false_on_required_raises():
    def f(host: Annotated[str, Spec(prompt=False)]):
        pass

    [param] = inspect_function_signature(f)
    with pytest.raises(ValueError, match="Cannot skip prompt for required parameter"):
        prompt(param)


def test_spec_prompt_false_with_falsy_default():
    def f(count: Annotated[int, Spec(prompt=False)] = 0):
        pass

    [param] = inspect_function_signature(f)
    value = prompt(param)
    assert value == 0


def test_spec_prompt_false_with_none_default():
    def f(name: Annotated[str | None, Spec(prompt=False)] = None):
        pass

    [param] = inspect_function_signature(f)
    value = prompt(param)
    assert value is None


def test_spec_prompt_true_forces_prompt():
    def f(host: Annotated[str, Spec(prompt=True)] = "localhost"):
        pass

    [param] = inspect_function_signature(f)
    value = prompt(param, input_reader=ScriptedInputReader(values=["forced"]))
    assert value == "forced"


def test_spec_prompt_true_overrides_prompt_optional():
    def f(host: Annotated[str, Spec(prompt=True)] = "localhost"):
        pass

    [param] = inspect_function_signature(f)
    value = prompt(param, prompt_optional=False, input_reader=ScriptedInputReader(values=["forced"]))
    assert value == "forced"


def test_prompt_optional_false_skips_optional():
    def f(name: str, port: int = 8080, verbose: bool = False):
        pass

    params = inspect_function_signature(f)
    values = [prompt(p, prompt_optional=False, input_reader=ScriptedInputReader(values=["myapp"])) for p in params]
    assert values == ["myapp", 8080, False]


def test_auto_widget_chooses_correct_widget():
    def f(env: Literal["dev", "prod"] = "dev"):
        pass

    [param] = inspect_function_signature(f)
    widget = auto_widget(param, input_reader=ScriptedInputReader(keypresses=["enter"]))
    assert isinstance(widget, SelectWidget)

    def g(verbose: bool = False):
        pass

    [param2] = inspect_function_signature(g)
    widget2 = auto_widget(param2, input_reader=ScriptedInputReader(keypresses=["y"]))
    assert isinstance(widget2, ConfirmWidget)

    def h(name: str):
        pass

    [param3] = inspect_function_signature(h)
    widget3 = auto_widget(param3, input_reader=ScriptedInputReader(values=["Alice"]))
    assert isinstance(widget3, TextInputWidget)
