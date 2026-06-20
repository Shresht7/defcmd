from defcmd.introspect import inspect_function_signature
from defcmd.prompt import prompt_for_param


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
