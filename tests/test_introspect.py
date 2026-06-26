import inspect

import pytest

from defcmd.introspect import inspect_function_signature, UnsupportedSignatureError
from defcmd.spec import Spec
from typing import Annotated

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

def test_non_annotated_parameter():
    def f(host: str, port: int):
        pass

    parameters = inspect_function_signature(f)
    assert parameters[0].annotation is str
    assert parameters[0].spec is None
    assert parameters[1].annotation is int
    assert parameters[1].spec is None

def test_annotated_specifications():
    def f(host: Annotated[str, Spec(help="target hostname")], port: int = 8080):
        pass

    params = inspect_function_signature(f)
    host, port = params

    assert host.annotation is str  # unwrapped, not Annotated[...]
    assert host.spec == Spec(help="target hostname")
    assert port.spec is None

def test_spec_validation_survives_introspection():
    def f(port: Annotated[int, Spec(min=1024, max=65535, pattern=r"^\d+$")]):
        pass

    [param] = inspect_function_signature(f)
    assert param.spec and param.spec.min == 1024
    assert param.spec and param.spec.max == 65535
    assert param.spec and param.spec.pattern == r"^\d+$"
