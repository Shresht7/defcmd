import pytest

from defcmd.introspect import inspect_function_signature
from defcmd.prompt import prompt_for_param
from defcmd.spec import Spec

from typing import Annotated, Literal

def test_required_str_returns_typed_value():
    def f(name: str):
        pass

    [param] = inspect_function_signature(f)
    value = prompt_for_param(param, input_fn=lambda _prompt: "Bob")
    assert value == "Bob"

def test_optional_blank_input_uses_default():
    def f(port: int = 8080):
        pass

    [param] = inspect_function_signature(f)

    # simulate the user hitting Enter with no input
    value = prompt_for_param(param, input_fn=lambda _prompt: "")
    assert value == 8080


def test_required_blank_reprompts_then_succeeds():
    def f(name: str):
        pass

    [param] = inspect_function_signature(f)
    inputs = iter(["", "", "Charlie"])
    value = prompt_for_param(param, input_fn=lambda _prompt: next(inputs))
    assert value == "Charlie"

def test_optional_bool_blank_input_uses_default():
    def f(verbose: bool = False):
        pass

    [p] = inspect_function_signature(f)
    value = prompt_for_param(p, input_fn=lambda _prompt: "")
    assert value is False

@pytest.mark.parametrize("raw,expected", [
    ("true", True), ("yes", True), ("y", True), ("1", True),
    ("false", False), ("no", False), ("n", False), ("0", False),
])
def test_bool_variants(raw, expected):
    def f(verbose: bool = False):
        pass

    [p] = inspect_function_signature(f)
    value = prompt_for_param(p, input_fn=lambda _prompt: raw)
    assert value is expected

def test_bool_invalid_input_reprompts():
    def f(verbose: bool = False):
        pass

    [p] = inspect_function_signature(f)
    inputs = iter(["notabool", "maybe", "yes"])
    value = prompt_for_param(p, input_fn=lambda _prompt: next(inputs))
    assert value is True

def test_int_invalid_then_valid():
    def f(port: int):
        pass

    [p] = inspect_function_signature(f)
    inputs = iter(["notanumber", "totally51", "9090"])
    value = prompt_for_param(p, input_fn=lambda _prompt: next(inputs))
    assert value == 9090
    assert isinstance(value, int)

def test_literal_choice_valid():
    from typing import Literal
    def f(env: Literal["dev", "prod"] = "dev"):
        pass

    [p] = inspect_function_signature(f)
    value = prompt_for_param(p, input_fn=lambda _prompt: "prod")
    assert value == "prod"

def test_literal_invalid_then_valid():
    from typing import Literal
    def f(env: Literal["dev", "prod"] = "dev"):
        pass

    [p] = inspect_function_signature(f)
    inputs = iter(["staging", "dev"])
    value = prompt_for_param(p, input_fn=lambda _prompt: next(inputs))
    assert value == "dev"

def test_spec_help_appears_in_prompt_label():
    def f(host: Annotated[str, Spec(help="target hostname")]):
        pass

    [p] = inspect_function_signature(f)
    seen_prompts = []

    def capture_input(prompt):
        seen_prompts.append(prompt)
        return "myhost"

    prompt_for_param(p, input_fn=capture_input)
    assert "target hostname" in seen_prompts[0]


def test_no_spec_means_no_help_hint():
    def f(host: str):
        pass

    [p] = inspect_function_signature(f)
    seen_prompts = []

    def capture_input(prompt):
        seen_prompts.append(prompt)
        return "myhost"

    prompt_for_param(p, input_fn=capture_input)
    assert "—" not in seen_prompts[0]
