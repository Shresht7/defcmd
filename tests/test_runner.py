from defcmd.runner import cmd, CLI
from defcmd.spec import Spec
from typing import Annotated

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
