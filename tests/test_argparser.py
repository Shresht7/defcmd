import pytest

from defcmd.introspect import inspect_function_signature
from defcmd.argparser import build_parser

from typing import Literal

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
