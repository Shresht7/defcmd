import pytest
import re

from defcmd.runner import cmd, CLI
from defcmd.spec import Spec
from typing import Annotated


_ansi_re = re.compile(r"\x1b\[[0-9;]*m")

def strip_ansi(text: str) -> str:
    return _ansi_re.sub("", text)

def test_full_argv_runs_without_prompting(monkeypatch):
    calls = []

    @cmd
    def deploy(host: str, port: int = 8080, verbose: bool = False):
        calls.append((host, port, verbose))

    monkeypatch.setattr("builtins.input", lambda *_: (_ for _ in ()).throw(AssertionError("should not prompt")))

    deploy.run(["localhost", "--port", "1234", "--verbose"])
    assert calls == [("localhost", 1234, True)]

def test_run_with_default_argv(monkeypatch):
    calls = []

    @cmd
    def deploy(host: str, port: int = 8080):
        calls.append((host, port))

    monkeypatch.setattr("sys.argv", ["script.py", "localhost", "--port", "9090"])
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)

    deploy.run()
    assert calls == [("localhost", 9090)]


def test_empty_argv_in_real_terminal_runs_wizard(monkeypatch):
    calls = []

    @cmd
    def deploy(host: str, port: int = 8080, verbose: bool = False):
        calls.append((host, port, verbose))

    monkeypatch.setattr("sys.stdin.isatty", lambda: True)

    prompted = iter(["wizardhost", 9090, True])
    monkeypatch.setattr("defcmd.runner.prompt", lambda _param, **kw: next(prompted))

    deploy.run([])
    assert calls == [("wizardhost", 9090, True)]


def test_cmd_prompt_optional_false_skips_optional_params(monkeypatch):
    calls = []

    @cmd(prompt_optional=False)
    def deploy(host: str, port: int = 8080, verbose: bool = False):
        calls.append((host, port, verbose))

    monkeypatch.setattr("sys.stdin.isatty", lambda: True)
    monkeypatch.setattr("builtins.input", lambda _: "myhost")

    deploy.run([])
    assert calls == [("myhost", 8080, False)]


def test_cmd_prompt_optional_false_with_spec_prompt_true_override(monkeypatch):
    calls = []
    inputs = iter(["myhost", "9090"])

    @cmd(prompt_optional=False)
    def deploy(
        host: str,
        port: Annotated[int, Spec(prompt=True)] = 8080,
        verbose: bool = False,
    ):
        calls.append((host, port, verbose))

    monkeypatch.setattr("sys.stdin.isatty", lambda: True)
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    deploy.run([])
    assert calls == [("myhost", 9090, False)]


def test_cmd_description_override():
    @cmd(description="custom desc")
    def deploy(host: str, port: int = 8080):
        """docstring desc"""

    assert deploy.description == "custom desc"


def test_cmd_description_falls_back_to_docstring():
    @cmd
    def deploy(host: str, port: int = 8080):
        """docstring desc"""

    assert deploy.description == "docstring desc"


def test_cmd_description_defaults_to_none_when_no_docstring():
    @cmd
    def deploy(host: str, port: int = 8080):
        pass

    assert deploy.description is None


def test_cli_subcmd_description_override():
    cli = CLI()

    @cli.subcmd(description="custom desc")
    def greet(name: str):
        """docstring desc"""

    assert cli.commands["greet"].description == "custom desc"


def test_cli_subcmd_description_falls_back_to_docstring():
    cli = CLI()

    @cli.subcmd
    def greet(name: str):
        """docstring desc"""

    assert cli.commands["greet"].description == "docstring desc"


def test_cmd_help_override():
    @cmd(help="short help")
    def deploy(host: str, port: int = 8080):
        """docstring desc"""

    assert deploy.help == "short help"


def test_cmd_help_falls_back_to_description():
    @cmd(description="long desc")
    def deploy(host: str, port: int = 8080):
        """docstring desc"""

    assert deploy.help == "long desc"


def test_cmd_help_falls_back_to_docstring():
    @cmd
    def deploy(host: str, port: int = 8080):
        """docstring desc"""

    assert deploy.help == "docstring desc"


def test_cmd_help_defaults_to_none():
    @cmd
    def deploy(host: str, port: int = 8080):
        pass

    assert deploy.help is None


def test_cli_subcmd_help_override():
    cli = CLI()

    @cli.subcmd(help="short help")
    def greet(name: str):
        """docstring desc"""

    assert cli.commands["greet"].help == "short help"


def test_cli_subcmd_help_falls_back_to_description():
    cli = CLI()

    @cli.subcmd(description="long desc")
    def greet(name: str):
        """docstring desc"""

    assert cli.commands["greet"].help == "long desc"


def test_cli_subcmd_help_falls_back_to_docstring():
    cli = CLI()

    @cli.subcmd
    def greet(name: str):
        """docstring desc"""

    assert cli.commands["greet"].help == "docstring desc"


def test_cmd_epilog_override():
    @cmd(epilog="see also: --help")
    def deploy(host: str):
        pass

    assert deploy.epilog == "see also: --help"


def test_cmd_epilog_defaults_to_none():
    @cmd
    def deploy(host: str):
        pass

    assert deploy.epilog is None


def test_cli_subcmd_epilog_override():
    cli = CLI()

    @cli.subcmd(epilog="see also: --help")
    def greet(name: str):
        pass

    assert cli.commands["greet"].epilog == "see also: --help"


def test_cli_subcmd_epilog_defaults_to_none():
    cli = CLI()

    @cli.subcmd
    def greet(name: str):
        pass

    assert cli.commands["greet"].epilog is None


def test_cli_subcmd_aliases_override():
    cli = CLI()

    @cli.subcmd(aliases=["ls", "list"])
    def greet(name: str):
        pass

    assert cli.commands["greet"].aliases == ["ls", "list"]


def test_cli_subcmd_aliases_defaults_to_none():
    cli = CLI()

    @cli.subcmd
    def greet(name: str):
        pass

    assert cli.commands["greet"].aliases is None


def test_cmd_hidden_defaults_to_false():
    @cmd
    def deploy(host: str):
        pass

    assert deploy.hidden is False


def test_cmd_hidden_true():
    @cmd(hidden=True)
    def deploy(host: str):
        pass

    assert deploy.hidden is True


def test_cli_subcmd_hidden_true():
    cli = CLI()

    @cli.subcmd(hidden=True)
    def greet(name: str):
        pass

    assert cli.commands["greet"].hidden is True


def test_cli_subcmd_hidden_excluded_from_interactive(monkeypatch):
    cli = CLI()

    @cli.subcmd
    def visible_cmd(name: str):
        pass

    @cli.subcmd(hidden=True)
    def hidden_cmd(name: str):
        pass

    monkeypatch.setattr("sys.stdin.isatty", lambda: True)
    monkeypatch.setattr("builtins.input", lambda _: "Alice")

    captured = {}
    monkeypatch.setattr("defcmd.runner.SelectWidget", lambda **kw: captured.update(kw) or type("", (), {"value": "visible_cmd"})())

    cli.run([])
    assert "hidden_cmd" not in captured["options"]
    assert "visible_cmd" in captured["options"]


def test_cli_subcmd_hidden_still_callable_via_argv(monkeypatch):
    cli = CLI()
    calls = []

    @cli.subcmd(hidden=True)
    def greet(name: str):
        calls.append(name)

    monkeypatch.setattr("sys.stdin.isatty", lambda: False)

    cli.run(["greet", "Alice"])
    assert calls == ["Alice"]


def test_cmd_version_override():
    @cmd(version="1.0.0")
    def deploy(host: str):
        pass

    assert deploy.version == "1.0.0"


def test_cmd_version_defaults_to_none():
    @cmd
    def deploy(host: str):
        pass

    assert deploy.version is None


def test_cmd_version_flag(monkeypatch):
    @cmd(version="1.0.0")
    def deploy(host: str):
        pass

    monkeypatch.setattr("sys.stdin.isatty", lambda: False)

    with pytest.raises(SystemExit) as exc:
        deploy.run(["--version"])
    assert exc.value.code == 0


def test_cli_version_override():
    cli = CLI(version="2.0.0")
    assert cli.version == "2.0.0"


def test_cli_version_flag(monkeypatch):
    cli = CLI(version="2.0.0")

    monkeypatch.setattr("sys.stdin.isatty", lambda: False)

    with pytest.raises(SystemExit) as exc:
        cli.run(["--version"])
    assert exc.value.code == 0


def test_cli_subcmd_prompt_optional_false(monkeypatch):
    cli = CLI()
    calls = []

    @cli.subcmd(prompt_optional=False)
    def greet(name: str, times: int = 1):
        calls.append((name, times))

    monkeypatch.setattr("sys.stdin.isatty", lambda: True)
    monkeypatch.setattr("defcmd.runner.SelectWidget", lambda **kw: type("", (), {"value": "greet"})())
    monkeypatch.setattr("builtins.input", lambda _: "Alice")

    cli.run([])
    assert calls == [("Alice", 1)]


# EXAMPLES
# --------


def test_cmd_examples_in_help(capsys):
    @cmd(examples={"Say hello to Alice": "greet Alice"})
    def greet(name: str):
        pass

    with pytest.raises(SystemExit):
        greet.run(["--help"])
    out = strip_ansi(capsys.readouterr().out)
    assert "examples:" in out
    assert "greet Alice        # Say hello to Alice" in out


def test_cmd_examples_with_epilog(capsys):
    @cmd(
        examples={"Say hello to Alice": "greet Alice"},
        epilog="See the docs for more info.",
    )
    def greet(name: str):
        pass

    with pytest.raises(SystemExit):
        greet.run(["--help"])
    out = strip_ansi(capsys.readouterr().out)
    assert "examples:" in out
    assert "greet Alice        # Say hello to Alice" in out
    assert "See the docs for more info." in out


def test_cmd_examples_none_omits_block(capsys):
    @cmd
    def greet(name: str):
        pass

    with pytest.raises(SystemExit):
        greet.run(["--help"])
    out = strip_ansi(capsys.readouterr().out)
    assert "examples:" not in out


def test_cli_top_level_examples_in_help(capsys):
    cli = CLI(examples={"Say hello": "greet Alice"})

    @cli.subcmd
    def greet(name: str):
        pass

    with pytest.raises(SystemExit):
        cli.run(["--help"])
    out = strip_ansi(capsys.readouterr().out)
    assert "examples:" in out
    assert "greet Alice        # Say hello" in out


def test_cli_subcommand_examples_in_help(capsys):
    cli = CLI()

    @cli.subcmd(examples={"With feeling": "greet Alice"})
    def greet(name: str):
        pass

    with pytest.raises(SystemExit):
        cli.run(["greet", "--help"])
    out = strip_ansi(capsys.readouterr().out)
    assert "examples:" in out
    assert "greet Alice        # With feeling" in out


def test_cmd_examples_flag_suppressed(capsys):
    @cmd(examples={"Say hello to Alice": "greet Alice"}, add_examples_flag=False)
    def greet(name: str):
        pass

    with pytest.raises(SystemExit):
        greet.run(["--help"])
    out = strip_ansi(capsys.readouterr().out)
    assert "--examples" not in out
    assert "examples:" in out
    assert "greet Alice        # Say hello to Alice" in out


def test_cmd_examples_flag_default(capsys):
    @cmd(examples={"Say hello to Alice": "greet Alice"})
    def greet(name: str):
        pass

    with pytest.raises(SystemExit):
        greet.run(["--help"])
    out = strip_ansi(capsys.readouterr().out)
    assert "--examples" in out


def test_cli_top_level_examples_flag_suppressed(capsys):
    cli = CLI(examples={"Say hello": "greet Alice"}, add_examples_flag=False)

    @cli.subcmd
    def greet(name: str):
        pass

    with pytest.raises(SystemExit):
        cli.run(["--help"])
    out = strip_ansi(capsys.readouterr().out)
    assert "--examples" not in out
    assert "examples:" in out


def test_cli_subcommand_examples_flag_suppressed(capsys):
    cli = CLI()

    @cli.subcmd(examples={"With feeling": "greet Alice"}, add_examples_flag=False)
    def greet(name: str):
        pass

    with pytest.raises(SystemExit):
        cli.run(["greet", "--help"])
    out = strip_ansi(capsys.readouterr().out)
    assert "--examples" not in out
    assert "examples:" in out
    assert "greet Alice        # With feeling" in out
