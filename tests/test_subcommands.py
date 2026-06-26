import pytest
from defcmd import CLI

def test_dispatch_by_name():
    cli = CLI()
    calls = []

    @cli.subcmd
    def init(name: str):
        calls.append(("init", name))

    cli.run(["init", "test_project"])
    assert calls == [("init", "test_project")]

def test_dispatch_multiple_commands():
    cli = CLI()
    calls = []

    @cli.subcmd
    def init(name: str):
        calls.append(("init", name))

    @cli.subcmd
    def build(clean: bool = False):
        calls.append(("build", clean))

    cli.run(["build", "--clean"])
    assert calls == [("build", True)]

def test_unknown_subcommand_exists(monkeypatch):
    cli = CLI()

    @cli.subcmd
    def init(name: str):
        pass

    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    with pytest.raises(SystemExit):
        cli.run(["unknown_command"])
