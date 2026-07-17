import pytest
import re

from defcmd.introspect import inspect_function_signature
from defcmd.argparser import build_parser, build_argparse_epilog, generate_examples_block
from defcmd.spec import Spec

from typing import Annotated, Literal


_ansi_re = re.compile(r"\x1b\[[0-9;]*m")

# TODO: Should probably be part of the `terminal` module, but for now it's here to help with testing the examples block formatting
# It should also probably use a while loop to walk the string instead of using regex, but this is good enough for now. 
def strip_ansi(text: str) -> str:
    return _ansi_re.sub("", text)


def test_required_str_becomes_positional_argument():
    def f(name: str):
        pass

    params = inspect_function_signature(f)
    parser = build_parser(params)
    ns = parser.parse_args(["Alice"])
    assert ns.name == "Alice"

def test_optional_becomes_flag_with_default():
    def f(port: int = 8080):
        pass

    params = inspect_function_signature(f)
    parser = build_parser(params)
    ns = parser.parse_args([])
    assert ns.port == 8080

    ns2 = parser.parse_args(["--port", "9090"])
    assert type(ns2.port) == int
    assert ns2.port == 9090

def test_bool_flag_true_false():
    def f(verbose: bool = False):
        pass

    params = inspect_function_signature(f)  
    parser = build_parser(params)
    assert parser.parse_args([]).verbose is False
    assert parser.parse_args(["--verbose"]).verbose is True
    assert parser.parse_args(["--no-verbose"]).verbose is False

def test_literal_choices_enforced():
    def f(env: Literal["dev", "prod"] = "dev"):
        pass

    params = inspect_function_signature(f)
    parser = build_parser(params)
    assert parser.parse_args([]).env == "dev"
    assert parser.parse_args(["--env", "prod"]).env == "prod"
    with pytest.raises(SystemExit):
        parser.parse_args(["--env", "staging"])

def test_spec_help_appears_in_help_output(capsys):
    def f(host: Annotated[str, Spec(help="target hostname")]):
        pass

    parser = build_parser(inspect_function_signature(f))
    with pytest.raises(SystemExit):
        parser.parse_args(["--help"])
    captured = capsys.readouterr()
    assert "target hostname" in captured.out

def test_spec_help_appears_for_bool_flags(capsys):
    def f(verbose: Annotated[bool, Spec(help="enable verbose output")] = False):
        pass

    parser = build_parser(inspect_function_signature(f))
    with pytest.raises(SystemExit):
        parser.parse_args(["--help"])

    captured = capsys.readouterr()
    assert "enable verbose output" in captured.out

def test_spec_short_flag_works():
    def f(port: Annotated[int, Spec(short="p", help="port number")] = 8080):
        pass

    parser = build_parser(inspect_function_signature(f))
    ns = parser.parse_args(["-p", "9090"])
    assert ns.port == 9090

def test_min_max_enforced():
    def f(port: Annotated[int, Spec(min=1024, max=65535)] = 8080):
        pass

    parser = build_parser(inspect_function_signature(f))
    assert parser.parse_args([]).port == 8080
    assert parser.parse_args(["--port", "1024"]).port == 1024
    assert parser.parse_args(["--port", "65535"]).port == 65535
    with pytest.raises(SystemExit):
        parser.parse_args(["--port", "443"])
    with pytest.raises(SystemExit):
        parser.parse_args(["--port", "70000"])

def test_pattern_enforced():
    def f(username: Annotated[str, Spec(pattern="^[a-zA-Z0-9_]+$")] = "user123"):
        pass

    parser = build_parser(inspect_function_signature(f))
    assert parser.parse_args([]).username == "user123"
    assert parser.parse_args(["--username", "valid_user"]).username == "valid_user"
    with pytest.raises(SystemExit):
        parser.parse_args(["--username", "invalid-user!"])

def test_pattern_on_positional():
    def f(host: Annotated[str, Spec(pattern=r"\d+\.\d+\.\d+\.\d+")]):
        pass

    parser = build_parser(inspect_function_signature(f))
    assert parser.parse_args(["10.0.0.1"]).host == "10.0.0.1"
    with pytest.raises(SystemExit):
        parser.parse_args(["invalid-host"])

def test_custom_validation_function():
    def validate_port(value):
        if value % 2 != 0:
            raise ValueError("port must be even")

    def f(port: Annotated[int, Spec(validate=validate_port)] = 8080):
        pass

    parser = build_parser(inspect_function_signature(f))
    assert parser.parse_args([]).port == 8080
    assert parser.parse_args(["--port", "8082"]).port == 8082
    with pytest.raises(SystemExit):
        parser.parse_args(["--port", "8081"])


# ENVIRONMENT VARIABLES
# ---------------------


def test_spec_env_single_var_uses_env_value(monkeypatch):
    monkeypatch.setenv("MYAPP_PORT", "9090")

    def f(port: Annotated[int, Spec(env="MYAPP_PORT")] = 8080):
        pass

    parser = build_parser(inspect_function_signature(f))
    args = parser.parse_args([])
    assert args.port == 9090


def test_spec_env_single_var_not_set_uses_default(monkeypatch):
    monkeypatch.delenv("MYAPP_PORT", raising=False)

    def f(port: Annotated[int, Spec(env="MYAPP_PORT")] = 8080):
        pass

    parser = build_parser(inspect_function_signature(f))
    args = parser.parse_args([])
    assert args.port == 8080


def test_spec_env_multiple_vars_uses_first_set(monkeypatch):
    monkeypatch.setenv("MYAPP_PORT", "9090")
    monkeypatch.setenv("MYAPP_ALT_PORT", "8080")

    def f(port: Annotated[int, Spec(env=("MYAPP_ALT_PORT", "MYAPP_PORT"))] = 8000):
        pass

    parser = build_parser(inspect_function_signature(f))
    args = parser.parse_args([])
    assert args.port == 8080  # MYAPP_ALT_PORT is checked first and is set


def test_spec_env_multiple_vars_none_set_uses_default(monkeypatch):
    monkeypatch.delenv("MYAPP_PORT", raising=False)
    monkeypatch.delenv("MYAPP_ALT_PORT", raising=False)

    def f(port: Annotated[int, Spec(env=("MYAPP_ALT_PORT", "MYAPP_PORT"))] = 8000):
        pass

    parser = build_parser(inspect_function_signature(f))
    args = parser.parse_args([])
    assert args.port == 8000  # Default is used since neither env var is set


def test_spec_env_required_becomes_optional(monkeypatch):
    monkeypatch.setenv("MYAPP_PORT", "9090")

    def f(port: Annotated[int, Spec(env="MYAPP_PORT")]):
        pass

    parser = build_parser(inspect_function_signature(f))
    args = parser.parse_args([]) # we don't provide the port, but the env var is set, so it should be used
    assert args.port == 9090  # The env var is used, so the parameter is effectively optional


def test_spec_env_cli_arg_overrides_env(monkeypatch):
    monkeypatch.setenv("MYAPP_PORT", "9090")

    def f(port: Annotated[int, Spec(env="MYAPP_PORT")] = 8080):
        pass

    parser = build_parser(inspect_function_signature(f))
    args = parser.parse_args(["--port", "7070"])  # CLI argument should override the environment variable
    assert args.port == 7070  # The CLI argument is used, not the environment variable


def test_spec_env_bool_flag(monkeypatch):
    monkeypatch.setenv("MYAPP_VERBOSE", "True")

    def f(verbose: Annotated[bool, Spec(env="MYAPP_VERBOSE")] = False):
        pass

    parser = build_parser(inspect_function_signature(f))
    args = parser.parse_args([])
    assert args.verbose is True


def test_spec_env_none_uses_function_default(monkeypatch):
    monkeypatch.delenv("MYAPP_PORT", raising=False)

    def f(port: Annotated[int, Spec(env="MYAPP_PORT")] = 8080):
        pass

    parser = build_parser(inspect_function_signature(f))
    args = parser.parse_args([])
    assert args.port == 8080  # The function default is used since the env var is not set


# EXAMPLES
# --------


def test_generate_examples_block_returns_formatted_block():
    examples = {"Say hello": "greet Alice", "Say goodbye": "greet Bob"}
    result = generate_examples_block(examples)
    assert result is not None
    plain = strip_ansi(result)
    assert plain.startswith("\nexamples:")
    assert "greet Alice        # Say hello" in plain
    assert "greet Bob          # Say goodbye" in plain


def test_generate_examples_block_none_returns_none():
    assert generate_examples_block(None) is None


def test_generate_examples_block_empty_returns_none():
    assert generate_examples_block({}) is None


def test_build_argparse_epilog_examples_only():
    result = build_argparse_epilog(None, {"Say hello": "greet Alice"})
    assert result is not None
    plain = strip_ansi(result)
    assert plain.startswith("\nexamples:")
    assert "greet Alice        # Say hello" in plain


def test_build_argparse_epilog_examples_with_epilog():
    result = build_argparse_epilog("See the docs.", {"Say hello": "greet Alice"})
    assert result is not None
    plain = strip_ansi(result)
    assert "examples:" in plain
    assert "greet Alice        # Say hello" in plain
    assert "See the docs." in plain


def test_build_argparse_epilog_epilog_only():
    result = build_argparse_epilog("See the docs.", None)
    assert result == "See the docs."


def test_build_argparse_epilog_none():
    assert build_argparse_epilog(None, None) is None


# LIST[T]
# -------

def test_list_required_positional():
    def f(items: list[str]):
        pass

    parser = build_parser(inspect_function_signature(f))
    args = parser.parse_args(["a", "b", "c"])
    assert args.items == ["a", "b", "c"]

def test_list_required_empty_rejected():
    def f(items: list[str]):
        pass

    parser = build_parser(inspect_function_signature(f))
    with pytest.raises(SystemExit):
        parser.parse_args([])  # No items provided, should raise an error

def test_list_optional_empty_default():
    def f(items: list[str] = []):
        pass

    parser = build_parser(inspect_function_signature(f))
    args = parser.parse_args([])
    assert args.items == []  # Default empty list is used

def test_list_optional_with_values():
    def f(items: list[str] = []):
        pass

    parser = build_parser(inspect_function_signature(f))
    args = parser.parse_args(["--items", "a", "b"])
    assert args.items == ["a", "b"]  # Provided values override the default empty

def test_list_inner_type_conversion():
    def f(items: list[int]):
        pass

    parser = build_parser(inspect_function_signature(f))
    args = parser.parse_args(["1", "2", "3"])
    assert args.items == [1, 2, 3]  # Strings are converted to integers

def test_list_inner_type_validation():
    def f(items: Annotated[list[int], Spec(min=0, max=10)]):
        pass

    parser = build_parser(inspect_function_signature(f))
    args = parser.parse_args(["1", "5", "10"])
    assert args.items == [1, 5, 10]  # Valid values

    with pytest.raises(SystemExit):
        parser.parse_args(["1", "11"])  # 11 is out of bounds, should raise an error

def test_list_literal_inner_type():
    def f(items: list[Literal["a", "b", "c"]]):
        pass

    parser = build_parser(inspect_function_signature(f))
    args = parser.parse_args(["a", "b"])
    assert args.items == ["a", "b"]  # Valid literals

    with pytest.raises(SystemExit):
        parser.parse_args(["a", "d"])  # 'd' is not a valid literal, should raise an error

def test_list_bool_inner_type():
    def f(items: list[bool]):
        pass

    parser = build_parser(inspect_function_signature(f))
    args = parser.parse_args(["true", "false", "yes", "no"])
    assert args.items == [True, False, True, False]  # Valid boolean representations

    with pytest.raises(SystemExit):
        parser.parse_args(["true", "maybe"])  # 'maybe' is not a valid boolean, should raise an error

def test_list_mixed_positional_and_flag():
    def f(name: str, items: list[str] = []):
        pass

    parser = build_parser(inspect_function_signature(f))
    args = parser.parse_args(["Alice", "--items", "a", "b"])
    assert args.name == "Alice"
    assert args.items == ["a", "b"]  # Positional argument and flag argument

