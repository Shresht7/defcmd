import inspect

import pytest

from defcmd.introspect import inspect_function_signature, UnsupportedSignatureError

def test_required_and_optional_parameters():
    def sample_function(a: int, b: str = "default", c: float = 3.14):
        pass

    parameters = inspect_function_signature(sample_function)

    assert len(parameters) == 3

    # Check required parameter
    assert parameters[0].name == "a"
    assert parameters[0].required is True
    assert parameters[0].default is inspect.Parameter.empty

    # Check optional parameter with default value
    assert parameters[1].name == "b"
    assert parameters[1].required is False
    assert parameters[1].default == "default"

    # Check another optional parameter with default value
    assert parameters[2].name == "c"
    assert parameters[2].required is False
    assert parameters[2].default == 3.14

def test_var_positional_rejected():
    def f(*args):
        pass        
    with pytest.raises(UnsupportedSignatureError):
        inspect_function_signature(f)


def test_var_keyword_rejected():
    def f(**kwargs):
        pass
    with pytest.raises(UnsupportedSignatureError):
        inspect_function_signature(f)
