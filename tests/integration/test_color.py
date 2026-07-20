import pytest
import re

from defcmd.runner import cmd, CLI
from defcmd.terminal import is_ansi_enabled


_ansi_re = re.compile(r"\x1b\[[0-9;]*m")

def strip_ansi(text: str) -> str:
    return _ansi_re.sub("", text)


class TestColorHelpVisibility:
    def test_color_flag_shown_in_help(self, capsys):
        @cmd
        def greet(name: str):
            pass

        with pytest.raises(SystemExit):
            greet.run(["--help"])
        out = capsys.readouterr().out
        assert "--color" in out
        assert "--no-color" in out


    def test_color_flag_shown_in_cli_help(self, capsys):
        cli = CLI()

        @cli.subcmd
        def greet(name: str):
            pass

        with pytest.raises(SystemExit):
            cli.run(["--help"])
        out = capsys.readouterr().out
        assert "--color" in out
        assert "--no-color" in out


class TestColorOverride:
    def test_color_flag_overrides_non_tty(self, monkeypatch):
        monkeypatch.setattr("sys.stdout.isatty", lambda: False)

        @cmd
        def greet(name: str):
            pass

        greet.run(["--color", "Alice"])

        assert is_ansi_enabled() is True


    def test_no_color_flag_overrides_tty(self, monkeypatch):
        monkeypatch.setattr("sys.stdout.isatty", lambda: True)

        @cmd
        def greet(name: str):
            pass

        greet.run(["--no-color", "Alice"])

        assert is_ansi_enabled() is False


    def test_color_flag_works_with_cli_subcommand(self, monkeypatch):
        monkeypatch.setattr("sys.stdout.isatty", lambda: False)

        cli = CLI()
        calls = []

        @cli.subcmd
        def greet(name: str):
            calls.append(name)

        cli.run(["--color", "greet", "Alice"])

        assert is_ansi_enabled() is True
        assert calls == ["Alice"]


    def test_no_color_flag_works_with_cli_subcommand(self, monkeypatch):
        monkeypatch.setattr("sys.stdout.isatty", lambda: True)

        cli = CLI()
        calls = []

        @cli.subcmd
        def greet(name: str):
            calls.append(name)

        cli.run(["--no-color", "greet", "Alice"])

        assert is_ansi_enabled() is False
        assert calls == ["Alice"]


class TestColorSuppression:
    def test_color_flag_suppressed_on_cmd(self, capsys):
        @cmd(add_color_flag=False)
        def greet(name: str):
            pass

        with pytest.raises(SystemExit):
            greet.run(["--help"])
        out = strip_ansi(capsys.readouterr().out)
        assert "--color" not in out
        assert "--no-color" not in out


    def test_color_flag_suppressed_on_cli(self, capsys):
        cli = CLI(add_color_flag=False)

        @cli.subcmd
        def greet(name: str):
            pass

        with pytest.raises(SystemExit):
            cli.run(["--help"])
        out = strip_ansi(capsys.readouterr().out)
        assert "--color" not in out
        assert "--no-color" not in out


    def test_color_flag_suppressed_on_subcmd(self, capsys):
        cli = CLI()

        @cli.subcmd(add_color_flag=False)
        def greet(name: str):
            pass

        with pytest.raises(SystemExit):
            cli.run(["greet", "--help"])
        out = strip_ansi(capsys.readouterr().out)
        assert "--color" not in out
        assert "--no-color" not in out
