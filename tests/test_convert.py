import pytest

from pathlib import Path

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


# PATH VALIDATION
# ---------------

def test_parse_value_path():
    def f(data: Path):
        pass

    from defcmd.introspect import inspect_function_signature
    [p] = inspect_function_signature(f)

    result = parse_value(p, "/some/path")
    assert isinstance(result, Path)
    assert result == Path("/some/path")


def test_path_exists_valid(tmp_path):
    d = tmp_path / "existing.txt"
    d.write_text("hello")

    def f(data: Annotated[Path, Spec(path_exists=True)]):
        pass

    from defcmd.introspect import inspect_function_signature
    [p] = inspect_function_signature(f)

    assert parse_value(p, str(d)) == d


def test_path_exists_invalid():
    def f(data: Annotated[Path, Spec(path_exists=True)]):
        pass

    from defcmd.introspect import inspect_function_signature
    [p] = inspect_function_signature(f)

    with pytest.raises(ValidationError, match="does not exist"):
        parse_value(p, "/nonexistent/path")


def test_path_type_file_valid(tmp_path):
    file = tmp_path / "file.txt"
    file.write_text("hello")

    def _(data: Annotated[Path, Spec(path_type="file")]):
        pass

    from defcmd.introspect import inspect_function_signature
    [p] = inspect_function_signature(_)

    assert parse_value(p, str(file)) == file


def test_path_type_file_invalid_wrong_type(tmp_path):
    dir = tmp_path / "adir"
    dir.mkdir()

    def _(data: Annotated[Path, Spec(path_type="file")]):
        pass

    from defcmd.introspect import inspect_function_signature
    [p] = inspect_function_signature(_)

    with pytest.raises(ValidationError, match="not a file"):
        parse_value(p, str(dir))


def test_path_type_dir_valid(tmp_path):
    dir = tmp_path / "adir"
    dir.mkdir()

    def _(data: Annotated[Path, Spec(path_type="dir")]):
        pass

    from defcmd.introspect import inspect_function_signature
    [p] = inspect_function_signature(_)

    assert parse_value(p, str(dir)) == dir


def test_path_type_dir_invalid_wrong_type(tmp_path):
    file = tmp_path / "file.txt"
    file.write_text("hello")

    def _(data: Annotated[Path, Spec(path_type="dir")]):
        pass

    from defcmd.introspect import inspect_function_signature
    [p] = inspect_function_signature(_)

    with pytest.raises(ValidationError, match="not a directory"):
        parse_value(p, str(file))


def test_path_type_without_exists_skips_nonexistent():
    """path_type without path_exists should not error on non-existent paths"""
    def f(data: Annotated[Path, Spec(path_type="file")]):
        pass

    from defcmd.introspect import inspect_function_signature
    [p] = inspect_function_signature(f)

    result = parse_value(p, "/nonexistent/file.txt")
    assert result == Path("/nonexistent/file.txt")
