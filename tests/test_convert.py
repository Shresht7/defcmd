import pytest

from defcmd.convert import ValidationError, parse_value
from defcmd.spec import Spec

from typing import Annotated


def test_min_on_non_numeric_raises():
    def f(name: Annotated[str, Spec(min=3)]):
        pass

    from defcmd.introspect import inspect_function_signature
    [p] = inspect_function_signature(f)

    with pytest.raises(ValidationError, match="must be a number"):
        parse_value(p, "abc")


def test_max_on_non_numeric_raises():
    def f(name: Annotated[str, Spec(max=10)]):
        pass

    from defcmd.introspect import inspect_function_signature
    [p] = inspect_function_signature(f)

    with pytest.raises(ValidationError, match="must be a number"):
        parse_value(p, "abc")


def test_pattern_on_non_string_raises():
    def f(port: Annotated[int, Spec(pattern=r"^\d+$")]):
        pass

    from defcmd.introspect import inspect_function_signature
    [p] = inspect_function_signature(f)

    with pytest.raises(ValidationError, match="must be a string"):
        parse_value(p, "1234")


def test_parse_value_no_spec():
    def f(name: str):
        pass

    from defcmd.introspect import inspect_function_signature
    [p] = inspect_function_signature(f)

    assert parse_value(p, "Alice") == "Alice"


def test_parse_bool_invalid():
    from defcmd.convert import parse_bool

    with pytest.raises(ValueError, match="please enter a valid boolean"):
        parse_bool("notabool")


def test_parse_value_bool():
    def f(verbose: bool):
        pass

    from defcmd.introspect import inspect_function_signature
    [p] = inspect_function_signature(f)

    assert parse_value(p, "true") is True
    assert parse_value(p, "false") is False
