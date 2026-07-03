import pytest

from defcmd.convert import ValidationError, parse_value
from defcmd.spec import Spec

from typing import Literal, Annotated


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


def test_literal_spec():
    def f(name: Literal["Alice", "Bob"]):
        pass

    from defcmd.introspect import inspect_function_signature
    [p] = inspect_function_signature(f)

    assert parse_value(p, "Alice") == "Alice"
    assert parse_value(p, "Bob") == "Bob"

    with pytest.raises(ValidationError, match="invalid choice"):
        parse_value(p, "Charlie")

def test_literal_non_string_choices():
    def f(num: Literal[1, 2, 3]):
        pass

    from defcmd.introspect import inspect_function_signature
    [p] = inspect_function_signature(f)

    assert parse_value(p, "1") == 1
    assert parse_value(p, "2") == 2
    assert parse_value(p, "3") == 3

    with pytest.raises(ValidationError, match="invalid choice"):
        parse_value(p, "4")


def test_literal_mixed_types():
    def f(val: Literal[1, "two", None]):
        pass

    from defcmd.introspect import inspect_function_signature
    [p] = inspect_function_signature(f)

    assert parse_value(p, "1") == 1
    assert parse_value(p, "two") == "two"

    with pytest.raises(ValidationError, match="invalid choice"):
        parse_value(p, "four")


def test_literal_numeric_strings_remain_strings():
    """Literal string choices that look like numbers should not be converted"""
    def f(val: Literal["1", "2", "3"]):
        pass

    from defcmd.introspect import inspect_function_signature
    [p] = inspect_function_signature(f)

    assert parse_value(p, "1") == "1"
    assert parse_value(p, "1") is not 1
    assert parse_value(p, "3") == "3"
