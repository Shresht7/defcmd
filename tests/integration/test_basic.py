import pytest
from pathlib import Path
from typing import Annotated

from defcmd.runner import cmd, CLI
from defcmd.spec import Spec
from defcmd.terminal import is_ansi_enabled


class TestBasicDispatch:
    def test_full_argv_runs_without_prompting(self, monkeypatch):
        calls = []

        @cmd
        def deploy(host: str, port: int = 8080, verbose: bool = False):
            calls.append((host, port, verbose))

        monkeypatch.setattr("builtins.input", lambda *_: (_ for _ in ()).throw(AssertionError("should not prompt")))

        deploy.run(["localhost", "--port", "1234", "--verbose"])
        assert calls == [("localhost", 1234, True)]


    def test_run_with_default_argv(self, monkeypatch):
        calls = []

        @cmd
        def deploy(host: str, port: int = 8080):
            calls.append((host, port))

        monkeypatch.setattr("sys.argv", ["script.py", "localhost", "--port", "9090"])
        monkeypatch.setattr("sys.stdin.isatty", lambda: False)

        deploy.run()
        assert calls == [("localhost", 9090)]


    def test_empty_argv_in_real_terminal_runs_wizard(self, monkeypatch):
        calls = []

        @cmd
        def deploy(host: str, port: int = 8080, verbose: bool = False):
            calls.append((host, port, verbose))

        monkeypatch.setattr("sys.stdin.isatty", lambda: True)

        prompted = iter(["wizardhost", 9090, True])
        monkeypatch.setattr("defcmd.runner.prompt", lambda _param, **kw: next(prompted))

        deploy.run([])
        assert calls == [("wizardhost", 9090, True)]


class TestPromptOptional:
    def test_cmd_prompt_optional_false_skips_optional_params(self, monkeypatch):
        calls = []

        @cmd(prompt_optional=False)
        def deploy(host: str, port: int = 8080, verbose: bool = False):
            calls.append((host, port, verbose))

        monkeypatch.setattr("sys.stdin.isatty", lambda: True)
        monkeypatch.setattr("builtins.input", lambda _: "myhost")

        deploy.run([])
        assert calls == [("myhost", 8080, False)]


    def test_cmd_prompt_optional_false_with_spec_prompt_true_override(self, monkeypatch):
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


    def test_cli_subcmd_prompt_optional_false(self, monkeypatch):
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


class TestHiddenIntegration:
    def test_cli_subcmd_hidden_excluded_from_interactive(self, monkeypatch):
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


    def test_cli_subcmd_hidden_still_callable_via_argv(self, monkeypatch):
        cli = CLI()
        calls = []

        @cli.subcmd(hidden=True)
        def greet(name: str):
            calls.append(name)

        monkeypatch.setattr("sys.stdin.isatty", lambda: False)

        cli.run(["greet", "Alice"])
        assert calls == ["Alice"]


class TestVersionIntegration:
    def test_cmd_version_flag(self, monkeypatch):
        @cmd(version="1.0.0")
        def deploy(host: str):
            pass

        monkeypatch.setattr("sys.stdin.isatty", lambda: False)

        with pytest.raises(SystemExit) as exc:
            deploy.run(["--version"])
        assert exc.value.code == 0


    def test_cli_version_flag(self, monkeypatch):
        cli = CLI(version="2.0.0")

        monkeypatch.setattr("sys.stdin.isatty", lambda: False)

        with pytest.raises(SystemExit) as exc:
            cli.run(["--version"])
        assert exc.value.code == 0


class TestMisc:
    def test_cmd_with_path_arg(self, tmp_path):
        file = tmp_path / "data.txt"
        file.write_text("hello")

        @cmd
        def read_file(path: Path):
            return path.read_text()

        result = read_file.run([str(file)])
        assert result == "hello"


    def test_cmd_list_required(self):
        calls = []

        @cmd
        def collect(items: list[int]):
            calls.append(items)

        collect.run(["1", "2", "3"])
        assert calls == [[1, 2, 3]]


    def test_cmd_list_optional(self):
        calls = []

        @cmd
        def collect(items: list[int] = []):
            calls.append(items)

        collect.run(["--items", "4", "5"])
        assert calls == [[4, 5]]
