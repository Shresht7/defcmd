import pytest

from defcmd.introspect import inspect_function_signature
from defcmd.argparser import build_parser
from defcmd.spec import Spec

from typing import Annotated, Literal


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
