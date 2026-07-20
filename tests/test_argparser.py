import pytest
import re
from typing import Annotated, Literal

from defcmd.introspect import inspect_function_signature
from defcmd.argparser import build_parser, build_argparse_epilog, generate_examples_block
from defcmd.spec import Spec


_ansi_re = re.compile(r"\x1b\[[0-9;]*m")

def strip_ansi(text: str) -> str:
    return _ansi_re.sub("", text)


class TestBasicParsing:
    def test_required_str_becomes_positional_argument(self):
        def f(name: str):
            pass

        params = inspect_function_signature(f)
        parser = build_parser(params)
        ns = parser.parse_args(["Alice"])
        assert ns.name == "Alice"

    def test_optional_becomes_flag_with_default(self):
        def f(port: int = 8080):
            pass

        params = inspect_function_signature(f)
        parser = build_parser(params)
        ns = parser.parse_args([])
        assert ns.port == 8080

        ns2 = parser.parse_args(["--port", "9090"])
        assert type(ns2.port) == int
        assert ns2.port == 9090

    def test_bool_flag_true_false(self):
        def f(verbose: bool = False):
            pass

        params = inspect_function_signature(f)
        parser = build_parser(params)
        assert parser.parse_args([]).verbose is False
        assert parser.parse_args(["--verbose"]).verbose is True
        assert parser.parse_args(["--no-verbose"]).verbose is False

    def test_literal_choices_enforced(self):
        def f(env: Literal["dev", "prod"] = "dev"):
            pass

        params = inspect_function_signature(f)
        parser = build_parser(params)
        assert parser.parse_args([]).env == "dev"
        assert parser.parse_args(["--env", "prod"]).env == "prod"
        with pytest.raises(SystemExit):
            parser.parse_args(["--env", "staging"])


class TestSpecDisplay:
    def test_spec_help_appears_in_help_output(self, capsys):
        def f(host: Annotated[str, Spec(help="target hostname")]):
            pass

        parser = build_parser(inspect_function_signature(f))
        with pytest.raises(SystemExit):
            parser.parse_args(["--help"])
        captured = capsys.readouterr()
        assert "target hostname" in captured.out

    def test_spec_help_appears_for_bool_flags(self, capsys):
        def f(verbose: Annotated[bool, Spec(help="enable verbose output")] = False):
            pass

        parser = build_parser(inspect_function_signature(f))
        with pytest.raises(SystemExit):
            parser.parse_args(["--help"])

        captured = capsys.readouterr()
        assert "enable verbose output" in captured.out

    def test_spec_short_flag_works(self):
        def f(port: Annotated[int, Spec(short="p", help="port number")] = 8080):
            pass

        parser = build_parser(inspect_function_signature(f))
        ns = parser.parse_args(["-p", "9090"])
        assert ns.port == 9090


class TestValidation:
    def test_min_max_enforced(self):
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

    def test_pattern_enforced(self):
        def f(username: Annotated[str, Spec(pattern="^[a-zA-Z0-9_]+$")] = "user123"):
            pass

        parser = build_parser(inspect_function_signature(f))
        assert parser.parse_args([]).username == "user123"
        assert parser.parse_args(["--username", "valid_user"]).username == "valid_user"
        with pytest.raises(SystemExit):
            parser.parse_args(["--username", "invalid-user!"])

    def test_pattern_on_positional(self):
        def f(host: Annotated[str, Spec(pattern=r"\d+\.\d+\.\d+\.\d+")]):
            pass

        parser = build_parser(inspect_function_signature(f))
        assert parser.parse_args(["10.0.0.1"]).host == "10.0.0.1"
        with pytest.raises(SystemExit):
            parser.parse_args(["invalid-host"])

    def test_custom_validation_function(self):
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


class TestEnvVars:
    def test_spec_env_single_var_uses_env_value(self, monkeypatch):
        monkeypatch.setenv("MYAPP_PORT", "9090")

        def f(port: Annotated[int, Spec(env="MYAPP_PORT")] = 8080):
            pass

        parser = build_parser(inspect_function_signature(f))
        args = parser.parse_args([])
        assert args.port == 9090

    def test_spec_env_single_var_not_set_uses_default(self, monkeypatch):
        monkeypatch.delenv("MYAPP_PORT", raising=False)

        def f(port: Annotated[int, Spec(env="MYAPP_PORT")] = 8080):
            pass

        parser = build_parser(inspect_function_signature(f))
        args = parser.parse_args([])
        assert args.port == 8080

    def test_spec_env_multiple_vars_uses_first_set(self, monkeypatch):
        monkeypatch.setenv("MYAPP_PORT", "9090")
        monkeypatch.setenv("MYAPP_ALT_PORT", "8080")

        def f(port: Annotated[int, Spec(env=("MYAPP_ALT_PORT", "MYAPP_PORT"))] = 8000):
            pass

        parser = build_parser(inspect_function_signature(f))
        args = parser.parse_args([])
        assert args.port == 8080

    def test_spec_env_multiple_vars_none_set_uses_default(self, monkeypatch):
        monkeypatch.delenv("MYAPP_PORT", raising=False)
        monkeypatch.delenv("MYAPP_ALT_PORT", raising=False)

        def f(port: Annotated[int, Spec(env=("MYAPP_ALT_PORT", "MYAPP_PORT"))] = 8000):
            pass

        parser = build_parser(inspect_function_signature(f))
        args = parser.parse_args([])
        assert args.port == 8000

    def test_spec_env_required_becomes_optional(self, monkeypatch):
        monkeypatch.setenv("MYAPP_PORT", "9090")

        def f(port: Annotated[int, Spec(env="MYAPP_PORT")]):
            pass

        parser = build_parser(inspect_function_signature(f))
        args = parser.parse_args([])
        assert args.port == 9090

    def test_spec_env_cli_arg_overrides_env(self, monkeypatch):
        monkeypatch.setenv("MYAPP_PORT", "9090")

        def f(port: Annotated[int, Spec(env="MYAPP_PORT")] = 8080):
            pass

        parser = build_parser(inspect_function_signature(f))
        args = parser.parse_args(["--port", "7070"])
        assert args.port == 7070

    def test_spec_env_bool_flag(self, monkeypatch):
        monkeypatch.setenv("MYAPP_VERBOSE", "True")

        def f(verbose: Annotated[bool, Spec(env="MYAPP_VERBOSE")] = False):
            pass

        parser = build_parser(inspect_function_signature(f))
        args = parser.parse_args([])
        assert args.verbose is True

    def test_spec_env_none_uses_function_default(self, monkeypatch):
        monkeypatch.delenv("MYAPP_PORT", raising=False)

        def f(port: Annotated[int, Spec(env="MYAPP_PORT")] = 8080):
            pass

        parser = build_parser(inspect_function_signature(f))
        args = parser.parse_args([])
        assert args.port == 8080


class TestExamples:
    def test_generate_examples_block_returns_formatted_block(self):
        examples = {"Say hello": "greet Alice", "Say goodbye": "greet Bob"}
        result = generate_examples_block(examples)
        assert result is not None
        plain = strip_ansi(result)
        assert plain.startswith("\nexamples:")
        assert "greet Alice        # Say hello" in plain
        assert "greet Bob          # Say goodbye" in plain

    def test_generate_examples_block_none_returns_none(self):
        assert generate_examples_block(None) is None

    def test_generate_examples_block_empty_returns_none(self):
        assert generate_examples_block({}) is None

    def test_build_argparse_epilog_examples_only(self):
        result = build_argparse_epilog(None, {"Say hello": "greet Alice"})
        assert result is not None
        plain = strip_ansi(result)
        assert plain.startswith("\nexamples:")
        assert "greet Alice        # Say hello" in plain

    def test_build_argparse_epilog_examples_with_epilog(self):
        result = build_argparse_epilog("See the docs.", {"Say hello": "greet Alice"})
        assert result is not None
        plain = strip_ansi(result)
        assert "examples:" in plain
        assert "greet Alice        # Say hello" in plain
        assert "See the docs." in plain

    def test_build_argparse_epilog_epilog_only(self):
        result = build_argparse_epilog("See the docs.", None)
        assert result == "See the docs."

    def test_build_argparse_epilog_none(self):
        assert build_argparse_epilog(None, None) is None


class TestList:
    def test_list_required_positional(self):
        def f(items: list[str]):
            pass

        parser = build_parser(inspect_function_signature(f))
        args = parser.parse_args(["a", "b", "c"])
        assert args.items == ["a", "b", "c"]

    def test_list_required_empty_rejected(self):
        def f(items: list[str]):
            pass

        parser = build_parser(inspect_function_signature(f))
        with pytest.raises(SystemExit):
            parser.parse_args([])

    def test_list_optional_empty_default(self):
        def f(items: list[str] = []):
            pass

        parser = build_parser(inspect_function_signature(f))
        args = parser.parse_args([])
        assert args.items == []

    def test_list_optional_with_values(self):
        def f(items: list[str] = []):
            pass

        parser = build_parser(inspect_function_signature(f))
        args = parser.parse_args(["--items", "a", "b"])
        assert args.items == ["a", "b"]

    def test_list_inner_type_conversion(self):
        def f(items: list[int]):
            pass

        parser = build_parser(inspect_function_signature(f))
        args = parser.parse_args(["1", "2", "3"])
        assert args.items == [1, 2, 3]

    def test_list_inner_type_validation(self):
        def f(items: Annotated[list[int], Spec(min=0, max=10)]):
            pass

        parser = build_parser(inspect_function_signature(f))
        args = parser.parse_args(["1", "5", "10"])
        assert args.items == [1, 5, 10]

        with pytest.raises(SystemExit):
            parser.parse_args(["1", "11"])

    def test_list_literal_inner_type(self):
        def f(items: list[Literal["a", "b", "c"]]):
            pass

        parser = build_parser(inspect_function_signature(f))
        args = parser.parse_args(["a", "b"])
        assert args.items == ["a", "b"]

        with pytest.raises(SystemExit):
            parser.parse_args(["a", "d"])

    def test_list_bool_inner_type(self):
        def f(items: list[bool]):
            pass

        parser = build_parser(inspect_function_signature(f))
        args = parser.parse_args(["true", "false", "yes", "no"])
        assert args.items == [True, False, True, False]

        with pytest.raises(SystemExit):
            parser.parse_args(["true", "maybe"])

    def test_list_mixed_positional_and_flag(self):
        def f(name: str, items: list[str] = []):
            pass

        parser = build_parser(inspect_function_signature(f))
        args = parser.parse_args(["Alice", "--items", "a", "b"])
        assert args.name == "Alice"
        assert args.items == ["a", "b"]

    def test_list_env_var(self, monkeypatch):
        monkeypatch.setenv("HOSTS", "server1 server2 server3")

        def f(hosts: Annotated[list[str], Spec(env="HOSTS")] = []):
            pass

        parser = build_parser(inspect_function_signature(f))
        args = parser.parse_args([])
        assert args.hosts == ["server1", "server2", "server3"]

    def test_list_env_var_int_conversion(self, monkeypatch):
        monkeypatch.setenv("PORTS", "80 443 8080")

        def f(ports: Annotated[list[int], Spec(env="PORTS")] = []):
            pass

        parser = build_parser(inspect_function_signature(f))
        args = parser.parse_args([])
        assert args.ports == [80, 443, 8080]
